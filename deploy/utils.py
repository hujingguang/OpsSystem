#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import pexpect
import random
import re
import time
import commands
from django.contrib.auth import authenticate
from models import RepoModel,DeployInfoModel
from datetime import datetime
IP_regex=r'((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))'
RSYNC_LOG_FILE='/tmp/ops_rsync.log'
REVISION=''
def check_svn_validated(user,password,url):
    global IP_regex
    ip_match=re.search(IP_regex,url)
    if not ip_match:
	return False,u'无效的IP地址!!'
    svn_ip=ip_match.group()
    check_network_cmd='ping -c 2 -i 1 -w 4 %s &>/dev/null' %svn_ip
    ping_result=os.system(check_network_cmd)
    if ping_result != 0:
	return False,u'无法连接指定SVN服务器'
    svn_cmd=''' svn info --non-interactive  --username="%s" --password="%s" %s &>/tmp/.svn_32197''' %(user,password,url)
    result=os.system(svn_cmd)
    if result==0:
	return True,u'ok'
    res=os.system('grep URL /tmp/.svn_32197')
    if res==0:
        return False,u'无效的svn URL地址'
    res=os.system('grep Password /tmp/.svn_32197')
    if res==0:
	return False,u'错误的svn用户密码'
    res=os.system('grep "timed out" /tmp/.svn_32197')
    if res==0:
	return False,u'检车URL超时,请确认地址是否有效！'
    res=os.system('grep "refused" /tmp/.svn_32197')
    if res==0:
	return False,u'拒绝连接该svn地址！'
    res=os.system('grep "Username" /tmp/.svn_32197')
    if res==0:
	return False,u'无效的用户名'
    res=os.system('grep "Unknown hostname" /tmp/.svn_32197')
    if res==0:
	return False,u'错误的svn地址'
    res=os.system('grep "Syntax" /tmp/.svn_32197')
    if res==0:
	return False,u'SVN格式错误!'
    res=os.system('grep "repository" /tmp/.svn_32197')
    if res == 0:
	return False,u'不存在该SVN 库'

def check_git_validated(url):
    global IP_regex
    if not re.search(IP_regex,url):
	return False,u'无效的IP地址 ！！'
    ip=re.search(IP_regex,url).group()
    ch=pexpect.spawn('ssh root@%s' %ip)
    res=ch.expect(['yes',pexpect.EOF,pexpect.TIMEOUT],timeout=4)
    if res==0:
	ch.sendline('yes')
	ch.close(force=True)
    cmd=r'git clone %s' %url
    ch=pexpect.spawn(cmd)
    res=ch.expect(['done','fatal',pexpect.EOF,pexpect.TIMEOUT],timeout=8)
    if res == 0:
	return True,u'ok'
    elif res == 1:
	return False,u'Git地址不正确或无效,示例: git@192.168.16.23:repo_name'
    else:
	return False,u'检测库地址超时,请确认IP是否正确,且需配置秘钥连接'

def check_ip_reachable(ip):
    if ip is None: 
	return False
    cmd='ping -c 2 -w 2 -i 1 %s &>/dev/null' %ip
    res=os.system(cmd)
    if res != 0:
	return False
    return True
    
def check_ssh_passwd(passwd,ip):
        ch=pexpect.spawn('ssh root@%s' %ip)
	res=ch.expect(['yes','assword',pexpect.EOF,pexpect.TIMEOUT],timeout=120)
	if res == 0:
	    ch.sendline('yes')
	    rs=ch.expect(['assword',pexpect.EOF,pexpect.TIMEOUT],timeout=120)
	    ch.sendline(passwd)
	    rsz=ch.expect(['assword','#',pexpect.EOF,pexpect.TIMEOUT],timeout=120)
	    if rsz == 0:
		ch.close(force=True)
	    if rsz == 1:
		ch.close(force=True)
		return True
	if res == 1:
	    ch.sendline(passwd)
	    rsz=ch.expect(['assword','#',pexpect.EOF,pexpect.TIMEOUT],timeout=120)
            if rsz == 0:
		ch.close(force=True)
	    if rsz == 1:
		ch.close(force=True)
		return True
        return False

