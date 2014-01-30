#!/usr/bin/env python3
import uuid
import pika
import threading
import json
import time
import os
import kecsl
import base64
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
            "Mode":Mode
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
        self.Runtimevar['ctrlqueues']={}
        self.Runtimevar['Connectedqueue']={}
        

    def connect(self):
        self.connection = pika.BlockingConnection(pika.URLParameters(self.InstConf['AQMP_URL']))
        self.Runtimevar['AQMP_connection']=connection
        channel = connection.channel(self.InstConf['AQMP_Channel'])
        self.Runtimevar['AQMP_channel']=channel
        channel.exchange_declare(exchange=self.InstConf['AQMP_Exange'],type='fanout')

    def WorkNode_register(self):
        channel=self.Runtimevar['AQMP_channel']
        ListeningQueue = channel.queue_declare(exclusive=True)
        ListeningQueue_name = ListeningQueue.method.queue
        self.Runtimevar['ListeningQueue']=ListeningQueue
        channel.queue_bind(exchange=self.InstConf['AQMP_Exange'],queue=ListeningQueue_name)

    def WorkNode_makePingResp(self,Rinterface_uuid):
        PingResp={}
        PingResp["Rinterface_uuid"]=Rinterface_uuid
        PingResp["Linterface_uuid"]=Runtimevar['uuid']
        PingResp["Act"]="PingResp"
        return PingResp

    def WorkNode_createkecsl(self):
        thekecsl=kecsl.KKUniCtrlConsole_KECSLInst()
        thekecsl.LoadConfig(self.Runtimevar['callback_KECSLconfig'](self.Runtimevar['uuid']))
        thekecsl.InitRuntime()
        thekecsl.SetEcckeyCallback(self.Runtimevar['callback_GetEccPukByID'])
        thekecsl.SetPasswsCallback(self.Runtimevar['callback_GetPasswdHashByID'])
        return thekecsl


    def WorkNode_Onencmessage(self,ch, method, properties, body):
        purpose,payload=self.ALL_Unwrapencdata(body)
        if purpose=='StartConn':
            conn=self.Runtimevar['ctrlqueues'][properties.reply_to]
            reply=conn['kecslobj'].OnRecvConnectReq(payload)
            replyW=ALL_Wrapencdata(reply,"StartConnRep")
            channel=self.Runtimevar['AQMP_channel']
            channel.basic_publish(routing_key=properties.reply_to,body=replyW)


        if purpose=='AuthP':
            conn=self.Runtimevar['ctrlqueues'][properties.reply_to]
            authto,reply=conn['kecslobj'].OnReceiveAuth(payload)
            conn['authed']=authto
            replyW=ALL_Wrapencdata(reply,"AuthPR")
            channel=self.Runtimevar['AQMP_channel']
            channel.basic_publish(routing_key=properties.reply_to,body=replyW)

        if purpose=='Data':
            conn=self.Runtimevar['ctrlqueues'][properties.reply_to]
            progressneed,recvdata=conn['kecslobj'].OnReceive(payload)
            conn['lastrecv']=time.time()
            if progressneed:
                self.Runtimevar['callback_Onreceive'](recvdata,conn['Rinterface_uuid'],conn['authed'])
                    

    def WorkNode_waitonenc(self,listenfor):
        self.Runtimevar['AQMP_channel'].basic_consume(self.WorkNode_Onencmessage, no_ack=True,queue=listenfor)

    def All_SendData(self,Rinterface_uuid,content):
        for key in self.Runtimevar['ctrlqueues'].keys():
            conn=self.Runtimevar['ctrlqueues'][key]
            if conn['Rinterface_uuid']==Rinterface_uuid:
                datatosend=conn['kecslobj'].Send(content)
                datatosendW=self.ALL_Wrapencdata(datatosend,'Data')
                channel=self.Runtimevar['AQMP_channel']
                channel.basic_publish(routing_key=conn['name'],body=datatosendW)



        



    def WorkNode_makeCtrlConn(self,Req):
        ctrlqueue=self.Runtimevar['AQMP_channel'].queue_declare(exclusive=True)
        ctrlqueuename = ctrlqueue.method.queue
        ctrlqueuex={}
        ctrlqueuex['name']=ctrlqueuename
        ctrlqueuex['ListeningQueue']=Req['CtrlInterface_ListeningQueue']
        ctrlqueuex['kecslobj']=WorkNode_createkecsl()
        ctrlqueuex['queueobj']=ctrlqueue
        self.Runtimevar['ctrlqueues'][Req['CtrlInterface_ListeningQueue']]=ctrlqueuex
        wait_thread=threading.Thread(target=self.WorkNode_waitonenc,args=(ctrlqueue),daemon=True)
        wait_thread.start()


        return ctrlqueuename

        

    def WorkNode_makeCtrlResp(self,Req):
        CtrlResp={}
        CtrlResp['Act']='CtrlResp'
        CtrlResp["Rinterface_uuid"]=Req['CtrlInterface_uuid']
        CtrlResp["Linterface_uuid"]=Runtimevar['uuid']
        self.Runtimevar['ctrlqueues'][Req["Node_ListeningQueue"]]={}
        self.Runtimevar['ctrlqueues'][Req["Rinterface_uuid"]]=Req['CtrlInterface_uuid']
        queuectrlname=WorkNode_makeCtrlConn(Req)
        CtrlResp["Node_ListeningQueue"]=queuectrlname
        return CtrlResp
        

    
    def WorkNode_wait_onmessage(self,ch, method, properties, body):
        try:
            Req=json.loads(body)
            channel=self.Runtimevar['AQMP_channel']
            if Req['Act']=="ping":
                channel.basic_publish(exchange='',
                    routing_key=Req['CtrlInterface_ListeningQueue'],
                    body=json.dumps(WorkNode_makePingResp(Req['CtrlInterface_uuid'])))
            if Req['Act']=="Ctrl":
                channel.basic_publish(exchange='',
                    routing_key=Req['CtrlInterface_ListeningQueue'],
                    body=json.dumps(WorkNode_makeCtrlResp(Req)))
                pass
        except Exception as e:
            raise e
        else:
            pass
        finally:
            pass

    def WorkNode_wait(self):
        channel=self.Runtimevar['AQMP_channel']
        ListeningQueue_name = self.Runtimevar['ListeningQueue'].method.queue
        channel.basic_consume(WorkNode_wait_onmessage,queue=ListeningQueue_name,no_ack=True)
        channel.start_consuming()

    def WorkNode_startwait(self):
        wait_thread=threading.Thread(target=WorkNode_wait,daemon=True)
        wait_thread.start()


    def ControlConsole_makeCtrlRequest(self):
        CtrlReq={}
        #UUIDs
        CtrlReq['CtrlerInst_uuid']=CtrlerRuntime['uuid']
        CtrlReq['CtrlInterface_uuid']=self.Runtimevar['uuid']
        #Listener
        CtrlReq['CtrlInterface_ListeningQueue']=self.Runtimevar['ListeningQueue'].method.queue
        CtrlReq['Act']="Ctrl"
        CtrlReqJSON=json.dumps(CtrlReq)
        return CtrlReqJSON

    def ControlConsole_makePingRequest(self):
        CtrlReq={}
        #UUIDs
        CtrlReq['CtrlerInst_uuid']=CtrlerRuntime['uuid']
        CtrlReq['CtrlInterface_uuid']=self.Runtimevar['uuid']
        #Listener
        CtrlReq['CtrlInterface_ListeningQueue']=self.Runtimevar['ListeningQueue'].method.queue
        CtrlReq['Act']="Ping"
        CtrlReqJSON=json.dumps(CtrlReq)
        return CtrlReqJSON


    def ControlConsole_broadcastCtrlRequest(self):
        CtrlReqJSON=ControlConsole_makeCtrlRequest()
        channel=self.Runtimevar['AQMP_channel']
        channel.basic_publish(exchange=self.InstConf['AQMP_Exange'],body=CtrlReqJSON)

    def ControlConsole_broadcastPingRequest(self):
        PingReqJSON=ControlConsole_makePingRequest()
        channel=self.Runtimevar['AQMP_channel']
        channel.basic_publish(exchange=self.InstConf['AQMP_Exange'],body=PingReqJSON)

    def ControlConsole_StartEnc(self,comingarg):
        thekecsl=kecsl.KKUniCtrlConsole_KECSLInst()
        thekecsl.LoadConfig(self.Runtimevar['callback_KECSLconfig'](self.Runtimevar['uuid']))
        thekecsl.GenKECSLkey()
        thekecsl.InitRuntime()
        connectreq=thekecsl.Connect()
        self.Runtimevar['Connectedqueue'][comingarg['Node_ListeningQueue']]['name']=comingarg['Node_ListeningQueue']
        self.Runtimevar['Connectedqueue'][comingarg['Node_ListeningQueue']]['thekecsl']=thekecsl
        self.Runtimevar['Connectedqueue'][comingarg['Node_ListeningQueue']]['Rinterface_uuid']=comingarg["Linterface_uuid"]

        return connectreq

    def ALL_Wrapencdata(self,encb,Act):
        encbstr=base64.b64encode(encb).decode('utf8')
        wraped={}
        wraped['Act']=Act
        wraped['payload']=encbstr
        wrapedJSON=json.dumps(wraped)
        return wrapedJSON

    def ALL_Unwrapencdata(self,wrapedJSON):
        wraped=json.loads(wrapedJSON)
        purpose=wraped['Act']
        encbstr=wraped['payload']
        enco=base64.b64decode(encbstr.encode('utf8'))

        return purpose,enco

    def ControlConsole_register(self):
        channel=self.Runtimevar['AQMP_channel']
        ListeningQueue = channel.queue_declare(exclusive=True)

    def ControlConsole_wait_onmessage(self,ch, method, properties, body):
        try:
            comingarg=json.loads(body)
            if comingarg['Act']=='PingResp':
                self.Runtimevar['callback_onPingResp'](comingarg)

            if comingarg['Act']=='CtrlResp':
                startencreq=ControlConsole_StartEnc(comingarg)
                startencreqW=self.ALL_Wrapencdata(startencreq,"StartConn")
                channel=self.Runtimevar['AQMP_channel']
                channel.basic_publish(routing_key=self.Runtimevar['Connectedqueue'][comingarg['Node_ListeningQueue']],body=startencreqW)

            if comingarg['Act']=='StartConnRep':
                data=self.ALL_Unwrapencdata(body)
                result=self.Runtimevar['Connectedqueue'][properties.reply_to]['thekecsl'].OnReceiveConnectionReply(data['payload'])
                if result:
                    self.Runtimevar['Connectedqueue'][properties.reply_to]['status']='Conn'
                    self.Runtimevar['callback_OnConnected'](self.Runtimevar['Connectedqueue'][properties.reply_to]['Rinterface_uuid'])
                else:
                    self.Runtimevar['Connectedqueue'][properties.reply_to]=None

            if comingarg['Act']=='AuthPR':
                data=self.ALL_Unwrapencdata(body)
                result=self.Runtimevar['Connectedqueue'][properties.reply_to]['thekecsl'].OnReceiveAuthReply(data['payload'])
                if result:
                    self.Runtimevar['Connectedqueue'][properties.reply_to]['authed']='Yes'
                    self.Runtimevar['callback_OnAuthed'](self.Runtimevar['Connectedqueue'][properties.reply_to]['Rinterface_uuid'])
                else:
                    self.Runtimevar['Connectedqueue'][properties.reply_to]=None

            if comingarg['Act']='Data':
                data=self.ALL_Unwrapencdata(body)
                progressneed,recvdata=self.Runtimevar['Connectedqueue'][properties.reply_to]['thekecsl'].OnReceive(data['payload'])
                conn['lastrecv']=time.time()
                if progressneed:
                    self.Runtimevar['callback_Onreceive'](recvdata,self.Runtimevar['Connectedqueue'][properties.reply_to]['Rinterface_uuid'])
                else:
                
        except Exception as e:
            raise e
        else:
            pass

    def ControlConsole_wait(self):
        channel=Runtimevar['AQMP_channel']
        ListeningQueue_name = Runtimevar['ListeningQueue'].method.queue
        channel.basic_consume(ControlConsole_wait_onmessage,queue=ListeningQueue_name,no_ack=True)
        channel.start_consuming()

    def ControlConsole_startwait(self):
        wait_thread=threading.Thread(target=ControlConsole_wait,daemon=True)
        wait_thread.start()



    def ControlConsole_Run(self):
        self.Connect()
        self.ControlConsole_register()
        self.ControlConsole_startwait()
        self.ControlConsole_broadcastCtrlRequest()

    def WorkNode_Run(self):
        self.Connect()
        self.WorkNode_register()
        self.WorkNode_startwait()


    def WorkNode_SetEcckeyCallback(self,func):
        self.Runtimevar['callback_GetEccPukByID']=func

    def WorkNode_SetPasswsCallback(self,func):
        self.Runtimevar['callback_GetPasswdHashByID']=func

    def WorkNode_SetPasswsCallback(self,func):
        self.Runtimevar['callback_GetPasswdHashByID']=func

    def WorkNode_SetOnReceiveCallback(self,func):
        self.Runtimevar['callback_Onreceive']=func

    def WorkNode_SetOnAuthedCallback(self,func):
        self.Runtimevar['callback_OnAuthed']=func

    def WorkNode_SetKECSLconfigCallback(self,func):
        self.Runtimevar['callback_KECSLconfig']=func
