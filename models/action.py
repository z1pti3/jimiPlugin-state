import hashlib
import time
import re

import jimi

from plugins.state.models import state

class _stateSet(jimi.action._action):
    stateName = str()
    stateValue = dict()
    defaultStateValue = dict()
    stateholdTime = int()

    def __init__(self):
        jimi.cache.globalCache.newCache("stateCache")

    def run(self,data,persistentData,actionResult):
        stateName = jimi.helpers.evalString(self.stateName,{"data" : data})
        stateValue = jimi.helpers.evalDict(self.stateValue,{"data" : data})
        defaultStateValue = jimi.helpers.evalDict(self.defaultStateValue,{"data" : data})
        
        stateObject = jimi.cache.globalCache.get("stateCache",stateName,getStateObject,customCacheTime=self.stateholdTime)
        if stateObject:
            if len(stateObject) > 1:
                for x in range(1,len(stateObject)-1):
                    stateObject[x].delete()
            stateObject = stateObject[0]
            if stateObject.defaultState != defaultStateValue:
                stateObject.defaultState = defaultStateValue
                stateObject.update(["defaultStateValue"])
            if stateObject.newState != stateValue:
                stateObject.currentState = stateObject.newState
                stateObject.newState = stateValue
                stateObject.stateHoldExpiry = time.time() + self.stateholdTime
                stateObject.update(["newState","data","stateHoldExpiry"])
            elif stateObject.stateHoldExpiry < time.time() + (self.stateholdTime / 2):
                stateObject.stateHoldExpiry = time.time() + self.stateholdTime
                stateObject.update(["stateHoldExpiry"])
            actionResult["result"] = True
            actionResult["rc"] = 302
            return actionResult
        else:
            stateId = state._state().new(self.acl,stateName,stateValue,defaultStateValue,self.stateholdTime).inserted_id
            actionResult["result"] = True
            actionResult["stateObjectId"] = stateId
            actionResult["rc"] = 201
            return actionResult

class _stateGet(jimi.action._action):
    stateName = str()

    def run(self,data,persistentData,actionResult):
        stateName = jimi.helpers.evalString(self.stateName,{"data" : data})
        stateObject = state._state().getAsClass(query={ "name" : stateName })
        if len(stateObject) > 0:
            stateObject = stateObject[0]
            actionResult["result"] = True
            actionResult["stateObject"] = jimi.helpers.classToJson(stateObject,hidden=True)
            actionResult["rc"] = 0
            return actionResult
        actionResult["result"] = True
        actionResult["msg"] = "stateObject not found"
        actionResult["rc"] = 404
        return actionResult
            
class _stateProcess(jimi.action._action):

    def run(self,data,persistentData,actionResult):
        stateObjects = state._state().getAsClass(query={ "$and" : [ {"stateHoldExpiry" : { "$lt" : time.time() }}, {"stateHoldExpiry" : { "$ne" : 0 }} ] })
        for stateObject in stateObjects:
            stateObject.currentState = stateObject.newState
            stateObject.newState = stateObject.defaultState
            stateObject.stateHoldExpiry = 0
            stateObject.update(["newState","currentState","stateHoldExpiry"])
        actionResult["result"] = True
        actionResult["rc"] = 0
        return actionResult

def getStateObject(stateName,sessionData):
    return state._state().getAsClass(query={ "name" : stateName })
