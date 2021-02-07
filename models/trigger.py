import jimi

from plugins.state.models import state

class _stateChange(jimi.trigger._trigger):
    stateName = str()
    lastStateValueSeen = dict()

    def check(self):
        stateObject = state._state().getAsClass(query={ "name" : self.stateName, "newState" : { "$ne" : self.lastStateValueSeen } })
        if len(stateObject) > 0:
            stateObject = stateObject[0]
            self.lastStateValueSeen = stateObject.newState
            self.update(["lastStateValueSeen"])
            self.result["events"] = [stateObject.newState]
