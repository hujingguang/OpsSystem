#!/usr/bin/env python
import threading
import sys
import time
import os
import commands
import psutil
import random
import urllib,urllib2
import socket
from optparse import OptionParser
SERVER_IP=''
SERVER_PORT=8899
DETECT_TIME=3600

try:
    import simplejson
except ImportError as e:
    import json as simplejson


def get_daemon():
    res,hostname=commands.getstatusoutput('hostname')
    daemon_list=[]
    tmp_list=[]
    illegal_daemon_list=[]
    p=psutil.Process(1)
    for pp in p.children():
	tmp_list.append(pp.name())
    for i in tmp_list:
	if i not in daemon_list:
	    daemon_list.append(i)
    all_daemon_list=[]
    try:
	with open('/etc/daemon.conf','r') as f:
	    for i in f.readlines():
		all_daemon_list.append(i.replace('\n',''))
    except Exception as e:
	print e
    for daemon in daemon_list:
	if daemon not in all_daemon_list:
	    illegal_daemon_list.append(daemon)
    if illegal_daemon_list != []:
	prefix='illegal daemon on %s running: ' %hostname
	for d in illegal_daemon_list:
	    prefix=prefix+'*'+d
	sendsms(prefix)

def daemon_safe_check():
    sleep_time=5
    while 1:
	get_daemon()
	time.sleep(sleep_time)
        print 'check...ok'

def sendsms(mess):
    app_id='your secret id'
    ID=str(random.randint(134234,876355))
    url='http://api.110monitor.com/alert/api/event'
    data={'app':app_id,
	    'priority':'3',
	    'eventType':'trigger',
	    'alarmName':mess,
	    'alarmContent':mess,
	    'eventId':ID,
	    'entityId':ID
	    }
    data=simplejson.dumps(data)
    header={'Content-type':'application/json'}
    request=urllib2.Request(url,data,header)
    response=urllib2.urlopen(request)
    print response.read()



def init_login_env():
    log_path='/tmp/.history_cmd.log'
    shell_scripts='''
    #!/bin/bash
    hist_format="export HISTTIMEFORMAT=\\"%Y-%m-%d %H:%M:%S @_@\$(whoami)@_@\`who am i|awk -F'[)(]' '{print \$2}'\`@_@\\""
    #echo $hist_format >>/etc/profile
    egrep '@_@' /etc/profile &>/dev/null
    if [ $? != 0 ]
         then
              echo $hist_format >>/etc/profile
    fi
    egrep '@_@' /root/.bash_profile &>/dev/null
    if [ $? != 0 ]
         then
              echo $hist_format >>/root/.bash_profile
    fi
    egrep 'history_cmd' /root/.bash_logout &>/dev/null
    if [ $? != 0 ]
      then
      echo "\`history >>/tmp/.history_cmd.log\`" >> /root/.bash_logout
    fi
    for i in `find /home/* |egrep '.bash_logout' `
    do
        egrep 'history_cmd' $i &>/dev/null
        if [ $? != 0 ]
          then
           echo "\`history >>/tmp/.history_cmd.log\`" >> $i
        fi
	chattr +a $i
    done
    if [ ! -e /tmp/.history_cmd.log ]
      then
          touch /tmp/.history_cmd.log
           chmod 777 /tmp/.history_cmd.log
          chattr +a /tmp/.history_cmd.log &>/dev/null
    fi
    '''
    with open('/tmp/.run_script.sh','w') as f:
	f.write(shell_scripts)
    os.system('bash /tmp/.run_script.sh')

def parse_history_log_file(path,num=1):
    cmd=r''' cat %s |awk '{$1="";print $0}'|sort -k1,2 | uniq -c|awk '{$1="";print $0}' >/tmp/.parse.log''' %path
    cmd_add_line_num=r''' sed = /tmp/.parse.log|sed 'N;s/\n/\t/' >/tmp/.format.log '''
    #cmd_get_begin_line=r''' sed -n '/%s.*/p' /tmp/.format.log |awk '{print $1}' ''' %dt
    cmd_get_total_line_num=''' cat /tmp/.parse.log |wc -l'''
    os.system(cmd)
    os.system(cmd_add_line_num)
    res,total=commands.getstatusoutput(cmd_get_total_line_num)
    total=int(total) 
    if os.path.exists('/tmp/.flag'):
	with open('/tmp/.flag','r') as f:
	    num=f.readline().replace('\n','').split(':')[1]
	    num=int(num)
    if total < num:
	total=num
    with open('/tmp/.flag','w') as f:
	f.write(str(num)+':'+str(total))
    shell_scripts='''
    func(){
     num=$1
     file=$2
     i=`sed -n "/^$num\s/p" $file`
     line=`echo $i |awk '{$1="";print $0}'`
     time=`echo $line |awk -F'@_@' '{print $1}'`
     user=`echo $line |awk -F '@_@' '{print $2}'`
     ip=`echo $line |awk -F '@_@' '{print $3}'`
     cmd=`echo $line |awk -F '@_@' '{print $4}'`
     echo $time'@_@'$user'@_@'$ip'@_@'$cmd
    }
    func $1 $2
    '''
    with open('/tmp/parse.sh','w') as f:
	f.write(shell_scripts)
    os.system('chmod +x /tmp/parse.sh')
    return (num,total,'/tmp/parse.sh','/tmp/.format.log')


