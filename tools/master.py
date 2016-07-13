#!/usr/bin/env python
import optparse
import os
import socket
import select
import MySQLdb
import sys
import time
import simplejson
import SocketServer
db_info={'db_name':'deploy',
	'host':'10.117.74.247',
	'user':'root',
	'password':'helloworld',
	}

class MainMaster(object):
    def __init__(self):
	global db_info
	self.db_name=db_info.get('db_name',None)
	self.host=db_info.get('host',None)
	self.user=db_info.get('user',None)
	self.password=db_info.get('password',None)
    def get_db_connect(self):
	try:
	    conn=MySQLdb.connect(user=self.user,passwd=self.password,host=self.host,db=self.db_name)
	except Exception as e:
	    print e
	    sys.exit(1)
	return conn
    def daemonize(self):
	try:
	    pid=os.fork()
	    if pid>0:
		sys.exit()
	except OSError as e:
	    print e
	    sys.exit(1)
	try:
	    pid=os.fork()
	    if pid>0:
		sys.exit()
	except OSError as e:
	    print e
	    sys.exit(1)
	for f in sys.stdout,sys.stderr:f.flush()
	si=file('/dev/null','r')
	so=file('/dev/null','a+')
	se=file('/dev/null','a+',0)
	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())
    def optparse(self):
	parse=optparse.OptionParser(usage='''
		usage: master.py [Option]
		this is server program collect agent push command info insert database
		''')
	parse.add_option('-l',
		'--listen',
		action='store',
		type='string',
		help='listen ip address',
		default='0.0.0.0',
		dest='listen_ip')
	parse.add_option('-p',
		'--port',
		action='store',
		type='int',
		help='listen port',
		default=8899,
		dest='port'
		)
	parse.add_option('-d','--daemonize',
		action='store_false',
		default=True,
		help='run server as daemon')
	opts,args=parse.parse_args()
	if not opts.daemonize:
	    self.daemonize()
	self.server_ip=opts.listen_ip
	self.server_port=opts.port
    def dowith_cmd_info(self,d=None):
	if d:
	    conn=self.get_db_connect()
	    try:
		d['cmd']=d['cmd'].replace('\\','')
		sql=''' insert into ops_cmd_opt_log (hostname,user,command,login_ip,runtime) values('%s','%s','%s','%s','%s');''' %(d['host'],d['user'],d['cmd'],d['ip'],d['time'])
		cursor=conn.cursor()
		try:
		    cursor.execute(sql)
		    conn.commit()
		except Exception as e:
		    print e
	    except Exception as e:
		sys.exit(1)
	    finally:
		conn.close()
    def start_listen(self):
	sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sk.bind((self.server_ip,self.server_port))
	sk.listen(128)
	fdmap={sk.fileno():sk}
	poll=select.epoll()
	poll.register(sk)
	while True:
	    events=poll.poll()
	    for fd,event in events:
		if fd == sk.fileno():
		    conn,addrs=sk.accept()
		    fdmap[conn.fileno()]=conn
		    poll.register(conn)
		elif fd & select.EPOLLIN:
		    data=fdmap[fd].recv(1024)
		    if not data:
			poll.unregister(fd)
			del fdmap[fd]
		    else:
			with open('/tmp/master','a') as f:
			    f.write(data+'\n')
			try:
			    info=simplejson.loads(data)
			    if info['type'] == 'cmd':
				self.dowith_cmd_info(info)
			except Exception as e:
			    print e
			    pass
    def start_listen2(self):
	server=SocketServer.ForkingTCPServer((self.server_ip,self.server_port),HandlerProcess)
	server.serve_forever()

class HandlerProcess(SocketServer.StreamRequestHandler):
    def handle(self):
	while True:
	    data=self.request.recv(1024)
	    if not data:
		break
	    try:
		info=simplejson.loads(data)
		if info['type'] == 'cmd':
		    self.dowith_cmd_info(info)
	    except Exception as e:
		pass
    def dowith_cmd_info(self,d=None):
	if d:
	    conn=self.get_db_connect()
	    try:
		d['cmd']=d['cmd'].replace('\\','')
		sql=''' insert into ops_cmd_opt_log (hostname,user,command,login_ip,runtime) values('%s','%s','%s','%s','%s');''' %(d['host'],d['user'],d['cmd'],d['ip'],d['time'])
		cursor=conn.cursor()
		try:
		    cursor.execute(sql)
		    conn.commit()
		except Exception as e:
		    print e
	    except Exception as e:
		sys.exit(1)
	    finally:
		conn.close()
    def get_db_connect(self):
        global db_info
	self.db_name=db_info.get('db_name',None)
	self.host=db_info.get('host',None)
	self.user=db_info.get('user',None)
	self.password=db_info.get('password',None)
        try:
	    conn=MySQLdb.connect(user=self.user,passwd=self.password,host=self.host,db=self.db_name)
	except Exception as e:
	    print e
	    sys.exit(1)
	return conn





def main():
    master=MainMaster()
    master.optparse()
    master.start_listen2()


if __name__=='__main__':
    main()










