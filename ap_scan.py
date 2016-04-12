#!/usr/bin/python
__author__ = 'Clay'

from os.path import isfile
from sys import argv, path
path.insert(0, '/home/automation/scripts/clayScripts/resources/')
import claylib
import sqlite3

logfile = open('/home/automation/scripts/clayScripts/dev/ap_serial_gatherer/log', 'w')
oids = {'wing4':'1.3.6.1.4.1.388.11.2.2.1.1', 'wing5':'1.3.6.1.4.1.388.50.1.4.1.2.1.9.132.36.141.89.91.176'}
local_db_name = '/home/automation/scripts/clayScripts/websites/clay/resources/ap_scanner.db'

snmp = {'ACEL':{'pw':'<SNIPPED SNMPv2 PASS>', 'sn':'1.3.6.1.4.1.388.11.2.2.1.1', 'fw':'1.3.6.1.4.1.388.11.3.5.5.1.1.12.1'},
        'MidW':{'pw':'<SNIPPED SNMPv2 PASS>', 'sn':'1.3.6.1.4.1.388.11.2.2.1.1', 'fw':'1.3.6.1.4.1.388.11.3.5.5.1.1.12.1'},
        'Amfleet1':{'pw':'<SNIPPED SNMPv2 PASS>', 'sn':'1.3.6.1.4.1.388.11.2.2.1.1', 'fw':'1.3.6.1.4.1.388.11.3.5.5.1.1.12.1'},
        'Autotrain':{'pw':'<SNIPPED SNMPv2 PASS>', 'sn':'1.3.6.1.4.1.388.50.1.4.2.1.1.5', 'fw':'1.3.6.1.4.1.388.50.1.4.2.4.1.1.3'},
        'VIA':{'pw':'<SNIPPED SNMPv2 PASS>', 'sn':'1.3.6.1.4.1.388.11.2.2.1.1', 'fw':'1.3.6.1.4.1.388.11.3.5.5.1.1.12.1'},
        'OCEAN':{'pw':'<SNIPPED SNMPv2 PASS>', 'sn':'1.3.6.1.4.1.388.11.2.2.1.1', 'fw':'1.3.6.1.4.1.388.11.3.5.5.1.1.12.1'},
        'MLX':{'pw':'<SNIPPED SNMPv2 PASS>', 'sn':'1.3.6.1.4.1.388.50.1.4.2.1.1.5', 'fw':'1.3.6.1.4.1.388.50.1.4.2.4.1.1.3'},
        'Surfliner':{'pw':'<SNIPPED SNMPv2 PASS>', 'sn':'1.3.6.1.4.1.388.50.1.4.2.1.1.5', 'fw':'1.3.6.1.4.1.388.50.1.4.2.4.1.1.3'},
        'Capt_Corr':{'pw':'<SNIPPED SNMPv2 PASS>', 'sn':'1.3.6.1.4.1.388.50.1.4.2.1.1.5', 'fw':'1.3.6.1.4.1.388.50.1.4.2.4.1.1.3'},
        'AMT_CAS':{'pw':'<SNIPPED SNMPv2 PASS>', 'sn':'1.3.6.1.4.1.388.50.1.4.2.1.1.5', 'fw':'1.3.6.1.4.1.388.50.1.4.2.4.1.1.3'},
        'AMT_ORE':{'pw':'<SNIPPED SNMPv2 PASS>', 'sn':'1.3.6.1.4.1.388.50.1.4.2.1.1.5', 'fw':'1.3.6.1.4.1.388.50.1.4.2.4.1.1.3'},
        'SunRail':{'pw':'<SNIPPED SNMPv2 PASS>', 'sn':'1.3.6.1.4.1.388.11.2.2.1.1', 'fw':'1.3.6.1.4.1.388.11.3.5.5.1.1.12.1'}}

# translation from server hosts file fleet names to settings.db fleet names so that the web front end shows the correct fleets.
cust_translation = {'<SNIPPED /ETC/HOSTS FLEET PREFIX>':'<SNIPPED SETTINGS.DB LONG FLEET NAME>'}


def main():
    local_db = claylib.Sqlite_db(local_db_name)
    local_db.open()
    customer = '%s.<SNIPPED DB NAME>' % argv[1]
    customer_name = cust_translation[argv[1]]
    ap_list = claylib.query_nomad_db(customer, '<SNIPPED DB NAME>', '<SNIPPED USER>', '<SNIPPED PASSWORD>', 'select f.fleet_ref, c.carriage_ref, a.ip_address from dev_access_point as a join obj_carriage as c on a.carriage_id=c.carriage_id join obj_fleet as f on c.fleet_id=f.fleet_id;')
    print('Got %i APs' % len(ap_list))
    # Fleet, Car, IP
    for ap in ap_list:
        if (len(argv)==3):
            if (argv[2] not in ap[0]):
               continue
        try:
            response = claylib.local_command('ping -c 1 %s' % ap[2])
            for line in response:
                if '100% packet loss' in line:
                    print('%s - %s - OFFLINE' % (ap[0], ap[2]))
                    break
            else:
                output = ''
                cmd = 'snmpwalk -v2c -c %s %s %s' % (snmp[ap[0]]['pw'], ap[2], snmp[ap[0]]['sn'])
                serial = claylib.local_command(cmd)[0]
                if serial:
                    serial = serial.split(' = STRING: "')[1][:-1]
                    cmd = 'snmpwalk -v2c -c %s %s %s' % (snmp[ap[0]]['pw'], ap[2], snmp[ap[0]]['fw'])
                    fw = claylib.local_command(cmd)[0]
                    fw = fw[fw.find('STRING: "')+9:-1]
                    print('%s - %s - DONE' % (ap[0], ap[2]))
                    query = 'INSERT INTO access_points (cust, fleet, car, ip, sn, fw) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\');' % (cust_translation[argv[1]], ap[0], ap[1], ap[2], serial, fw)
                    local_db.query(query)
        except KeyboardInterrupt:
            exit()
        except KeyError:
            print('Unsupported fleet: %s' % ap[0])
            continue
        except sqlite3.OperationalError as err:
            print(err)
            print('FW:%s' %fw)
            print('SN:%s' % serial)
            continue

main()
