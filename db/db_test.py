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
# Close the connection to the database
conn.close()

# uuid = 'GPU-4264b029-1063-9fdf-4083-7b642bb3a0d2'
# gpu_id = '16'
# server_name = '221'
# gpu_name = 'NVIDIA RTX A6000'

# query = "INSERT INTO gpu_info (uuid, gpu_id, server_name, gpu_name) VALUES (%s, %s, %s, %s)"
# values = (uuid, gpu_id, server_name, gpu_name)
# cur.execute(query, values)
# conn.commit()
# conn.close()
