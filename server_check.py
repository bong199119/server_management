import os
import os.path
import sys
import subprocess
import time
# import mysql.connector # apt-get install python-mysql.connector
import json
import pprint
import psutil


# time.sleep(1)
# fail, output = subprocess.getstatusoutput("nvidia-smi")
# str_ = ''
# list_str = []
# index_for_uppergpuid = 0
# for idx, ele in enumerate(output):
#     str_ += ele
#     if ele=='\n':
#         # print(str_)
#         # print('1')
#         list_str.append(str_)
#         str_ = ''

# # with open('test.txt', 'w', encoding = 'utf-8') as f:
# #     for i in list_str:
# #         f.write(i)
# # f.close()

# for idx, i in enumerate(list_str):
#     if '=============================================================================' in i:
#         index_for_uppergpuid = idx
# list_gpu_line = list_str[index_for_uppergpuid+1:]
# dict_gpu = {}
# dict_gpu['gpu id'] = {}
# for idx, gpu_line in enumerate(list_gpu_line):
#     list_gpu_line_ele = gpu_line.split(' ')
#     while '' in list_gpu_line_ele:
#         list_gpu_line_ele.remove('')
    
#     list_gpu_line_ele = list_gpu_line_ele[1:-1]
#     if  list_gpu_line_ele[0] not in dict_gpu['gpu id']:
#         dict_gpu['gpu id'][list_gpu_line_ele[0]] = []
#         dict_gpu['gpu id'][list_gpu_line_ele[0]].append(
#                                 {'GPU ID' : list_gpu_line_ele[0],
#                                 'GIID' : list_gpu_line_ele[1],
#                                 'CIID' : list_gpu_line_ele[2],
#                                 'PID' : list_gpu_line_ele[3],
#                                 'Type' : list_gpu_line_ele[4],
#                                 'Process name' : list_gpu_line_ele[5],
#                                 'GPU Memory Usage' : list_gpu_line_ele[6]})
#     else:
#         dict_gpu['gpu id'][list_gpu_line_ele[0]].append(
#                                 {'GPU ID' : list_gpu_line_ele[0],
#                                 'GIID' : list_gpu_line_ele[1],
#                                 'CIID' : list_gpu_line_ele[2],
#                                 'PID' : list_gpu_line_ele[3],
#                                 'Type' : list_gpu_line_ele[4],
#                                 'Process name' : list_gpu_line_ele[5],
#                                 'GPU Memory Usage' : list_gpu_line_ele[6]})



# print(dict_gpu)
# print(list_str[index_for_uppergpuid+1:][0].split(' '))

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

def get_gpu_info(nvidia_smi_path='nvidia-smi', keys=DEFAULT_ATTRIBUTES, no_units=True):
    nu_opt = '' if not no_units else ',nounits'
    cmd = '%s --query-gpu=%s --format=csv,noheader%s' % (nvidia_smi_path, ','.join(keys), nu_opt)
    output = subprocess.check_output(cmd, shell=True)
    lines = output.decode().split('\n')
    lines = [ line.strip() for line in lines if line.strip() != '' ]

    return [ { k: v for k, v in zip(keys, line.split(', ')) } for line in lines ]



pprint.pprint(get_gpu_info()) 



# def _check_usage_of_cpu_and_memory():
    
#     pid = os.getpid()
#     py  = psutil.Process(pid)
    
#     cpu_usage   = os.popen("ps aux | grep " + str(pid) + " | grep -v grep | awk '{print $3}'").read()
#     cpu_usage   = cpu_usage.replace("\n","")
    
#     memory_usage  = round(py.memory_info()[0] /2.**30, 2)
    
#     print("cpu usage\t\t:", cpu_usage, "%")
#     print("memory usage\t\t:", memory_usage, "%")
    
#     dict_server_cpu_ram = {
#         "cpu" : f"cpu usage : {cpu_usage}%",
#         "ram" : f"ram usage : {memory_usage}%"
#     }

#     return dict_server_cpu_ram


# _check_usage_of_cpu_and_memory()
