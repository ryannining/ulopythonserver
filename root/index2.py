<?
start_time = time.time()
headers['Content-Type']='text/plain'
con=sqlite3.connect('pemilu.sdb')
cur = con.cursor()
cur.execute("select * from pemilu_tps order by s1a desc limit 1000")
for data in cur.fetchall():
    put("%22s %6s %3s %3s %3s\n" %(data[6],data[0],data[5],data[1],data[2]))
put("%f seconds" %(time.time() - start_time))
?>
