import socket
import subprocess

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(('192.168.2.186', 9008))     


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

m_send = get_gpu_info()
print(m_send)

sock.send(m_send[0].encode())