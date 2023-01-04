import paramiko
import getpass
import subprocess
import time
import json
import psutil
import os
import threading
import mariadb
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from config import config

class_config = config.config()

conn = mariadb.connect(
        user=class_config.mariadb['user'],
        password=class_config.mariadb['password'],
        host=class_config.mariadb['host'],
        port=class_config.mariadb['port'],
        database=class_config.mariadb['database']
    )

cur = conn.cursor()

sql_gpu_info = "SELECT * FROM gpu_info"
sql_server_info = "SELECT * FROM server_info"
# Use the read_sql function to load the data into a DataFrame
df_gpu_info = pd.read_sql(sql_gpu_info, conn)
df_server_info = pd.read_sql(sql_server_info, conn)

print(df_gpu_info)
print(df_server_info)

list_server = class_config.list_server

DEFAULT_ATTRIBUTES = (
        'index',
        'uuid',
        'name',
        'timestamp',
        'memory.total',
        'memory.free',
        'memory.used',
        'utilization.gpu',
        'utilization.memory',
        'temperature.gpu',
        'temperature.memory'
    )

def get_gpu_info(cli, nvidia_smi_path='nvidia-smi', keys=DEFAULT_ATTRIBUTES, no_units=True):
    nu_opt = '' if not no_units else ',nounits'
    cmd = '%s --query-gpu=%s --format=csv,noheader%s' % (nvidia_smi_path, ','.join(keys), nu_opt)
    # output = subprocess.check_output(cmd, shell=True)
    stdin, output, stderr = cli.exec_command(cmd)
    lines = output.readlines()
    lines = [ line.strip() for line in lines if line.strip() != '' ]

    return [ { k: v for k, v in zip(keys, line.split(', ')) } for line in lines ]

def _check_usage_of_cpu_and_memory(cli):
        
        pid = os.getpid()
        py  = psutil.Process(pid)
        
        # cpu_usage   = os.popen("ps aux | grep " + str(pid) + " | grep -v grep | awk '{print $3}'").read()
        # cpu_usage   = cpu_usage.replace("\n","")
        cmd = 'top -b -n1'
                
        stdin, stdout, stderr = cli.exec_command(cmd)
        output = stdout.read().decode('utf-8')
        for line in output.split('\n'):
            if 'Cpu(s)' in line:
                cpu_usage = line.split(',')[0].split(':')[1].strip()
                print(f'CPU usage: {cpu_usage}')

        # cpu_usage   = cpu_usage.replace("\n","")
        memory_usage  = round(py.memory_info()[0] /2.**30, 2)
        
        print("cpu usage\t\t:", cpu_usage, "%")
        print("memory usage\t\t:", memory_usage, "%")
        
        dict_server_cpu_ram = {
            "cpu" : f"cpu usage : {cpu_usage}%",
            "ram" : f"ram usage : {memory_usage}%"
        }

        return dict_server_cpu_ram  

def check_server(server):
    cur = conn.cursor()
    
    while True:
        dict_server = {}
        gpu_running = False
        dict_server['server_connect'] = {}
        dict_server['gpu_detail'] = {}
        dict_server['gpu_abstarct'] = {}
        dict_server['server_cpu_ram'] = {}

        for server in [server]:
            cli = paramiko.SSHClient()
            cli.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            try:
                cli.connect(f"192.168.2.{server}", username="bseo", password="105wkd4dlaak")
                dict_server['server_connect'][server] = 'connect'
                print(f'{server} connect')
            except:
                dict_server['server_connect'][server] = 'disconnected'
                print(f'{server} discoonected')
                continue
            stdin, stdout, stderr = cli.exec_command('nvidia-smi')
            lines = stdout.readlines()

            list_str = lines
            index_for_uppergpuid = 0

            for idx, i in enumerate(list_str):
                if '=============================================================================' in i:
                    index_for_uppergpuid = idx
            list_gpu_line = list_str[index_for_uppergpuid+1:-1]
            dict_gpu = {}
            dict_gpu['gpu id'] = {}

            # GPU사용중일 때와 아닐 때 구분
            if 'No' in list_gpu_line[0] and 'running' in list_gpu_line[0] and 'processes' in list_gpu_line[0] and 'found' in list_gpu_line[0]:
                gpu_running = False
            else:
                gpu_running = True

            if gpu_running:
                for idx, gpu_line in enumerate(list_gpu_line):
                    list_gpu_line_ele = gpu_line.split(' ')
                    while '' in list_gpu_line_ele:
                        list_gpu_line_ele.remove('')
                    
                    list_gpu_line_ele = list_gpu_line_ele[1:-1]        
                    # print(list_gpu_line_ele)    

                    if  list_gpu_line_ele[0] not in dict_gpu['gpu id']:
                        dict_gpu['gpu id'][list_gpu_line_ele[0]] = []
                        dict_gpu['gpu id'][list_gpu_line_ele[0]].append(
                                                {'GPU ID' : list_gpu_line_ele[0],
                                                'GIID' : list_gpu_line_ele[1],
                                                'CIID' : list_gpu_line_ele[2],
                                                'PID' : list_gpu_line_ele[3],
                                                'Type' : list_gpu_line_ele[4],
                                                'Process name' : list_gpu_line_ele[5],
                                                'GPU Memory Usage' : list_gpu_line_ele[6]})
                    else:
                        dict_gpu['gpu id'][list_gpu_line_ele[0]].append(
                                                {'GPU ID' : list_gpu_line_ele[0],
                                                'GIID' : list_gpu_line_ele[1],
                                                'CIID' : list_gpu_line_ele[2],
                                                'PID' : list_gpu_line_ele[3],
                                                'Type' : list_gpu_line_ele[4],
                                                'Process name' : list_gpu_line_ele[5],
                                                'GPU Memory Usage' : list_gpu_line_ele[6]})

                dict_server['gpu_detail'][server] = dict_gpu
                dict_server['gpu_abstarct'][server] = get_gpu_info(cli)
            else:
                dict_server['gpu_detail'][server] = 'not use'

            server_cpu_ram = _check_usage_of_cpu_and_memory(cli)

            dict_server['server_cpu_ram'][server] = server_cpu_ram
            
            # with open(f'dict_{server}_server.json','w',encoding = 'utf-8') as f:
            #     json.dump(dict_server, f, indent=2)    

            # cli.close()

            # ssh를 통해 받아온 신호처리
            # df_server = df_gpu_info[df_gpu_info['server_name'] == server]

            if dict_server['server_connect'][server] == 'connect':
                if dict_server['gpu_detail'][server] == 'not use':
                    print(df_gpu_info[(df_gpu_info['server_name'] == '221') & (df_gpu_info['gpu_id'] == '13')])
                    query = "INSERT INTO use_or_not (server_name, gpu_id, gpu_use, server_connect) VALUES (%s, %s, %s, %s)"
                    values = (server_name, gpu_id, gpu_use, server_connect)
                    cur.execute(query, values)
                    conn.commit()
                else:
                    2
            else:
                query = "UPDATE gpu_info SET server_use = %s WHERE server_name = %s"
                values = ('not use', server)
                cur.execute(query, values)
                conn.commit()
                continue

            time.sleep(1)

threads = []
for server in list_server:
    print(server)
    thread = threading.Thread(target=check_server, args=(server,))
    threads.append(thread)
    thread.start()

# Wait for the threads to finish
for thread in threads:
    thread.join()

