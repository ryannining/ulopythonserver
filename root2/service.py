<!
session_start()
ses=session
sdb=sqlite3.connect('database.sdb')
cur=sdb.cursor()
def query(sql):
  cur.execute(sql)
  return cur.fetchall()
def xquery(sql):
  put(sql)
  return query(sql)
def fillcombo(sql):
  print "fillcombo"
  cur.execute(sql)
  for row in cur:
    @<option value="$(row[0])">$(row[1])</option>
if form.call=='loadverifierdata':
  data=query("select data from auditsvlk where ver='$(form.verifier)' and idauditmain=$(form.idauditmain)")
  if data:put(data[0][0])    
if form.call=='saveverifierdata':
  put('OK :')
  query("delete from auditsvlk where ver='$(form.verifier)' and idauditmain=$(session.idauditmain)")
  form.data=form.data.replace('\'','\\''');
  query("insert into auditsvlk(ver,idauditmain,prinsip,data) values('$(form.verifier)','$(form.idauditmain)','$(form.prinsip)','$(form.data)')")
!>
<FINALIZE>
try:
  sdb.commit()
  sdb.close()
except:pass