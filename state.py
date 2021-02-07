import uuid

import jimi

from plugins.state.models import action as stateAction

class _state(jimi.plugin._plugin):
    version = 0.2

    def install(self):
        # Register models
        jimi.model.registerModel("state","_state","_document","plugins.state.models.state")
        jimi.model.registerModel("stateSet","_stateSet","_action","plugins.state.models.action")
        jimi.model.registerModel("stateGet","_stateGet","_action","plugins.state.models.action")
        jimi.model.registerModel("stateProcess","_stateProcess","_action","plugins.state.models.action",hidden=True)
        jimi.model.registerModel("stateChange","_stateChange","_trigger","plugins.state.models.trigger")

        c = jimi.conduct._conduct().new("stateCore")
        c = jimi.conduct._conduct().getAsClass(id=c.inserted_id)[0]
        t = jimi.trigger._trigger().new("stateCore")
        t = jimi.trigger._trigger().getAsClass(id=t.inserted_id)[0]
        a = stateAction._stateProcess().new("stateCore")
        a = stateAction._stateProcess().getAsClass(id=a.inserted_id)[0]
       
        c.triggers = [t._id]
        flowTriggerID = str(uuid.uuid4())
        flowActionID = str(uuid.uuid4())
        c.flow = [
            {
                "flowID" : flowTriggerID,
                "type" : "trigger",
                "triggerID" : t._id,
                "next" : [
                    {"flowID": flowActionID, "logic": True }
                ]
            },
            {
                "flowID" : flowActionID,
                "type" : "action",
                "actionID" : a._id,
                "next" : []
            }
        ]
        jimi.webui._modelUI().new(c._id,{ "ids":[ { "accessID":"0","delete": True,"read": True,"write": True } ] },flowTriggerID,0,0,"")
        jimi.webui._modelUI().new(c._id,{ "ids":[ { "accessID":"0","delete": True,"read": True,"write": True } ] },flowActionID,150,50,"")
        c.acl = { "ids":[ { "accessID":"0","delete": True,"read": True,"write": True } ] }
        c.enabled = True
        c.update(["triggers","flow","enabled","acl"])
        t.acl = { "ids":[ { "accessID":"0","delete": True,"read": True,"write": True } ] }
        t.schedule = "15-30s"
        t.enabled = True
        t.update(["schedule","enabled","acl"])
        a.acl = { "ids":[ { "accessID":"0","delete": True,"read": True,"write": True } ] }
        a.enabled = True
        a.update(["enabled","acl"])
        return True

    def uninstall(self):
        # deregister models
        jimi.model.deregisterModel("state","_state","_document","plugins.state.models.state")
        jimi.model.deregisterModel("stateSet","_stateSet","_action","plugins.state.models.action")
        jimi.model.deregisterModel("stateGet","_stateGet","_action","plugins.state.models.action")
        jimi.model.deregisterModel("stateProcess","_stateProcess","_action","plugins.state.models.action")
        jimi.model.deregisterModel("stateChange","_stateChange","_trigger","plugins.state.models.trigger")


        jimi.conduct._conduct().api_delete(query={"name" : "stateCore"  })
        jimi.trigger._trigger().api_delete(query={"name" : "stateCore"  })
        stateAction._stateProcess().api_delete(query={"name" : "stateCore"  })
        return True

    def upgrade(self,LatestPluginVersion):
        if self.version < 0.2:
            jimi.model.registerModel("stateChange","_stateChange","_trigger","plugins.state.models.trigger")
        return True
