#!/usr/bin/env python3
import uuid
import pika
import threading
import json
import time
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
        self.Runtimevar['Callbacks']={}

    def connect():
        connection = pika.BlockingConnection(pika.URLParameters(self.InstConf['AQMP_URL']))
        Runtimevar['AQMP_connection']=connection
        channel = connection.channel(InstConf['AQMP_Channel'])
        Runtimevar['AQMP_channel']=channel
        channel.exchange_declare(exchange=InstConf['AQMP_Exange'],type='fanout')

    def WorkNode_register():
        channel=Runtimevar['AQMP_channel']
        ListeningQueue = channel.queue_declare(exclusive=True)
        ListeningQueue_name = ListeningQueue.method.queue
        Runtimevar['ListeningQueue']=ListeningQueue
        channel.queue_bind(exchange=InstConf['AQMP_Exange'],queue=ListeningQueue_name)

    def WorkNode_makePingResp(Rinterface_uuid):
        PingResp={}
        PingResp["Rinterface_uuid"]=Rinterface_uuid
        PingResp["Linterface_uuid"]=Runtimevar['uuid']
        PingResp["Act"]="PingResp"
        

    def WorkNode_makeCtrlResp(Req):
        CtrlResp={}
        CtrlResp["Rinterface_uuid"]=Rinterface_uuid
        CtrlResp["Linterface_uuid"]=Runtimevar['uuid']
        

    
    def WorkNode_wait_onmessage(ch, method, properties, body):
        try:
            Req=json.loads(body)
            channel=Runtimevar['AQMP_channel']
            if Req['Act']=="ping":
                channel.basic_publish(exchange='',
                    routing_key=Req['CtrlInterface_ListeningQueue'],
                    body=json.dumps(WorkNode_makePingResp(Req['CtrlInterface_uuid'])))
            if Req['Act']=="Ctrl":
                channel.basic_publish(exchange='',
                    routing_key=Req['CtrlInterface_ListeningQueue'],
                    body=json.dumps(WorkNode_makeCtrlResp(Req)))
                pass
        except Exception, e:
            pass
        else:
            pass
        finally:
            pass

    def WorkNode_wait():
        channel=Runtimevar['AQMP_channel']
        ListeningQueue_name = Runtimevar['ListeningQueue'].method.queue
        channel.basic_consume(WorkNode_wait_onmessage,queue=ListeningQueue_name,no_ack=True)
        channel.start_consuming()

    def WorkNode_startwait():
        wait_thread=threading.Thread(target=WorkNode_wait,daemon=True)
        wait_thread.start()


    def ControlConsole_makeCtrlRequest():
        CtrlReq={}
        #UUIDs
        CtrlReq['CtrlerInst_uuid']=CtrlerRuntime['uuid']
        CtrlReq['CtrlInterface_uuid']=Runtimevar['uuid']
        #Listener
        CtrlReq['CtrlInterface_ListeningQueue']=Runtimevar['ListeningQueue'].method.queue
        CtrlReq['Act']="Ctrl"
        CtrlReqJSON=json.dumps(CtrlReq)

    def ControlConsole_makePingRequest():
        CtrlReq={}
        #UUIDs
        CtrlReq['CtrlerInst_uuid']=CtrlerRuntime['uuid']
        CtrlReq['CtrlInterface_uuid']=Runtimevar['uuid']
        #Listener
        CtrlReq['CtrlInterface_ListeningQueue']=Runtimevar['ListeningQueue'].method.queue
        CtrlReq['Act']="Ping"
        CtrlReqJSON=json.dumps(CtrlReq)


    def ControlConsole_broadcastCtrlRequest():
        CtrlReqJSON=ControlConsole_makeCtrlRequest()
        channel=Runtimevar['AQMP_channel']
        channel.basic_publish(exchange=InstConf['AQMP_Exange'],body=CtrlReqJSON)

    def ControlConsole_broadcastPingRequest():
        PingReqJSON=ControlConsole_makePingRequest()
        channel=Runtimevar['AQMP_channel']
        channel.basic_publish(exchange=InstConf['AQMP_Exange'],body=PingReqJSON)



    def ControlConsole_register():
        channel=Runtimevar['AQMP_channel']
        ListeningQueue = channel.queue_declare(exclusive=True)

    def ControlConsole_wait_onmessage(ch, method, properties, body):
        try:
            pass
        except Exception, e:
            pass
        else:
            pass

    def ControlConsole_wait():
        channel=Runtimevar['AQMP_channel']
        ListeningQueue_name = Runtimevar['ListeningQueue'].method.queue
        channel.basic_consume(ControlConsole_wait_onmessage,queue=ListeningQueue_name,no_ack=True)
        channel.start_consuming()

    def ControlConsole_startwait():
        wait_thread=threading.Thread(target=ControlConsole_wait,daemon=True)
        wait_thread.start()