def deploy_git_code(repo_name,
	repo_address,
	checkout_dir,
	exclude_dir,
	revision,
	ip,
	target,
	wwwDir,
	deploy_password,
	deploy_person):
    global REVISION
    log_file='/tmp/.'+str(random.randint(100,100000))+'.log'
    if not checkout_dir.startswith('/'):
	checkout_dir='/'+checkout_dir
    if not checkout_dir.endswith('/'):
	checkout_dir=checkout_dir+'/'
    checkout_code_parent_dir=checkout_dir+repo_name+'_'+target
    if not os.path.exists(checkout_code_parent_dir):
	os.system('mkdir -p %s' %checkout_code_parent_dir)
    if repo_address.strip(' ').endswith('.git'):
	n=repo_address.rfind('/')
	code_dir=repo_address[n+1:].replace('.git','')
    else:
	n=repo_address.rfind(':')
	if n==-1:
	    return False,u'错误的Git地址',None
	code_dir=repo_address[n+1:]
    if not os.path.exists(checkout_code_parent_dir+'/'+code_dir+'/.git'):
	cmd_init_project=''' cd %s && git clone %s ''' %(checkout_code_parent_dir,repo_address)
	logfunc(log_file,'INFO','init cmd : '+cmd_init_project)
	res=os.system(cmd_init_project)
	logfunc(log_file,'INFO','cmd run return code :'+str(res))
	if res !=0 :
	    return False,u'初始化Git库失败！！',log_file
    else:
	cmd_pull_project=''' cd %s/%s && git pull origin master ''' %(checkout_code_parent_dir,code_dir)
	logfunc(log_file,'INFO','pull lastest code cmd :'+cmd_pull_project)
	res=os.system(cmd_pull_project)
	logfunc(log_file,'INFO','cmd run return code: '+str(res))
	if res != 0:
	    return False,u'拉取最新代码失败！！',log_file
    if not os.path.exists(checkout_code_parent_dir+'/'+code_dir+'/.git/refs/heads'):
	logfunc(log_file,'Error','the revision file do not exists! :%s'+checkout_code_parent_dir+'/'+code_dir+'/.git/refs/heads')
	return False,u'无法获取最新版本号',log_file
    cmd_get_lastest_version='cat %s/%s/.git/refs/heads/master' %(checkout_code_parent_dir,code_dir)
    lastest_revision=commands.getstatusoutput(cmd_get_lastest_version)[1][:10]
    if lastest_revision==revision:
	return False,u'没有可更新的代码',None
    diff_file='/tmp/.'+str(random.randint(10000,1000000))+'.log'
    cmd_get_diff_file=''' cd %s/%s && git diff --name-status %s %s|sed "s/^\s\+//g" >%s ''' %(checkout_code_parent_dir,code_dir,revision,lastest_revision,diff_file)
    logfunc(log_file,'INFO','get diff file cmd: '+cmd_get_diff_file)
    cmd_res=os.system(cmd_get_diff_file)
    logfunc(log_file,'INFO','cmd run return code: '+str(cmd_res))
    if cmd_res != 0:
        return False,u'获取更新文件失败！！！',log_file
    cmd_dealwith_diff_file=''' cat %s |egrep -v '^$' |awk '/^[^D]/{print $2}' > %s.log ''' %(diff_file,diff_file)
    logfunc(log_file,'INFO','get dealwith file cmd: '+cmd_dealwith_diff_file)
    cmd_res=os.system(cmd_dealwith_diff_file)
    logfunc(log_file,'INFO','cmd run return code: '+str(cmd_res))
    if cmd_res != 0:
	return False,u'处理更新文件失败！',log_file
    f=open(diff_file,'r')
    diff_file_list=f.readlines()
    logfunc(log_file,'INFO','以下文件将上传到服务器: ')
    for line in diff_file_list:
	logfunc(log_file,'file',line)
    code,log=commands.getstatusoutput('cat %s' %diff_file)
    REVISION=lastest_revision
    if target == 'test' or target == 'pre':
	res,mess,log_file=upload_code_with_password(checkout_code_parent_dir+'/'+code_dir,
		deploy_password,
		wwwDir,
		ip[0],
		diff_file+'.log',
		exclude_dir,
		log_file)
	os.system('rm -f %s && rm -f %s.log' %(diff_file,diff_file))
	if res:
	    recode,m=insert_deploy_log(repo_name,
		    target,
		    lastest_revision,
		    datetime.now(),
		    log,
		    deploy_person.get_username())
	    return recode,m,log_file
	else:
	    return res,mess,log_file
    else:
	if not deploy_person.is_superuser:
	    return False,u'非管理员无法发布至正式环境！！！',None
	user=authenticate(username=deploy_person.get_username(),password=deploy_password)
	if user is not None:
	    res,mess,log_file=upload_code_with_no_password(checkout_code_parent_dir+'/'+code_dir,wwwDir,ip,diff_file+'.log',exclude_dir,log_file)
	    os.system('rm -f %s && rm -f %s.log' %(diff_file,diff_file))
	    if res:
		recode,m=insert_deploy_log(repo_name,
			target,
			lastest_revision,
			datetime.now(),
			log,
			deploy_person.get_username())
		return recode,m,log_file
	    else:
		return res,mess,log_file
	else:
	    return False,u'密码错误,请输入管理员密码',None


