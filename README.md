# OpsSystem
ops plateform


#这是一个运维平台，使用bootstrap 和django 框架进行开发。目前只实现了项目管理模块，能发布Git和SVN代码库的php工程。

部署步骤，  

1 ：安装python2.7版本，django1.9框架  pexpect python模块，svn工具  git工具

2： pip install django  && pip install pexpect && yum install git subversion -y

3: 进入工程根目录，配置好mysql数据库，执行python manage.py test 测试数据库连接

4： 初始化数据库表，python manage.py migrate

5:  创建一个管理员账号, python manage.py createsuperuser ,（在该平台里，只有管理员才能发布工程到正式环境）

6： 第一次发布代码，需要初始化发布记录，直接在表ops_deploy_info 插入一条发布记录,版本号根据自己项目而定，发布到相应的环境需要初始换相应的target字段：如测试环境target为test,预生产环境为pre,正式环境target字段为online.
7： 如果发布到正式环境，需配置ssh秘钥登陆，发布密码为管理员密码。

8： 运行平台 python manage.py runserver 0.0.0.0:80
