#!/bin/bash - 
#===============================================================================
#
#          FILE: install.sh
# 
#         USAGE: ./install.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: Only adapte Centos6.x   Python2.7  and x64 architecture
#        AUTHOR: Hoover
#  ORGANIZATION: 
#       CREATED: 05/19/2016 10:37
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

root_dir=`pwd`
if [ -e /etc/redhat-release ]
then
    cat /etc/redhat-release |egrep '6' &>/dev/null
    if [ $? != 0 ]
	then
	    echo '请基于centos6.x部署该项目'
            exit
    fi
else
    exit
fi
rpm -qa|grep epel &>/dev/null 
if [ $? != 0 ]
then
    echo 'begin install epel repo..............'
wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm &>/dev/null \
&& rpm -ih ./epel-release-latest-6.noarch.rpm &>/dev/null \
&& rm -rf ./epel-release-latest-6.noarch.rpm
    echo 'is ok ...............................'
fi

yum install https://repo.saltstack.com/yum/redhat/salt-repo-2015.8-3.el6.noarch.rpm -y &>/dev/null
yum install salt salt-master  salt-ssh salt-syndic salt-minion  -y &>/dev/null

#install python2.7

    version=`python --version`
    echo $version |grep '2.7' &>/dev/null
    if [ $? != 0 ]
    then 
	echo 'begin install python2.7 .........................'
	yum install xz gcc -y &>/dev/null
	cd ./soft && tar -xzf Python-2.7.10.tgz && \
	cd Python-2.7.10 && \
	./configure --prefix=/usr/local/ops/python2.7 &>/dev/null && \
	make &>/dev/null && make install &>/dev/null
	if [ $? != 0 ]
	then
	    echo 'install python2.7 failed ! '
	    exit 1
	fi
	echo 'install python2.7 is ok .........................'
	mv /usr/bin/python /usr/bin/python.bak 
	rm -rf /usr/bin/python
	ln -s /usr/local/ops/python2.7/bin/python /usr/bin/python
	sed -i 's#\#!/usr/bin/python#\#!/usr/bin/python2.6#g' /usr/bin/yum &>/dev/null
	cd ..
	rm -rf ./Python-2.7.11* &>/dev/null
    else
	cd ./soft
    fi
    echo 'install setuptool and pip tools'
    tar -zxf setuptools-18.4.tar.gz && \
    tar -zxf pip-7.1.2.tar.gz && \
    cd setuptools-18.4 && \
    /usr/local/ops/python2.7/bin/python setup.py install &>/dev/null
    if [ $? != 0 ]
    then 
	echo 'install setuptools failed'
	exit 1
    fi
    cd ../pip-7.1.2 && /usr/local/ops/python2.7/bin/python setup.py install &>/dev/null
    if [ $? != 0 ]
    then
	echo 'install pip tool failed '
	exit 1
    fi
    echo 'install setuptool and pip tools is ok .............................'
    echo 
    echo 'install pexpect , salt , django ,MySQL-python'
    if [ -e /usr/local/ops/python2.7/bin/pip ]
    then
    /usr/local/ops/python2.7/bin/pip install django==v1.9
    /usr/local/ops/python2.7/bin/pip install salt
    /usr/local/ops/python2.7/bin/pip install pexpect
    /usr/local/ops/python2.7/bin/pip install MySQL-python
    /usr/local/ops/python2.7/bin/pip install pyaml
    /usr/local/ops/python2.7/bin/pip install tornado
    /usr/local/ops/python2.7/bin/pip install zmq
    /usr/local/ops/python2.7/bin/pip install msgpack-python
    else
    pip install django==v1.9
    pip install salt
    pip install pexpect
    pip install pyaml
    pip install tornado
    pip install zmq
    pip install msgpack-python
    fi
    yum install salt salt-master git subversion mysql-devel mysql-server mysql MySQL-python -y &>/dev/null
    if [ ! -e /usr/lib64/libmysqlclient.so.18 ]
    then
    \cp ../libmysqlclient.so.18  /usr/lib64/
    fi
    /etc/init.d/salt-master start &>/dev/null
    echo 'install pexpect salt django MySQL-pytho is ok ....................................'
    cd ../..
    if [ ! -e /srv/salt ]
    then
	mkdir -p /srv/salt
    fi
    \cp -a ./sls/* /srv/salt/ &>/dev/null
    /usr/local/ops/python2.7/bin/pip install Mysql-python &>/dev/null

echo 'please install mysql server and start '
echo 'please vim ./ops_system/setting.py  and set database '
echo 'run: python manage.py test '
echo 'run: python manage.py makemigrations  '
echo 'run: python manage.py migrate'
echo 'run: python manage.py createsuperuser'

