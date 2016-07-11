/etc/init.d/agent.py:
  file.managed:
    - source: salt://tools/files/agent.py
    - mode: 755

/tmp/psutil-4.3.0.tar.gz:
  file.managed:
    - source: salt://tools/files/psutil-4.3.0.tar.gz
          
install_gcc:
  cmd.run:
    - name: yum install python-devel gcc -y &>/dev/null


install_psutil:
  cmd.run:
    - name: cd /tmp  && tar -zxf psutil-4.3.0.tar.gz && cd psutil-4.3.0 && python setup.py install &>/dev/null
    - required:
      - file: /tmp/psutil-4.3.0.tar.gz

/etc/daemon.conf:
  file.managed:
    - source: salt://tools/files/daemon.conf
    - mode: 700

run:
  cmd.run:
    - name: /etc/init.d/agent.py  -d -s 72000 -m 10.117.74.247
    - unless: ps aux|grep python|grep agent.py|egrep -v 'grep'
