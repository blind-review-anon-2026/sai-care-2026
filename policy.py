"""Finite policy abstraction; predicates are supplied, not inferred from prose."""
from dataclasses import dataclass
from itertools import product

@dataclass(frozen=True)
class State:
    actor: str = 'owner'
    op: str = 'transform'
    phase: str = 'execute'
    task: str = 'TR1'
    risk: str = 'low'
    status: str = 'resolved'
    prohibited: bool = False
    scope: bool = True
    preconditions: bool = True
    route: bool = True

@dataclass(frozen=True)
class Decision:
    rule: str
    mode: str
    resolver: str
    obligations: tuple

def valid(s):
    return (s.actor in ('owner','caregiver','model','professional')
        and s.op in ('transform','edit','approve','share')
        and s.phase in ('initiate','execute')
        and s.task in tuple('TR'+str(i) for i in range(1,10))+('unknown','NA')
        and s.risk in ('low','moderate','high','unassessed')
        and s.status in ('resolved','uncertain')
        and ((s.task == 'NA') == (s.op != 'transform'))
        and (s.task != 'unknown' or s.status == 'uncertain')
        and (s.op == 'transform' or s.status == 'resolved')
        and (s.op != 'transform' or s.risk != 'unassessed' or s.status == 'uncertain')
        and (s.actor != 'owner' or s.phase == 'execute'))

def role_allowed(s):
    if s.actor == 'owner': return True
    return s.actor == 'caregiver' and (s.op == 'edit' or
        (s.op in ('transform','share') and s.phase == 'initiate'))

def decide(s):
    if not valid(s): raise ValueError('IN-STATE')
    if s.op == 'transform' and (s.risk == 'high' or s.task in ('TR8','TR9')):
        return Decision('R1','ESCALATE' if s.route else 'REFUSE',
                        'professional-route' if s.route else 'none',('fixed-message',))
    if not role_allowed(s): j = 'R2'
    elif s.prohibited: j = 'R3'
    elif not s.scope: j = 'R4'
    elif s.op == 'transform' and s.status == 'uncertain': j = 'R5'
    elif s.phase == 'initiate' and s.actor != 'owner': j = 'R6'
    elif s.task == 'TR7': j = 'R7'
    elif not s.preconditions: j = 'R8'
    elif s.op == 'transform' and s.task in tuple('TR'+str(i) for i in range(1,7)): j = 'R9'
    elif s.op in ('edit','approve','share'): j = 'R10'
    else: j = 'R11'
    if j in ('R2','R3','R11'): return Decision(j,'REFUSE','none',('fixed-message',))
    asks = dict(R4='resolve-scope',R5='clarify-task',R6='confirm-operation',R7='narrow-task',R8='satisfy-preconditions')
    if j in asks: return Decision(j,'ASK','owner',(asks[j],))
    if j == 'R9': return Decision(j,'CONSTRAINED','owner',('source-validation','owner-review') + (('comparison-ack',) if s.risk == 'moderate' else ()))
    return Decision(j,'ALLOW','none',('operation-gates',)+(('fixed-notice',) if s.risk == 'high' else ()))

def states():
    for values in product(('owner','caregiver','model','professional'),
            ('transform','edit','approve','share'),('initiate','execute'),
            tuple('TR'+str(i) for i in range(1,10))+('unknown','NA'),
            ('low','moderate','high','unassessed'),('resolved','uncertain'),
            (False,True),(False,True),(False,True),(False,True)):
        s = State(*values)
        if valid(s): yield s
