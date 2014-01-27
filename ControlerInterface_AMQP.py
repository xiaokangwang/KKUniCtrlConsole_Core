#!/usr/bin/env python3
import uuid
"""ControlerInterface:AMQP Progresser"""

WorkMode={
'WorkNode', #Accetpt Control
'ControlConsole' #Connect to Server Accept Control
}

class ControlerInterface_AMQP(object):
	"""The AQMP Controler interface Instance"""
	InstConf={}
	Runtimevar={}
	CtrlerRuntime={}
	def __init__(self):
		super(ControlerInterface_AMQP, self).__init__()
		
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

        self.InstConf['AQMP_URL']=''
        self.InstConf['AQMP_Channel']=''
        self.InstConf['AQMP_Exange']=''

        if Mode == "WorkNode":
        	pass
            
        if Mode == "ControlConsole":
        	pass


    def ExportConfig(self):
        return self.InstConf

    def InitRuntime(self,CtrlerRuntime):
        self.Runtimevar['uuid']=str(uuid.uuid4())
        self.CtrlerRuntime=CtrlerRuntime

    

