include:
  - zabbix.install
  - zabbix.update_zbx_conf

start_zbx_agentd:
  cmd.run:
    - name: service zabbix_agentd start
    - unless: pstree|grep zabbix_agentd
