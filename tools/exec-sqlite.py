from sys import argv
from sqlite3 import connect

conn = connect(argv[1])
cur = conn.cursor()
res = cur.execute(argv[2])
print(res.fetchall())
print(res.rowcount)
conn.commit()
conn.close()