def deploy_svn_code(repo_name,
	user,
	password,
	repo_address,
	checkout_dir,
	exclude_dir,
	revision,
	ip,
	target,
	wwwDir,
	deploy_password,
	deploy_person):
    '''
    upload code to target host
    Args:
        repo_name: 定义的工程名
	user: svn用户名
	password: svn用户密码
        repo_address: 版本库地址,工程在代码库中的根目录地址
	exclude_dir: 排除的目录或文件
	revision: 上一次发布的版本号
	ip: 目标机器的IP地址
	target: 发布的环境,可选为 test, pre ,online
	wwwDir: 目标机器的网站跟目录路径
	deploy_password: 发布密码,发布至正式环境为管理员登陆密码，测试环境或预发布环境为机器root用户密码
	deploy_person: 发布用户
    Returns:
        返回一个三个元素的元组,第一个为布尔值,表示上传成功与否，第二个为发布返回信息，第三个为发布日志  
    '''
    global REVISION
    log_file='/tmp/.'+str(random.randint(100,100000))+'.log'
    if not checkout_dir.startswith('/'):
	checkout_dir='/'+checkout_dir
    if not checkout_dir.endswith('/'):
	checkout_dir=checkout_dir+'/'
    if repo_address.endswith('/'):
	n=repo_address.rfind('/')
	repo_address=repo_address[:n]
    checkout_code_parent_dir=checkout_dir+repo_name+'_'+target
    n=repo_address.rfind('/')
    code_dir=repo_address[n+1:]
    if not os.path.exists(checkout_code_parent_dir):
	os.system('mkdir -p %s' %checkout_code_parent_dir)
    svn_cmd_args=' --non-interactive --username="%s" --password="%s" %s ' %(user,password,repo_address)
    cmd_checkout_code=''' cd %s && svn checkout  --force %s && cd %s && svn cleanup ''' %(checkout_code_parent_dir,svn_cmd_args,code_dir)
    logfunc(log_file,'INFO','checkout out cmd: '+cmd_checkout_code)
    cmd_res=os.system(cmd_checkout_code)
    logfunc(log_file,'INFO','cmd run return code: '+str(cmd_res))
    if cmd_res != 0:
	return False,u'发布失败！！无法获取最新代码',log_file
    cmd_get_lastest_revision=''' svn info %s |grep Last|grep Rev |tr -s " "|awk '{print $NF}' ''' %svn_cmd_args
    logfunc(log_file,'INFO','get revision cmd: '+cmd_get_lastest_revision) 
    cmd_res,lastest_revision=commands.getstatusoutput(cmd_get_lastest_revision)
    logfunc(log_file,'INFO','cmd run return code: '+str(cmd_res))
    if cmd_res != 0:
	return False,u'获取版本号失败！！！',log_file
    if int(revision) == int(lastest_revision):
	return False,u'没有可更新的代码！！！',log_file
    if int(revision) > int(lastest_revision):
	return False,u'最新的版本号小于上次记录版本号！ 请检查数据库',log_file
    if int(revision) < int(lastest_revision):
	diff_file='/tmp/.'+str(random.randint(10000,1000000))+'.log'
	cmd_get_diff_file=''' cd %s/%s && svn diff -r%s:%s --summarize|sed "s/^\s\+//g" >%s ''' %(checkout_code_parent_dir,code_dir,revision,lastest_revision,diff_file)
        logfunc(log_file,'INFO','get diff file cmd: '+cmd_get_diff_file)
	cmd_res=os.system(cmd_get_diff_file)
	logfunc(log_file,'INFO','cmd run return code: '+str(cmd_res))
	if cmd_res != 0:
	    return False,u'获取更新文件失败！！！',log_file
        cmd_dealwith_diff_file=''' cat %s |egrep -v '^$' |awk '/^[^D]/{print $2}' > %s.log ''' %(diff_file,diff_file)
	logfunc(log_file,'INFO','get dealwith file cmd: '+cmd_dealwith_diff_file)
	cmd_res=os.system(cmd_dealwith_diff_file)
	logfunc(log_file,'INFO','cmd run return code: '+str(cmd_res))
	if cmd_res != 0:
	    return False,u'处理更新文件失败！',log_file
	f=open(diff_file,'r')
	diff_file_list=f.readlines()
	logfunc(log_file,'INFO','以下文件将上传到服务器: ')
	for line in diff_file_list:
	    logfunc(log_file,'file',line)
	code,log=commands.getstatusoutput('cat %s' %diff_file)
	REVISION=lastest_revision
        if target == 'test' or target == 'pre':
	    res,mess,log_file=upload_code_with_password(checkout_code_parent_dir+'/'+code_dir,
		    deploy_password,
		    wwwDir,
		    ip[0],
		    diff_file+'.log',
		    exclude_dir,log_file)
            os.system('rm -f %s && rm -f %s.log' %(diff_file,diff_file))
	    if res:
		recode,m=insert_deploy_log(repo_name,
			target,
			lastest_revision,
			datetime.now(),
			log,
			deploy_person.get_username())
		return recode,m,log_file
	    else:
		return res,mess,log_file
	else:
	    if not deploy_person.is_superuser:
		return False,u'非管理员无法发布至正式环境！！！',None
	    user=authenticate(username=deploy_person.get_username(),password=deploy_password)
	    if user is not None:
	        res,mess,log_file=upload_code_with_no_password(checkout_code_parent_dir+'/'+code_dir,wwwDir,ip,diff_file+'.log',exclude_dir,log_file)
		os.system('rm -f %s && rm -f %s.log' %(diff_file,diff_file))
		if res:
		    recode,m=insert_deploy_log(repo_name,target,
			    lastest_revision,datetime.now(),
			    log,
			    deploy_person.get_username())
		    return recode,m,log_file
		else:
		    return res,mess,log_file
	    else:
		return False,u'密码错误,请输入管理员密码',None


