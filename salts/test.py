from salt.client import LocalClient
from salt.config import client_config
from utils import SaltByLocalApi
def test1():
    client=LocalClient()
    config=client_config('/etc/salt/master')
    for k,v in config.iteritems():
	print k,v
    exit()
    result=client.cmd('self','state.sls',['memcached.install'])
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
    for key in saltapi.get_master_config()['nodegroups'].iterkeys():
	nodegroup_list.append(key)
    if match == 'list':
	pass
    elif match == 'hostname':
	pass
    elif match == 'grains':
	pass
    elif match == 'nodegroup':
	pass
    elif match == 'pcre':
	pass


if __name__=='__main__':
    parse_target_params('sss','ddd')
