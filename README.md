# telegraf-avamar
Script that will query the avamar mcbd and optionally format a summary for influxdb. 

Usage:

dump_report.py -d DB -u USER -H HOST -P PORT -p PWD -C IDENT -D DAYS -i INFLUX

- H : This is the Avamar ip address. 
- p :  The Avamar viewuser password
- C : Identity for the Avamar data. In multi avamar environments, you want each Avamar to be identified by this IDENT tag
- D : The number of days to query for the report. Default is 1, so you will get a report for the last 24 hours. 
- i : True/False for influx format (default true). 


Using influxdb's exec input, you can redict the output remotely to a collector. The agent runs every 12 hours.

```
[agent]
interval = "12h"
[[inputs.exec]]
  commands = ["/opt/backup_check/dump_report.py -H 192.168.50.19 -p $viewuserpass -C NJDC01 -i True -D 1"]
  data_format = "influx"
[[outputs.influxdb]]
  url = "https://myinfluxcollector.com:8086"
  database = "telegraf_northeast_backups"
  username = "telegraf_node123"
  password = "tzuMbbdzSAMPLEGOMzSAMPLEyi1"
  insecure_skip_verify=true
```
You can then use Grafana to visualize all your data. 
