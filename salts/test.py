#-*- coding: utf-8 -*-
from salt.client import LocalClient
from salt.config import client_config
from utils import SaltByLocalApi
def test1():
    client=LocalClient()
    result=client.cmd('self','oss:centos',['ls /root'],'grain')
    print result
#    for k,v  in result.iteritems():
#	print k
#	print '----'
#	for i,j in v.iteritems():
#	    print i
#	    print j
#

def parse_target_params(target,match):
    saltapi=SaltByLocalApi('/etc/salt/master')
    active_minion_list=saltapi.connected_minions_list
    nodegroup_list=[]
    t_list=[]
    target=target.replace(' ','')
    for key in saltapi.get_master_config()['nodegroups'].iterkeys():
	nodegroup_list.append(key)
    if match == 'list':
	L=target.split(',')
	t_list=[x for x in L if x !='']
        for v in t_list:
	    if v not in active_minion_list:
		return None,'do not exists the minion: %s' %v
	return True,','.join(t_list)
    elif match == 'glob':
	if target == '*':
	    pass
	elif target not in active_minion_list:
	    return None,'illegal hostname: %s ' %target
    elif match == 'grain':
        grains=saltapi.get_grains().values()[0]
	if grains is None:
	    return None,'do not exists online monions'
        var_list=target.split(':')
	length=len(var_list)
	if length<2:
	    return None,'illegal grains'
        g_var=var_list[length-1]
	g_key=var_list[:length-1]
	for k in g_key:
	    if k not in grains:
		return None,'bad grains key : %s' %k
            grains=grains[k] 
    elif match == 'nodegroup':
	if target not in nodegroup_list:
	    return None,'do not exist nodegroup: %s' %target
    return True,target


if __name__=='__main__':
    print parse_target_params('supply_webss','nodegroup')
