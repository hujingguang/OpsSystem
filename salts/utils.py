import urllib,urllib2,json

try:
    from salt.client import LocalClient
    from salt.wheel import Wheel
    from salt.config import master_config
except:
    print 'please install salt!!!   commands: pip install salt '
    exit(1)

class SaltApiByWeb(object):
    def __init__(self,url,user,password):
	self.headers={'Accept':'application/json'}
	self.auth_params={'username':user,'password':password,'eauth':'pam'}
	self.url=url.rstrip('/')
	self.user=user
	self.password=password
        self.token=self.get_token_id()
	self.headers['X-Auth-Token']=self.token

    def get_token_id(self):
	body=urllib.urlencode(self.auth_params)
	request=urllib2.Request(self.url+'/login',body,self.headers)
	try:
	    response=urllib2.urlopen(request)
	except Exception as e:
	    print 'Error: %s ' %e
            exit(1)
        result=json.load(response)
	return result['return'][0]['token']
    def get_minion_info(self,pre):
	self.auth_params.update({'tgt':'*','fun':'key.list_all','client':'local'})
	body=urllib.urlencode(self.auth_params);
	print self.auth_params
	request=urllib2.Request(self.url+pre,body,self.headers)
	response=urllib2.urlopen(request)
	j=json.load(response)
        print j



class SaltApiByLocal(object):
    def __init__(self,main_config):
	opts=master_config(main_config)
	self.wheel=Wheel(opts)
	self.client=LocalClient()
	self.connected_minions_list=self.wheel.call_func('minions.connected')
	self.key_dict=self.wheel.call_func('key.list_all')
	self.total=len(self.key_dict['minions'])+len(self.key_dict['minions_pre'])+len(self.key_dict['minions_denied'])+len(self.key_dict['minions_rejected'])
    def get_minions_key_status(self):
	reject=len(self.key_dict['minions_rejected'])
	unaccept=len(self.key_dict['minions_pre'])
	accept=len(self.key_dict['minions'])
	return [accept,reject,unaccept]
    def get_minions_status(self):
        return [self.total,len(self.connected_minions_list),self.total-len(self.connected_minions_list)]



if __name__=='__main__':
    #salt=SaltApi('http://10.117.74.247:8080','salt','hoover123')
    #salt.get_minion_info('/run')
    local=SaltApiByLocal('/etc/salt/master')
    print local.get_minions_status(),local.get_minions_key_status()
