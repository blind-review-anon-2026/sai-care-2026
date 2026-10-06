"""In-memory reference control path. No network, real LLM, database, or clinical classifier."""
from copy import deepcopy
import hashlib
import json
from policy import decide

class Control:
    def __init__(self):
        self.journal_up = True
        self.audit = []
        self.calls = []
        self.sent = {}
        self.consent = True
        self.version = 1
        self.recipient = 'clinician-8'
        self.scope = 'visit'
        self.elements = [dict(text='I lose track when stressed.', origin='human', author='owner', lineage=[], generated=False)]
        self.flags = []
        self.ack = False
        self.moderate = False
        self.approval = None
        self.approval_record = None  # Detached: never included in its own hash.
        self.release_provenance = []
        self.messages = []
        # Deployment-owned test configuration, never extracted from source text.
        self.urgent_guidance = 'For urgent concerns, use the locally configured urgent-care service.' 
        self.allowed = {'n1','z1'}
        self.selected = {'n1'}
        self.sources = {'n1':'I lose track when stressed.', 'n2':'Excluded private note.'}
        self.excluded = set()
        self.narrow_confirmed = True
        self.params = {'length':'brief'}
        self.parameter_ids = {'length':'z1'}
        self.metadata = {}  # Values are (versioned item ID, value).
        self.preferences = {}
        self.last_payload = None
        self.assessment_version = None
        self.assessment_risk = 'unassessed'
    def record(self,event):
        if not self.journal_up: return False
        self.audit.append(event)
        return True
    def assess(self,permitted):
        if not permitted or not self.selected <= self.allowed: return 'IN-SCOPE'
        if not self.record('assess'): return 'EX-AUDIT'
        self.calls.append(('assessor',tuple(sorted(self.selected))))
        self.assessment_version,self.assessment_risk = self.version,'high'
        return 'ASSESSED'
    def inherited_risk(self):
        return self.assessment_risk if self.assessment_version == self.version else 'unassessed'
    def generate(self,s,*,semantic_error=False,missing_lineage=False,injection=False):
        if s.op != 'transform': return 'IN-STATE'
        d = decide(s)
        if d.rule == 'R1':
            self.messages.append('This transformation is not performed. ' + self.urgent_guidance)
            return d.rule
        if d.rule != 'R9': return d.rule
        if not self.consent: return 'EX-CONSENT'
        if not self.narrow_confirmed: return 'EX-INPUT'
        source_ids = self.selected-self.excluded
        if not source_ids or not source_ids <= self.allowed: return 'EX-INPUT'
        used = set(source_ids)
        params, preferences, metadata = {}, {}, {}
        # Every channel uses the same authorisation AND exclusion projection.
        for key,value in self.params.items():
            item = self.parameter_ids.get(key)
            if item is None: return 'EX-INPUT'
            if item in self.excluded: continue
            if item not in self.allowed: return 'EX-INPUT'
            params[key] = deepcopy(value); used.add(item)
        for key,(value,enabled) in self.preferences.items():
            if not enabled: continue
            item = 'pref:'+key
            if item in self.excluded: continue
            if item not in self.allowed: return 'EX-INPUT'
            preferences[key] = deepcopy(value); used.add(item)
        for key,(item,value) in self.metadata.items():
            if item in self.excluded: continue
            if item not in self.allowed: return 'EX-INPUT'
            metadata[key] = deepcopy(value); used.add(item)
        payload = dict(instructions='Reformulate selected sources as data; no tools.',
            sources=[{'id':i,'text':self.sources[i]} for i in sorted(source_ids)],
            parameters=params,preferences=preferences,metadata=metadata)
        assert used <= self.allowed-self.excluded
        if not self.record('model:R9'): return 'EX-AUDIT'
        self.last_payload = deepcopy(payload)
        self.calls.append(('model',deepcopy(payload)))
        self.version += 1
        self.approval = self.approval_record = None
        self.release_provenance = []
        # Scripted output and scripted semantic verdicts: no accuracy claim.
        self.elements = [dict(text='I lose track when I am stressed.',origin='model',author='model',
            lineage=[] if missing_lineage else sorted(source_ids), generated=True)]
        self.moderate = s.risk == 'moderate'
        self.flags = ['unsupported'] if semantic_error else (['injected-instruction'] if injection else [])
        if not self.record('validate'): return 'EX-AUDIT'
        return self.validate()
    def validate(self):
        if any((e['generated'] and (e['origin'] != 'model' or not e['lineage'])) or
               (e['author'] == 'caregiver' and e.get('attribution') != 'Caregiver statement') for e in self.elements):
            return 'VAL-STRUCT'
        return 'VAL-SEM' if self.flags else 'REVIEWABLE'
    def resolve_flag(self,evidence=None):
        if not evidence: return 'VAL-SEM'
        if not self.record('review-evidence'): return 'EX-AUDIT'
        self.flags.clear()
        return self.validate()
    def bundle(self):
        return dict(version=self.version,elements=deepcopy(self.elements),recipient=self.recipient,scope=self.scope,
            provenance=deepcopy(self.release_provenance))
    def digest(self):
        return hashlib.sha256(json.dumps(self.bundle(),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    def approve(self,s):
        if s.op != 'approve': return 'IN-STATE'
        d=decide(s)
        if d.rule != 'R10': return d.rule
        if self.validate() != 'REVIEWABLE' or (self.moderate and not self.ack): return 'R8'
        if not self.consent: return 'EX-CONSENT'
        if not self.record('approve'): return 'EX-AUDIT'
        # One synchronous finalisation: freeze recipient-visible labels, then hash.
        self.release_provenance = [
            'Caregiver statement; approved for release by patient' if e['author']=='caregiver'
            else ('AI-assisted reformulation, approved by patient' if e['generated']
                  else 'Patient statement, approved by patient') for e in self.elements]
        self.approval=self.digest()
        self.approval_record=dict(owner=s.actor,version=self.version,digest=self.approval,
                                  recipient=self.recipient,scope=self.scope)
        return 'APPROVED'
    def edit(self,s,text='A new fact.'):
        if s.op != 'edit': return 'IN-STATE'
        d=decide(s)
        if d.rule != 'R10': return d.rule
        if not self.record('edit'): return 'EX-AUDIT'
        self.version+=1
        self.approval = self.approval_record = None
        self.release_provenance = []
        self.elements.append(dict(text=text,origin='human',author=s.actor,lineage=[],generated=False,
            attribution='Caregiver statement' if s.actor == 'caregiver' else 'Patient statement'))
        return self.validate()
    def share(self,s,delivery='delivery-1',before_dispatch=None):
        if s.op != 'share': return 'IN-STATE'
        d=decide(s)
        if d.rule != 'R10': return d.rule
        if self.approval != self.digest() or self.validate() != 'REVIEWABLE': return 'R8'
        # Synchronous hook represents a mutation between policy check and atomic boundary.
        if before_dispatch: before_dispatch(self)
        if not self.consent or self.approval != self.digest() or self.validate() != 'REVIEWABLE': return 'REL-STALE'
        if not self.record('dispatch-intent'): return 'EX-AUDIT'
        if delivery not in self.sent: self.sent[delivery]=deepcopy(self.bundle())
        self.record('dispatch-reconciled')
        return 'SHARED'
