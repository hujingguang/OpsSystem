#!/usr/bin/env python

import psutil
import urllib2,urllib
import json
import random
import commands
import time
def get_daemon():
    sleep_time=5
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
    time.sleep(sleep_time) 

    
def sendsms(mess):
    app_id='375f0089-6ae1-0b10-a41d-6fa882086341'
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
    data=json.dumps(data)
    header={'Content-type':'application/json'}
    request=urllib2.Request(url,data,header)
    response=urllib2.urlopen(request)


if __name__ == '__main__':
    get_daemon()
