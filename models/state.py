import time

import jimi

class _state(jimi.db._document):
    name = str()
    newState = dict()
    currentState = dict()
    stateHoldExpiry = int()
    defaultState = dict()

    _dbCollection = jimi.db.db["state"]

    def new(self,acl,name,newState,defaultState,holdTime):
        self.acl = acl
        self.name = name
        self.newState = newState
        self.defaultState = defaultState
        self.stateHoldExpiry = time.time() + holdTime
        return super(_state, self).new()

    
