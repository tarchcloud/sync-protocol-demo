# coding=utf8

#copyright@Catosoft.com reserved, 2016
#history:
#2016.12.14, created by Jason.Chen

import socket
import time
import fcntl,os
import select 
import sys
import time
import threading, signal
import random
import math

RETURNOK='OK'
BUFFER_SIZE=255
is_exit = False

#设备ID，查看方式为  主页->产品管理->选择产品->设备管理
DEVICE_ID='e0639be8848e3903c9150ce785b0c881' ;	

#package_id 查看方式为 主页->产品管理->选择产品->数据接口
PACKAGE_ID='612a272ad6edcdb7c3e6' ;

#	服务器地址
HOST='106.14.46.176' ;
#	tcp服务器端口
PORT= 9003;

# 上线命令
DEVICE_ONLINE='1001'
# 心跳命令
DEVICE_BEAT = '1004'
# 上传数据的命令
DEVICE_UPLOAD='1003'
# 服务器下发受到的命令
DEVICE_CONTROL='1002'
#	自定义的blink命令，详见 主页->产品管理->选择产品->控制命令
DEVICE_CONTROL_BLINK='blink'
DEVICE_CONTROL_PAY_BLINK='pay' 

# 	函数：GenerateDevice_OnLine
# 	参数：
#	 	deviceId:	对应设备id。
#	说明：	
#		根据传入的设备id，生成上线字符串命令
def GenerateDevice_OnLine(deviceId):
	return '#'+DEVICE_ONLINE + '#'+deviceId+'#'

# 	函数：GenerateDevice_Bead
# 	参数：
#	 	
#	说明：	
#		生成心跳字符串命令
def GenerateDevice_Bead():
	return '#'+DEVICE_BEAT + '#' ;

# 	函数：GenerateDevice_Upload
# 	参数：
#	 	PackageId:	数据接口ID。
# 		Params:	对应的数据接口的数据点数组，数组顺序按照数据点的定义的顺序
#		例如数据接口A定义如下数据点
#		数据点名---------标识-----类 型---------范围-------描述
#		warn   ---------warn----数 值--------——0～100-------warn
#		bool   ---------bool-----布尔---------------------布尔类型
#		则数组为['20',true]
#	说明：	
#		生成上传数据的字符串。
def GenerateDevice_Upload(PackageId,Params):
	if(len(Params) <= 0):
		return False ;
	return '#'+DEVICE_UPLOAD + '#' + PackageId + '#' + '#'.join(Params) + '#'


class TcpClient(object):
	def __init__(self):
		self.tcpClient=socket.socket(socket.AF_INET,socket.SOCK_STREAM) ;

	def tcpConnect(self,ServerAddress,ServerPort):
		bReturn = False ;
		count = 0
		ServerInfo = (ServerAddress,ServerPort) ;
		while count < 10:
			print 'reconnect count:',count
			try:
				self.tcpClient.connect(ServerInfo) ;
				bReturn = True ;
				break ;
			except Exception, e:
				print e ;
				time.sleep(0.1) ;
			else:
				pass
			finally:
				pass
			count=count+1 ;
		return bReturn ;

	def tcpRead(self, nMax):
		self.tcpClient.settimeout(1)
		str='' ;
		try:
			str = self.tcpClient.recv(nMax) ;
			pass
		except socket.error, e:
			print e
		else:
			pass
		finally:
			pass
		return str 

	def tcpReadBlock(self, nMax):
		str='' ;
		try:
			str = self.tcpClient.recv(nMax) ;
			pass
		except socket.error, e:
			print e
		else:
			pass
		finally:
			pass
		return str 

	def send(self, szContent):
		self.tcpClient.send(szContent) ;

	def tcpClose(self):
		self.tcpClient.close() ;


	def tcpSelect(self, nMax):
		output=[] ;
		inputs = [self.tcpClient] ;
		str='' ;
		try:
			readable,writeable,exceptional = select.select(inputs,output,inputs,1) ;
		except select.error,e:
			print e ;
		if self.tcpClient in readable:
			str = self.tcpClient.recv(nMax) ;
		return str ;


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
	szUploadData = GenData(runSecond, 'warn')
	return szUploadData ;


def getTag():
	return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())) + "-" + " > "

def loop():
		doReport(DEVICE_ID);

def doReport(deviceId):
	global is_exit
	tcp = TcpClient();
	print getTag() + ", connect " + HOST + ":" + str(PORT) ;
	
	if False == tcp.tcpConnect(HOST,PORT) :
		print getTag() + 'connnect err'
		sys.exit(0)

	print getTag() + 'connect success' + HOST + ':' + str(PORT) ;
	strCommandOnline = GenerateDevice_OnLine(deviceId) ;

	tcp.send(strCommandOnline) ;
	print getTag() + ">>" + strCommandOnline 
	szCommand = tcp.tcpSelect(BUFFER_SIZE) ;
	print getTag() + "<<" +  szCommand ;

	workNum = 50 ;
	print is_exit ;
	while not is_exit:
		szUploadData = genData(workNum)
		print 'upload Data:' , szUploadData ;	
		if len(szUploadData) > 0:
			szCommand = GenerateDevice_Upload(PACKAGE_ID,szUploadData) ;
			print getTag() + ">>" + szCommand ;
			tcp.send(szCommand) ;
			szCommand = tcp.tcpSelect(BUFFER_SIZE) ;
			if len(szCommand) > 0:
				print getTag() + "<<" + szCommand ;

		#监听server发来的命令，如果想接受命令，将下面去掉下面注释就可以了
		#szCommand = tcp.tcpSelect(BUFFER_SIZE) ;

		# if len(szCommand) > 0:
		# 	print getTag() + "<<" +  szCommand ;
		# if szCommand.strip():
		# 	if(szCommand.find(DEVICE_CONTROL_BLINK) > 0) :
		# 		print getTag() + 'blink' ;

		# 	elif (szCommand.find(DEVICE_CONTROL_PAY_BLINK) > 0) :
		# 		print getTag() + 'pay' ;

		# bind
		if workNum%30 == 0:
			strCommandOnline = GenerateDevice_Bead() ;
			tcp.send(strCommandOnline) ;
			szCommand = tcp.tcpSelect(BUFFER_SIZE) ;
		workNum+=1
		if workNum%5==0:
			time.sleep(5); 
	print getTag() + "tcpClose"
	tcp.tcpClose();

def handler(signum, frame):
	global is_exit
	is_exit = True
	print "receive a signal %d, is_exit = %d"%(signum, is_exit)


def main(argv=None):

	signal.signal(signal.SIGINT, handler)
	signal.signal(signal.SIGTERM, handler)
	
	loop() ;

if __name__ == "__main__":
	sys.exit(main())

