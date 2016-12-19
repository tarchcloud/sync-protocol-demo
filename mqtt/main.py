# coding=utf8
#!/usr/bin/python

import time

#   服务器地址
SERVER_ADDRESS='106.14.46.176'
#   mqtt服务器端口
SERVER_PORT=9004

#设备ID，查看方式为  主页->产品管理->选择产品->设备管理
DEVICE_ID='e0639be8848e3903c9150ce785b0c881'

#package_id 查看方式为 主页->产品管理->选择产品->数据接口
PACKAGEID='612a272ad6edcdb7c3e6'


gid=DEVICE_ID
TOPIC_COMMAND = gid + "/command" ;
TOPIC_UPLOAD_RESULT = gid + "/upload_result"
TOPIC_UPLOAD=   "upload"
TOPIC_RESULT= "command_result" ;
# 上线命令
DEVICE_ONLINE='1001'
# 心跳命令
DEVICE_BEAT = '1004'
# 上传数据的命令
DEVICE_UPLOAD='1003'
# 服务器下发受到的命令
DEVICE_CONTROL='1002'

#   自定义的blink命令，详见 主页->产品管理->选择产品->控制命令
DEVICE_CONTROL_BLINK='blink'
DEVICE_CONTROL_PAY_BLINK='pay' 

import sys
try:
    import paho.mqtt.client as mqtt
except ImportError:
    import os
    import inspect
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"paho-mqtt-1.1/src")))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import paho.mqtt.client as mqtt

#   函数：GenerateDevice_OnLine
#   参数：
#       deviceId:   对应设备id。
#   说明： 
#       根据传入的设备id，生成上线字符串命令
def GenerateDevice_OnLine(deviceId):
    return '#'+DEVICE_ONLINE + '#'+deviceId+'#'

#   函数：GenerateDevice_Bead
#   参数：
#       
#   说明： 
#       生成心跳字符串命令
def GenerateDevice_Bead():
    return '#'+DEVICE_BEAT + '#' ;

#   函数：GenerateDevice_Upload
#   参数：
#       PackageId:  数据接口ID。
#       Params: 对应的数据接口的数据点数组，数组顺序按照数据点的定义的顺序
#       例如数据接口A定义如下数据点
#       数据点名---------标识-----类 型---------范围-------描述
#       warn   ---------warn----数 值--------——0～100-------warn
#       bool   ---------bool-----布尔---------------------布尔类型
#       则数组为['20',true]
#   说明： 
#       生成上传数据的字符串。
def GenerateDevice_Upload(PackageId,Params):
    if(len(Params) <= 0):
        return False ;
    return '#'+DEVICE_UPLOAD + '#' + PackageId + '#' + '#'.join(Params) + '#'

global isConnect
isConnect=0

def getCommandExecuteResult(id,code):
    strData = {}
    strData["id"]=id;
    strData["code"] = code;
    if(code == 200):
        strData["msg"] = "success";
    else:
        strData["msg"] = "fail";
    return json.dumps(strData);

def on_connect(mqttc, obj, flags, rc):
    global isConnect
    isConnect=1
    print("connected > rc: "+str(rc))
    mqttc.subscribe(TOPIC_COMMAND, 0)
    mqttc.subscribe(TOPIC_UPLOAD_RESULT, 0)


def on_message(mqttc, obj, msg):
    print( "on_message > " +msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    if(msg.qos == 0):
        if(TOPIC_COMMAND == msg.topic):
            print '*** we should execute command ' + str(msg.payload)
            #afte execute, we should public the result.
            commandInfo = json.loads(str(msg.payload))

            result = getCommandExecuteResult(commandInfo["id"], 200)
            mqttc.publish(TOPIC_RESULT, result)
            print 'publish result = ' + result

        if(TOPIC_UPLOAD_RESULT == msg.topic):
            print 'get update result = ' + str(msg.payload)



def on_publish(mqttc, obj, mid):
    print("on_publish mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed > "+str(mid)+" "+str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

def on_disconnect(mqttc, obj, rc):
    global isConnect
    isConnect=0
    print("disconnected > rc: "+str(rc))

mqttc = mqtt.Client();
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_disconnect = on_disconnect

mqttc.username_pw_set(gid, "")
# Uncomment to enable debug messages
#mqttc.on_log = on_log
mqttc.connect(SERVER_ADDRESS, SERVER_PORT, 30)
# mqttc.subscribe(TOPIC_COMMAND, 0)

# loop async
mqttc.loop_start()
# mqttc.loop_forever()

i = 0 ;
while(1):
    # only publish when the server is connected.
    if not isConnect:
        time.sleep(1)
        continue

    if i%2 == 0:
        time.sleep(1) ;

    i=i+1;
    temp = i % 100 + 1;
    if i%30 == 0:
        if temp > 40:
            strData = '\"' + str(temp) + '\",\"true\"';
          # szUploadData = str(temp) + '#' +"true";
        else:
            strData = '\"' + str(temp) + '\",\"false\"';
        szUploadData = "{\"packageId\":\"" + PACKAGEID + "\",\"datas\":[" + strData + "]}"
        print "upload " + szUploadData

        mqttc.publish(TOPIC_UPLOAD, szUploadData)
