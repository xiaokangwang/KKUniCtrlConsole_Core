#!/usr/bin/env python3
import uuid

WorkMode={
'WorkNode', #Accetpt Control
'ControlConsole' #Connect to Server Accept Control
}

class KKUniCtrlConsole_CtrlerInst(object):
    """The Control Instance of KKUniCtrlConsole."""

    InstConf={}
    Runtimevar={}
    def __init__(self):
        super(KKUniCtrlConsole_CtrlerInst, self).__init__()

    def SetConfig(self,key,val):
        self.InstConf[key]=val

    def GetConfig(self,key):
        if key in self.InstConf:
            return self.InstConf[key]
        else:
            raise Exception("Not exist.")

    def LoadConfig(self,confDict):
        self.InstConf.update(confDict)

    def InitConfig(self,Mode):
        
        if Mode in WorkMode:

            self.InstConf={
            "Mode"=Mode
            }

        if Mode == "WorkNode":
            self.InstConf['CtrleeProject']={}
            self.InstConf['CtrleeInstance']={}
            self.InstConf['Controlers']=[]
            self.InstConf['ControlerInterface']=[]

        if Mode == "ControlConsole":
            self.InstConf['CtrleeProjects']=[]
            self.InstConf['Controler']={}

    def ExportConfig(self):
        return self.InstConf

    def InitRuntime(self):
        self.Runtimevar['uuid']=str(uuid.uuid4())

