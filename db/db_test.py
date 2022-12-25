import mariadb

conn = mariadb.connect(
        user="root",
        password="105wkd4dlaak",
        host="127.0.0.1",
        port=3316,
        database="server_monitoring_system"
    )

cur = conn.cursor()

query = "INSERT INTO server_info (server_name, ip, rack_number) VALUES (%s, %s, %s)"
values = ('201', '192.168.2.201', '2')
cur.execute(query, values)
conn.commit()
conn.close()
