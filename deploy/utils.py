#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import pexpect
import re
IP_regex=r'((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))'
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
    print svn_cmd
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
    res=os.system('grep " Syntax" /tmp/.svn_32197')
    if res==0:
	return False,u'SVN格式错误!'
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



if __name__=='__main__':
    print check_svn_validated(u'root',u'wuyang',u'svn://192.168.1.1/huiyiding')