def send_cmd_info():
    global SERVER_IP,SERVER_PORT,DETECT_TIME
    sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sec=86400
    res,hostname=commands.getstatusoutput('hostname')
    while True:
        begin,end,script,log=parse_history_log_file('/tmp/.history_cmd.log')
        try:
            sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	    sk.connect((SERVER_IP,SERVER_PORT))
            for i in range(begin,end):
	        cmd=script+' '+str(i)+' '+log
	        res,info=commands.getstatusoutput(cmd)
		if info:
		    str_list=info.split('@_@')
		    dicts={'type':'cmd'}
		    dicts['time']=str_list[0].rstrip(' ')
		    dicts['user']=str_list[1]
		    dicts['ip']=str_list[2]
		    dicts['cmd']=str_list[3]
		    dicts['host']=hostname
		    json=simplejson.dumps(dicts)
		    if dicts['ip'] == '' or dicts['user'] == '':
			continue
	            sk.sendall(json)
        except Exception as e:
	    print e
        finally:
	    sk.close()
	time.sleep(DETECT_TIME)

class MainAgent(object):
    def __init__(self,func_list=[]):
	self.func_list=[]
	self.threads=[]
	if func_list:
	    for func in func_list:
		self.func_list.append(func)
    def pre_threads(self):
	if self.func_list:
	    for func in self.func_list:
	        func_thread=threading.Thread(target=func)
	        self.threads.append(func_thread)
        return self.threads
    def start_threads(self):
	for td in self.pre_threads():
	    td.setDaemon(True)
	    td.start()
    def get_threads(self):
	return self.threads
 
def daemonize():
   try:
        pid=os.fork()
        if pid>0:
            sys.exit(0)
   except OSError as e:
       print e
       sys.exit(1)
   os.chdir('/')
   os.umask(0)
   os.setsid()
   try:
       pid=os.fork()
       if pid>0:
           sys.exit(0)
   except OSError as e:
       print e
       sys.exit(1)
   for f in sys.stdout, sys.stderr: f.flush()
   si=file('/dev/null','r')
   so=file('/dev/null','a+')
   se=file('/dev/null','a+',0)
   os.dup2(si.fileno(), sys.stdin.fileno())
   os.dup2(so.fileno(), sys.stdout.fileno())
   os.dup2(se.fileno(), sys.stderr.fileno())



def main():
    global SERVER_IP,SERVER_PORT,DETECT_TIME
    parse=OptionParser(usage='''
	    Usage: agent [options]
	    this is monitor send login and commands to master server
	    ''')
    parse.add_option('-m','--master',
	    type='string',
	    action='store',
	    help='the server host ip must be append!',
	    dest='server_ip')
    parse.add_option('-p','--port',
	    type='int',
	    action='store',
	    help='the server listen port ,default is 8899',
	    dest='port',
	    default=8899)
    parse.add_option('-s','--second',
	    type='int',
	    help='detect command log file per second',
	    dest='sec',
	    default=3600)
    parse.add_option('-d','--daemonize',
	    action='store_false',
	    help='run agent as daemon',
	    default=True
	    )
    opts,args=parse.parse_args()
    if not opts.server_ip:
	parse.print_help()
	sys.exit(1)
    if not opts.daemonize:
	daemonize()
    SERVER_IP=opts.server_ip
    SERVER_PORT=opts.port
    DETECT_TIME=opts.sec
    init_login_env()
    #func_list=[send_cmd_info,daemon_safe_check] ,if you want using the illegal daemon check, you must configure sendsms function.
    func_list=[send_cmd_info]
    agent=MainAgent(func_list)
    agent.start_threads()
    threads=agent.get_threads()
    for t in threads:
	t.join()


if __name__ == '__main__':
    main()
