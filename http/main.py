# coding=utf8
#copyright@Catosoft.com reserved, 2016

import sys
# import gendata as GenData
import time
import threading, signal
import random
import httplib, urllib
import math

#设备ID，查看方式为  主页->产品管理->选择产品->设备管理
DEVICE_ID='e0639be8848e3903c9150ce785b0c881' ;	

#package_id 查看方式为 主页->产品管理->选择产品->数据接口
PACKAGE_ID='612a272ad6edcdb7c3e6' ;

#	服务器地址
HOST='106.14.46.176' ;
#	http服务器端口
PORT=9005 ;

RETURNOK='OK'
BUFFER_SIZE=255

is_exit = False


def GenData(runSecond, funcName):
#	warn是数据接口的标识符号，其定义的数据点类型顺序为  数值型，布尔型-------请参考GenerateDevice_Upload函数说明部分
#	water_consume的数据点类型顺序为数值型------请参考GenerateDevice_Upload函数说明部分
#	distrubute的数据点类型的顺序为数值型，数值型。--------请参考GenerateDevice_Upload函数说明部分
	if funcName == "warn":
		temp = runSecond % 100 + 1;
		if temp > 40:
			return [ str(temp), "true"];
		else:
			return [ str(temp), "false"];

	if funcName == "water_consume":
		temp = runSecond % 100 + 1;
		return [ str(temp) ]

	if funcName == "distrubute":
		len = 8.0
		n = runSecond * 0.2
		lang = 110.000 + len * math.sin(n) + random.uniform(0,0.5)
		lat = 35.000 + len * math.cos(n) + random.uniform(0,0.5)

		return [str(lang), str(lat)]

	else:
		return []


def genData(runSecond):
	szUploadData = []
	
	interval = 5 ;
	if interval < 1:
		return szUploadData
	if runSecond%interval == interval-1:
		szUploadData = GenData(runSecond, "warn")

	return szUploadData

def getTag():
	return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())) + " thread-" + " > "

def loop(deviceId):

	# try:
		doReport(deviceId);
	# except:
		# print getTag() + " exception "

def doReport(deviceId):
	global is_exit
	workNum = 10;
	while not is_exit:
		szUploadData = genData(workNum)

		if len(szUploadData) > 0:		
			data = ';'.join(szUploadData) 
			print getTag() + " connect and send " + data
			params = urllib.urlencode({'deviceId': deviceId, 'packageId': PACKAGE_ID, 'datas':data })
			headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
			conn = httplib.HTTPConnection(HOST, PORT)
			conn.request("POST", "/upload/devicedata/v1", params, headers)
			response = conn.getresponse()
			print response.status, response.reason

			content = response.read()
			conn.close()

		workNum+=1
		time.sleep(1); 

def handler(signum, frame):
	global is_exit
	is_exit = True
	print "receive a signal %d, is_exit = %d"%(signum, is_exit)


def main(argv=None):
	signal.signal(signal.SIGINT, handler)
	signal.signal(signal.SIGTERM, handler)
	

	print ' ### sleep 2 second to check the config ###'
	# time.sleep(2)
	loop(DEVICE_ID) ;

if __name__ == "__main__":
	sys.exit(main())


