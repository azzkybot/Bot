# -*- coding: utf-8 -*-
from LineAlpha import LineClient
from LineAlpha.LineApi import LineTracer
from LineAlpha.LineThrift.ttypes import Message
from LineAlpha.LineThrift.TalkService import Client
import time, datetime, random ,sys, re, string, os, json

reload(sys)
sys.setdefaultencoding('utf-8')

client = LineClient()
client._qrLogin("line://au/q/")

profile, setting, tracer = client.getProfile(), client.getSettings(), LineTracer(client)
offbot, messageReq, wordsArray, waitingAnswer = [], {}, {}, {}

print client._loginresult()

wait = {
    'readPoint':{},
    'readMember':{},
    'setTime':{},
    'ROM':{}
   }

setTime = {}
setTime = wait["setTime"]

def sendMessage(to, text, contentMetadata={}, contentType=0):
    mes = Message()
    mes.to, mes.from_ = to, profile.mid
    mes.text = text

    mes.contentType, mes.contentMetadata = contentType, contentMetadata
    if to not in messageReq:
        messageReq[to] = -1
    messageReq[to] += 1
    client._client.sendMessage(messageReq[to], mes)

def NOTIFIED_ADD_CONTACT(op):
    try:
        sendMessage(op.param1, client.getContact(op.param1).displayName + "Thanks for add")
    except Exception as e:
        print e
        print ("\n\nNOTIFIED_ADD_CONTACT\n\n")
        return

tracer.addOpInterrupt(5,NOTIFIED_ADD_CONTACT)

def NOTIFIED_ACCEPT_GROUP_INVITATION(op):
    #print op
    try:
        sendMessage(op.param1, client.getContact(op.param2).displayName + "c " + group.name)
    except Exception as e:
        print e
        print ("\n\nNOTIFIED_ACCEPT_GROUP_INVITATION\n\n")
        return

tracer.addOpInterrupt(17,NOTIFIED_ACCEPT_GROUP_INVITATION)

def NOTIFIED_KICKOUT_FROM_GROUP(op):
    try:
        sendMessage(op.param1, client.getContact(op.param3).displayName + "已被退出群組")
    except Exception as e:
        print e
        print ("\n\nNOTIFIED_KICKOUT_FROM_GROUP\n\n")
        return

tracer.addOpInterrupt(19,NOTIFIED_KICKOUT_FROM_GROUP)

def NOTIFIED_LEAVE_GROUP(op):
    try:
        sendMessage(op.param1, client.getContact(op.param2).displayName + "已退出群組")
    except Exception as e:
        print e
        print ("\n\nNOTIFIED_LEAVE_GROUP\n\n")
        return

tracer.addOpInterrupt(15,NOTIFIED_LEAVE_GROUP)

def NOTIFIED_READ_MESSAGE(op):
    #print op
    try:
        if op.param1 in wait['readPoint']:
            Name = client.getContact(op.param2).displayName
            if Name in wait['readMember'][op.param1]:
                pass
            else:
                wait['readMember'][op.param1] += "\n・" + Name
                wait['ROM'][op.param1][op.param2] = "・" + Name
        else:
            pass
    except:
        pass

tracer.addOpInterrupt(55, NOTIFIED_READ_MESSAGE)

def RECEIVE_MESSAGE(op):
    msg = op.message
    try:
        if msg.contentType == 0:
            try:
                if msg.to in wait['readPoint']:
                    if msg.from_ in wait["ROM"][msg.to]:
                        del wait["ROM"][msg.to][msg.from_]
                else:
                    pass
            except:
                pass
        else:
            pass
    except KeyboardInterrupt:
	       sys.exit(0)
    except Exception as error:
        print error
        print ("\n\nRECEIVE_MESSAGE\n\n")
        return

tracer.addOpInterrupt(26, RECEIVE_MESSAGE)

