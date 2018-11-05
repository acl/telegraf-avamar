#!/usr/bin/python

__license__ = "GPL"
__maintainer__ = "Abel Laura"
__email__ = "abel.laura@gmail.com"

""" MODULE IMPORTS """
import psycopg2
import string
import datetime
import time
import optparse
import sys
import os
import getpass

""" COMMAND LINE OPTION PARSING """
usage = "USAGE: %prog -d DB -u USER -H HOST -P PORT -p PWD -C CLI -D DAYS -i INFLUX"
parser = optparse.OptionParser(usage=usage)
parser.add_option('-d', action="store", default="mcdb", help="Avamar PG Database [default: %default]", type="string")
parser.add_option('-u', action="store", default="viewuser", help="PG User [default: %default]", type="string")
parser.add_option('-H', action="store", default="localhost", help="Avamar Server [default: %default]", type="string")
parser.add_option('-P', action="store", default="5555", help="PG Port [default: %default]", type="string")
parser.add_option('-p', action="store", default="viewuser1", help="PG Password [default: %default]", type="string")
parser.add_option('-C', action="store", default="ClinicIT", help="Client Name [default: %default]", type="string")
parser.add_option('-D', action="store", default="1", help="Days to query [default: %default Day(s)]", type="int")
parser.add_option('-i', action="store", default=False, help="Output Influx/Telegraf version [default: %default]")

options, args = parser.parse_args()

""" ARG COUNT CHECK """
if len(sys.argv[1:]) == 0:
    parser.print_help()
    sys.exit(1)

""" TEST DATABASE CONNECTION """
try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'"\
    % (options.d, options.u, options.H, options.p, options.P))
except psycopg2.DatabaseError, e:
    print e
    sys.exit(1)

""" MAIN FUNCTION """
def main():
    if (options.i):
        time_query="extract(epoch from completed_ts::timestamptz at time zone 'UTC') "
    else:
        time_query="completed_ts::timestamptz at time zone 'UTC' "

    query ="SELECT display_name, status_code, "\
    "(CASE WHEN status_code = 30000 THEN 'OK' "\
    "WHEN status_code = 30005 THEN 'WARN' "\
    "ELSE 'FAIL' END) as clinic_status, "\
    "plugin_name, status_code_summary, "\
    "completed_ts - started_ts as elapsed_time, "\
    "cast((bytes_scanned)/1024/1024/1024 as numeric(30,4)), "\
    "cast((bytes_new)/1024/1024/1024 as numeric(30,4)), "\
    + time_query + "FROM v_activities_2 WHERE "\
    "(completed_ts::timestamp at time zone 'UTC' > current_timestamp - interval '" + str(options.D) + " day') "\
    "and (v_activities_2.type like '%Backup%') Order By completed_ts;"

    try:
        cur = conn.cursor()
        cur.execute(query)
        for row in cur:
            calc_seconds = row[5].days * 1440 + row[5].seconds
            if (options.i):
                influxtime = int(row[8] * (10**9))
                influxserver_name = row[0].replace(" ", "\\ ")
                influxplugin_name = row[3].replace(" ", "\\ ")
                print('backup_logs,client=%s,server_name=%s,status_code=%s,clinic_status=%s,plugin_name=%s '
                'status_code_summary=\"%s\",elapsed_time=%s,gbprotected=%s,gbnew=%s %s' % \
                (options.C, influxserver_name, row[1], row[2], influxplugin_name, row[4], calc_seconds, row[6], row[7], influxtime))
            else:
                print('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % \
                (row[0], row[1], row[2], row[3], row[4], calc_seconds, row[6], row[7], row[8].isoformat()))
        cur.close()
        conn.close()
        sys.exit(0)
    except psycopg2.DatabaseError, e:
        print ( 'Error %s' % e )
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

