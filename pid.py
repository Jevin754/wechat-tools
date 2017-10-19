import os
import itchat
import time
import commands


account_alias = u'.'
print "Login wechat..."
itchat.auto_login(enableCmdQR=2, hotReload=True)
account_info = itchat.search_friends(name = account_alias)


stopFlag = False
def monitorgpu(pid_list):
	numPids = len(pid_list)
	pidFlags = {}
	for p in pid_list:
		pidFlags[p] = True
	while not stopFlag:
		time.sleep(1)
		
		for p in pid_list:
			comd = 'nvidia-smi |grep %s' % p
			status, output = commands.getstatusoutput(comd)
			if (status == 256) & pidFlags[p]:
				msg = 'Message from Ti-Two: PID-%s finished!' % p
				print msg
				itchat.send(msg, toUserName='filehelper')
				pidFlags[p] = False

if __name__ == '__main__':
	# account_alias = u'.'
	# itchat.auto_login(enableCmdQR=2, hotReload=True)
	# account_info = itchat.search_friends(name = account_alias)
	
	pid_list = [27564,25988]
	monitorgpu(pid_list)
