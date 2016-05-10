
/tmp/epel-release-latest-6.noarch.rpm:
  file.managed:
    - source: salt://epel/files/epel-release-latest-6.noarch.rpm
    - mode: 755
    - user: root

install_epel:
  cmd.run:
    - name: cd /tmp && rpm -ih epel-release-latest-6.noarch.rpm
    - required:
      - file: /tmp/epel-release-latest-6.noarch.rpm
    - unless: rpm -qa|grep epel
