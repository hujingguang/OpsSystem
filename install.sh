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

rpm -qa|grep epel &>/dev/null 
if [ $? != 0 ]
then
    echo 'begin install epel repo..............'
wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm &>/dev/null \
&& rpm -ih ./epel-release-latest-6.noarch.rpm &>/dev/null \
&& rm -rf ./epel-release-latest-6.noarch.rpm
    echo 'is ok ...............................'
fi

#install python2.7

install_python2_7(){
    version=`python --version`
    echo $version |grep '2.7' &>/dev/null
    if [ $? != 0 ]
    then 
	echo 'begin install python2.7 .........................'
	yum install xz gcc -y &>/dev/null
	wget https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tar.xz &>/dev/null
	tar -xf Python-2.7.11.tar.xz && \
	cd Python-2.7.11 && \
	./configure --prefix=/usr/local/python2.7 &>/dev/null && \
	make &>/dev/null && make install &>/dev/null
	if [ $? != 0 ]
	then
	    echo 'install python2.7 failed ! '
	    exit 1
	fi
	echo 'install python2.7 is ok .........................'
	mv /usr/bin/python /usr/bin/python.bak 
	ln -s /usr/local/python2.7/bin/python /usr/bin/python
	new_version=`python --version`
        echo $new_version |grep '2.7' &>/dev/null
	sed -i 's#\#!/usr/bin/python#\#!/usr/bin/python2.6#g' /usr/bin/yum
	rm -rf ./Python-2.7.11*
    fi
}

install_python_module(){
    echo 'install setuptool and pip tools'
    setuptools_url='https://pypi.python.org/packages/f0/32/99ead2d74cba43bd59aa213e9c6e8212a9d3ed07805bb66b8bf9affbb541/setuptools-21.1.0.tar.gz#md5=8fd8bdbf05c286063e1052be20a5bd98'
    pip_url='https://pypi.python.org/packages/ce/15/ee1f9a84365423e9ef03d0f9ed0eba2fb00ac1fffdd33e7b52aea914d0f8/pip-8.0.2.tar.gz#md5=3a73c4188f8dbad6a1e6f6d44d117eeb'
    wget $setuptools_url &>/dev/null && wget $pip_url &>/dev/null
    tar -zxf setuptools-21.1.0.tar.gz && \
    tar -zxf pip-8.0.2.tar.gz && \
    cd setuptools-21.1.0 && \
    /usr/local/python2.7/bin/python setup.py install &>/dev/null
    if [ $? != 0 ]
    then 
	echo 'install setuptools failed'
	exit 1
    fi
    cd ../pip-8.0.2 && /usr/local/python2.7/bin/python setup.py install &>/dev/null
    if [ $? != 0 ]
    then
	echo 'install pip tool failed '
	exit 1
    fi
    echo 'install setuptool and pip tools is ok .............................'
    echo 
    echo 'install pexpect , salt , django ,MySQL-python'
    /usr/local/python2.7/bin/pip install django
    /usr/local/python2.7/bin/pip install salt
    /usr/local/python2.7/bin/pip install pexpect
    /usr/local/python2.7/bin/pip install MySQL-python
    /usr/local/python2.7/bin/pip install pyaml
    /usr/local/python2.7/bin/pip install tornado
    /usr/local/python2.7/bin/pip install zmq
    /usr/local/python2.7/bin/pip install msgpack-python
    yum install salt salt-master  mysql-devel mysql-server mysql MySQL-python -y &>/dev/null
    mysqlib=`find / -name 'libmysqlclient.so.18'`
    if [ ! -e /usr/lib64/libmysqlclient.so.18 ]
    then
    ln -s $mysqlib /usr/lib64/libmysqlclient.so.18
    fi
    echo 'install pexpect salt django MySQL-pytho is ok ....................................'
}

install_salt_master(){
    echo 'install git subversion ...............................'
     yum install salt-master git subversion -y &>/dev/null
     if [ $? != 0 ]
     then
	 echo 'install salt-master failed '
	 exit 1
     fi
     echo 'install git subversion is ok ...........................'
     service salt-master start &>/dev/null
}

copy_sls_files(){
    if [ ! -e /srv/salt ]
    then
	mkdir -p /srv/salt
    fi
    cur=`pwd`
    \cp -a $cur/sls/* /srv/salt/ &>/dev/null
}


main(){
copy_sls_files
install_python2_7
install_python_module
install_salt_master
}

echo 'begin to start.......'
main
echo 'please install mysql server and start '
echo 'please vim ./ops_system/setting.py  and set database '
echo 'run: python manage.py test '
echo 'run: python manage.py makemigrations  '
echo 'run: python manage.py migrate'
echo 'run: python manage.py createsuperuser'