def upload_code_with_no_password(code_dir,
	wwwDir,
	ip,
	diff_file,
	exclude_dir,
	log_file):
    global RSYNC_LOG_FILE,REVISION
    if not os.path.exists(code_dir):
	return False,u'不存在源码目录: %s' %code_dir,log_file
    os.system('rm -rf /tmp/.tmp0001')
    exclude_args=deal_with_exclude(exclude_dir)
    for i in ip:
	ch=pexpect.spawn('ssh %s' %i)
	res=ch.expect(['password','#',pexpect.EOF,pexpect.TIMEOUT])
	if res != 1:
	    return False,u'IP: %s 没有配置秘钥连接！！请先配置ssh key 登陆再进行正式环境代码发布' %i,None
    failed=0
    for ii in ip:
	os.system('rm -rf /tmp/.up.log')
        cmd_upload=''' rsync -avlpP %s --files-from=%s %s %s:%s &>/tmp/.up.log && echo ok >/tmp/.tmp0001 || echo error >/tmp/.tmp0001 ''' %(exclude_args,diff_file,code_dir,ii,wwwDir)
        logfunc(log_file,'INFO','upload file cmd: '+cmd_upload)
	res=os.system(cmd_upload)
	logfunc(log_file,'INFO','upload cmd return code: '+str(res))
        logfunc(log_file,'INFO','-'*20)
        cmd_rsync_log='echo %s >> %s && cat /tmp/.up.log >> %s' %(REVISION,RSYNC_LOG_FILE,RSYNC_LOG_FILE)
        os.system(cmd_rsync_log)
        r,out=commands.getstatusoutput('cat /tmp/.up.log')
        logfunc(log_file,'INFO',out)
	if res != 0:
	    failed=failed+1
	    logfunc(log_file,'ERROR','upload file to IP: %s  Failed' %ii)
	else:
	    logfunc(log_file,'Success','upload file to IP: %s successed ' %ii)
    
    if failed==0:
	return True,'代码成功上传至所有的正式环境服务器组',log_file
    else:
	success=str(len(ip)-failed)
	failed=str(failed)
	return False,'代码发布失败,发布结果 成功台数： %s 失败台数：%s '  %(success,failed),log_file


