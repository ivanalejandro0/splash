from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import sys, time

class HeartbeatSender(DatagramProtocol):
    def __init__(self, name, host, port):
        self.name = name
        self.loopObj = None
        self.host = host
        self.port = port

    def startProtocol(self):
        # Called when transport is connected
        # I am ready to send heart beats
        self.transport.joinGroup('224.0.0.1')
        self.loopObj = LoopingCall(self.sendHeartBeat)
        self.loopObj.start(2, now=False)

    def stopProtocol(self):
        "Called after all transport is teared down"
        pass

    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)


    def sendHeartBeat(self):
        self.transport.write(self.name, (self.host, self.port))



class HeartbeatReciever(DatagramProtocol):
    def __init__(self, name):
        self.name = name

    def startProtocol(self):
        "Called when transport is connected"
        self.transport.joinGroup('224.0.0.1')
        pass

    def stopProtocol(self):
        "Called after all transport is teared down"


    def datagramReceived(self, data, (host, port)):
        now = time.localtime(time.time())  
        timeStr = str(time.strftime("%y/%m/%d %H:%M:%S",now)) 
        print "%s received %r from %s:%d at %s" % (self.name, data, host, port, timeStr)



heartBeatSenderObj = HeartbeatSender("sender", "224.0.0.1", 8005)

reactor.listenMulticast(8005, HeartbeatReciever("listner1"), listenMultiple=True)
reactor.listenMulticast(8005, HeartbeatReciever("listner2"), listenMultiple=True)
reactor.listenMulticast(8005, heartBeatSenderObj, listenMultiple=True)
reactor.run()
