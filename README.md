# OpsSystem
运维管理发布系统  Demo 地址:  http://demo.hujingguang.cn    username: guest    管理系统  password: 123123


#这是一个运维平台，使用bootstrap 和django 框架进行开发。目前实现了项目管理模块，发布Git和SVN代码库的php工程,回滚代码，以及集成Saltstack 进行应用批量部署模块和命令批量执行. 命令审计查询


前端模板下载地址： https://startbootstrap.com/


Docker Image 部署 


docker pull hooversa/ops_system:latest

docker  run --name ops_system --rm -p 80:81 -d hooversa/ops_system 

浏览器打开  127.0.0.1   （用户名/密码: admin/helloworld）





服务器部署步骤，  

1 ：安装python2.7版本，CentOS6.x, django1.9框架  pexpect python模块，svn工具  git工具 Saltstack 自动化工具

2： pip install django==v1.9.0  && pip install pexpect && yum install git subversion -y && pip install salt==v2015.8.13

3: 进入工程根目录，配置好mysql数据库，执行python manage.py test 测试数据库连接

4： 初始化数据库表，python manage.py makemigrations && python manage.py migrate

5:  创建一个管理员账号, python manage.py createsuperuser ,（在该平台里，只有管理员才能发布工程到正式环境）

6： 第一次发布代码，需要初始化发布记录，直接在表ops_deploy_info 插入一条发布记录,版本号根据自己项目而定，发布到相应的环境需要初始换相应的target字段：如测试环境target为test,预生产环境为pre,正式环境target字段为online.
7： 如果发布到正式环境，需配置ssh秘钥登陆，发布密码为管理员密码。发布到测试环境或预发布环境，密码为机器的root密码

8： 运行平台 python manage.py runserver 0.0.0.0:80

9:   如果要进行应用部署，请将项目根目录下的sls目录里面的所有文件拷贝至salt的file_root 下面，一般为/srv/salt 下面。如果要部署tomcat应用，请自行下载jdk源码包，放在/srv/salt/tomcat/files下面，并修改install.sls文件.

10: 要进行应用部署，需要安装minion客户端，并配置好master 和id  ,还有必须在grains 添加三个变量：group,area,usage。  这个三个变量信息会在主机信息中对应:组,地址,和用途三栏。否则刷新无法获取到主机信息


11: 命令审计模块需要在各个salt-minion端安装agent.py,该文件位于项目下tools文件夹中，在salt-master运行 master.py接受来自agent.py的数据。,master.py需要配置数据库连接信息。直接编辑文件添加即可.




git clone https://github.com/hujingguang/OpsSystem.git

cd OpsSystem && cat INSTALL


-----Demo 地址：

   http://demo.hujingguang.cn 

   username: guest

   password: 123123


#### Screenshots
-----------
登陆界面

![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/0.png)

Dashboard
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/1.png)

用户管理
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/15.png)

用户添加
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/16.png)

添加SVN版本库项目
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/2.png)

添加Git版本库项目
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/3.png)

发布工程
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/4.png)

代码回滚
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/13.png)

主机信息
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/5.png)

应用部署
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/6.png)

命令执行
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/7.png)

应用部署记录
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/8.png)

命令执行记录
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/9.png)

云资产信息
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/10.png)

文件下载
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/11.png)

命令审计
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/12.png)

集成脚本代码发布
![](https://github.com/hujingguang/OpsSystem/blob/master/screenshots/14.png)
