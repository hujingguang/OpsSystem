#!/bin/bash - 
#===============================================================================
#
#          FILE: create_user.sh
# 
#         USAGE: ./create_user.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2019/03/15 11:41
#      REVISION:  ---
#===============================================================================


mysql -uroot -p123123 -e " insert into ops.auth_user(password,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined) values('pbkdf2_sha256$24000$C3pV7OkipU4m$UH0KJBcA5klYUwO9M3ExZn7olt0L/PMPDUgwODIYlWw=',1,'admin','administrator','admin','admin@gmail.com',1,1,'2019-03-15 10:58:59');"