def SEND_MESSAGE(op):
    msg = op.message
    try:
        if msg.toType == 0:
            if msg.contentType == 0:
                if msg.text == "mid":
                    sendMessage(msg.to, msg.to)
                if msg.text == "me":
                    sendMessage(msg.to, text=None, contentMetadata={'mid': msg.from_}, contentType=13)
                if msg.text == "gift":
                    sendMessage(msg.to, text="gift sent", contentMetadata=None, contentType=9)
                else:
                    pass
            else:
                pass
        if msg.toType == 2:
            if msg.contentType == 0:
                
                if "kick:" in msg.text:
                    key = msg.text[5:]
                    client.kickoutFromGroup(msg.to, [key])
                    contact = client.getContact(key)
                    sendMessage(msg.to, ""+contact.displayName+" 敬酒不吃 吃罰酒")
                if "nk:" in msg.text:
                    key = msg.text[3:]
                    group = client.getGroup(msg.to)
                    Names = [contact.displayName for contact in group.members]
                    Mids = [contact.mid for contact in group.members]
                    if key in Names:
                        kazu = Names.index(key)
                        sendMessage(msg.to, "敬酒不吃")
                        client.kickoutFromGroup(msg.to, [""+Mids[kazu]+""])
                        contact = client.getContact(Mids[kazu])
                        sendMessage(msg.to, ""+contact.displayName+" 吃罰酒")
                    else:
                        sendMessage(msg.to, "錯誤 查無此人 提示：不能標人 名字去他人姓名欄複製")
                if msg.text == "cancel":
                    group = client.getGroup(msg.to)
                    if group.invitee is None:
                        sendMessage(op.message.to, "邀請欄真乾淨 沒有用戶被取消")
                    else:
                        gInviMids = [contact.mid for contact in group.invitee]
                        client.cancelGroupInvitation(msg.to, gInviMids)
                        sendMessage(msg.to, str(len(group.invitee)) + " 個用戶被取消邀請")
                if "invite:" in msg.text:
                    key = msg.text[-33:]
                    client.findAndAddContactsByMid(key)
                    client.inviteIntoGroup(msg.to, [key])
                    contact = client.getContact(key)
                    sendMessage(msg.to, ""+contact.displayName+" 邀你了 不用謝我")
		if msg.text == "kick all":
                    print "ok"
                    _name = msg.text.replace("kick all","")
                    gs = client.getGroup(msg.to)
                    sendMessage(msg.to,"全面破壞 every. get you fuckout away.")
                    targets = []
                    for g in gs.members:
                        if _name in g.displayName:
                            targets.append(g.mid)
                    if targets == []:
                        sendMessage(msg.to,"error")
                    else:
                        for target in targets:
                            try:
                                klist=[client]
                                kicker=random.choice(klist)
                                kicker.kickoutFromGroup(msg.to,[target])
                                print (msg.to,[g.mid])
                            except:
                                sendText(msg.to,"error")

                if msg.text == "艾登⚫皮爾斯已被退出群組":
                    sendMessage(msg.to, "invite:u799fc61385cd0746c0eea9a7f5c68587")
                    try:
                        del wait['readPoint'][msg.to]
                        del wait['readMember'][msg.to]
                    except:
                        pass
                    wait['readPoint'][msg.to] = msg.id
                    wait['readMember'][msg.to] = ""
                    wait['setTime'][msg.to] = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    wait['ROM'][msg.to] = {}
                    print wait
		if msg.text == "傑克森⚫皮爾斯已被退出群組":
                    sendMessage(msg.to, "invite:ub0931037994cc32cf40b5761c333030c")
                    try:
                        del wait['readPoint'][msg.to]
                        del wait['readMember'][msg.to]
                    except:
                        pass
                    wait['readPoint'][msg.to] = msg.id
                    wait['readMember'][msg.to] = ""
                    wait['setTime'][msg.to] = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    wait['ROM'][msg.to] = {}
                    print wait
		if msg.text == "莉娜⚫皮爾斯已被退出群組":
                    sendMessage(msg.to, "invite:ube4240b2b1032b45b51b58793e4a49a9")
                    try:
                        del wait['readPoint'][msg.to]
                        del wait['readMember'][msg.to]
                    except:
                        pass
                    wait['readPoint'][msg.to] = msg.id
                    wait['readMember'][msg.to] = ""
                    wait['setTime'][msg.to] = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    wait['ROM'][msg.to] = {}
                    print wait
		if msg.text == "松阪明夫已被退出群組":
                    sendMessage(msg.to, "invite:u989138703b60eebbf7e46c4266436dba")
                    try:
                        del wait['readPoint'][msg.to]
                        del wait['readMember'][msg.to]
                    except:
                        pass
                    wait['readPoint'][msg.to] = msg.id
                    wait['readMember'][msg.to] = ""
                    wait['setTime'][msg.to] = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    wait['ROM'][msg.to] = {}
                    print wait
                if msg.text == "tes":
                    if msg.to in wait['readPoint']:
                        if wait["ROM"][msg.to].items() == []:
                            chiya = ""
                        else:
                            chiya = ""
                            for rom in wait["ROM"][msg.to].items():
                                print rom
                                chiya += rom[1] + "\n"

                        sendMessage(msg.to, "看到訊息者 %s\n♪\n\n已讀不回者\n%s♪\n\n此訊息偵測時間:\n[%s]"  % (wait['readMember'][msg.to],chiya,setTime[msg.to]))
                    else:
                        sendMessage(msg.to, "已讀不回者\n「set」♪ 不要以為我不知道 ♪")
                else:
                    pass
        else:
            pass

    except Exception as e:
        print e
        print ("\n\nSEND_MESSAGE\n\n")
        return

tracer.addOpInterrupt(25,SEND_MESSAGE)

while True:
    tracer.execute()