def insert_deploy_log(repoName,target,revision,date,log,person):
    deployinfo=DeployInfoModel(repoName=repoName,
	    target=target,
	    revision=revision,
	    date=date,
	    log=log,
	    person=person)
    try:
	deployinfo.save()
    except:
	return False,u'插入发布日志失败'
    return True,u'发布成功'

	
def upload_code_with_password(code_dir,password,wwwDir,ip,diff_file,exclude_dir,log_file):
    global RSYNC_LOG_FILE,REVISION
    if not os.path.exists(code_dir):
	return False,u'不存在源代码目录: %s' %code_dir,log_file
    os.system('rm -rf /tmp/.tmp0001 && rm -rf /tmp/.up.log')
    exclude_args=deal_with_exclude(exclude_dir)
    cmd_upload=''' rsync -avlpP %s --files-from=%s %s %s:%s &>/tmp/.up.log && echo ok >/tmp/.tmp0001 || echo error >/tmp/.tmp0001 ''' %(exclude_args,diff_file,code_dir,ip,wwwDir)
    logfunc(log_file,'INFO','upload file cmd: '+cmd_upload)
    f=open('/tmp/.cmd_run.sh','w')
    f.write(cmd_upload)
    f.close()
    ch=pexpect.spawn('bash /tmp/.cmd_run.sh')
    res=ch.expect(['yes','assword',pexpect.TIMEOUT,pexpect.EOF],timeout=120)
    if res == 0:
	ch.sendline('yes')
	ch.expect(['assword',pexpect.TIMEOUT,pexpect.EOF],timeout=120)
	ch.sendline(password)
	loopfunc(ch.pid)
	ch.close(force=True)
    elif res == 1:
	ch.sendline(password)
	loopfunc(ch.pid)
	ch.close(force=True)
    else:
	return False,u'上传代码执行超时！！！',log_file
    is_ok=os.system('grep ok /tmp/.tmp0001 &>/dev/null')
    logfunc(log_file,'INFO','-'*20)
    cmd_rsync_log='echo %s >> %s && cat /tmp/.up.log >> %s' %(REVISION,RSYNC_LOG_FILE,RSYNC_LOG_FILE)
    os.system(cmd_rsync_log)
    r,out=commands.getstatusoutput('cat /tmp/.up.log')
    logfunc(log_file,'INFO',out)
    if is_ok == 0:
	return True,u'代码上传至服务器成功！',log_file
    else:
	return False,u'代码上传至服务器失败！',log_file


def logfunc(log_file,log_rate,info):
    f=open(log_file,'a')
    content=time.strftime('%Y-%m-%d %X',time.localtime())+'  ---'+log_rate+'---: '+info
    f.write(content+'\n')
    f.close()

def loopfunc(pid):
    cmd=''' pstree -p|grep python |grep '%s'|grep rsync ''' %pid
    while True:
	res=os.system(cmd)
	if res == 0:
	    time.sleep(2)
	    break
	time.sleep(3)

def deploy_project_func(repoName,password,target,deploy_person):
    repoinfo=RepoModel.objects.get(repoName=repoName)
    deployinfo=DeployInfoModel.objects.filter(repoName=repoName).filter(target=target).order_by('-date').first()
    if deployinfo is None:
	return False,u'没有发布记录！！请先初始化一条发布数据',None
    revision=deployinfo.revision
    ip=[]
    if target=='test':
	ip.append(repoinfo.testDeployIP)
    elif target=='pre':
	ip.append(repoinfo.preDeployIP)
    else:
	tmp_list=repoinfo.onlineDeployIP.split(' ')
	for i in tmp_list:
	    if i !='':
		ip.append(i)
    if repoinfo.repoType=='svn':
	#svn 发布方法
	return deploy_svn_code(repoinfo.repoName,
		repoinfo.repoUser,
		repoinfo.repoPassword,
		repoinfo.repoAddress,
		repoinfo.localCheckoutDir,
		repoinfo.excludeDir,
		revision,
		ip,
		target,
		repoinfo.wwwDir,
		password,
		deploy_person)
    else:
	if len(revision)<10:
	    return False,u'Git版本号字符串必须大于等于10位',None
	revision=revision[:10]
	#git 发布方法
	return deploy_git_code(repoinfo.repoName,
		repoinfo.repoAddress,
		repoinfo.localCheckoutDir,
		repoinfo.excludeDir,
		revision,
		ip,
		target,
		repoinfo.wwwDir,
		password,
		deploy_person)


	
'''
处理排除目录参数函数
Returns: --exclude={'.svn','.git'}
'''    

def deal_with_exclude(exclude_dir):
    exclude_dir=exclude_dir.replace(' ','')
    exclude_list=exclude_dir.strip(' ').split(';')
    exclude_args=' '
    for i in  exclude_list:
	if i == ' ':
	    exclude_list.remove(' ')  
        if i == '':
	    exclude_list.remove('')
	if i == '  ':
	    exclude_list.remove('  ')
    if len(exclude_list) == 0:
	    exclude_args=' '
    elif len(exclude_list) == 1:
	    exclude_args=''' --exclude "%s" ''' %exclude_list[0].strip(' ')
    else:
	exclude_files=''
	L=[]
	for f in exclude_list:
	    f='"'+f.strip(' ')+'",'
	    L.append(f)
        for j in L:
	    exclude_files=exclude_files+j
	n=exclude_files.rfind(',')
	exclude_files=exclude_files[:n]
	exclude_args=' --exclude={' +exclude_files+'} '
    return exclude_args


if __name__=='__main__':
    #print check_svn_validated(u'root',u'wuyang',u'svn://192.168.1.1/huiyiding')
    print deal_with_exclude('dd.log;          ;haha;  ;makelog;')
