<!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.2//EN" "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile12.dtd"><html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en" id="bp-doc">
<head>
<title>Audit Lapangan
</title>
<script src="js/jquery-1.4.2.min.js"></script>
<script src="js/json2.js"></script>
<script>
jq=jQuery;
</script>
<!
fz='10px arial';
!>
<style>
 body {font:$(fz);  background:#fff;padding:0;margin:0;
}
 
 .wndbox {
  position:absolute;
  left:0;
  top:0;
  right:0;
  bottom:0;
  padding:10px;
  background:#fff;
  z-index:100;
 }
 .taskbar {
  position:absolute;
  bottom:0;
  right:0;
  margin-left:0;
  left:0;
  height:40px;
  background:#eee;
  padding:10px;
  z-index:0;
 }
 .taskbar .goback {
  border:0;
  width:32px;
  height:32px;
  background:url(img/go-previous.png);
  left:164px;
  position:absolute;
 }
 .taskbar .goexit {
  border:0;
  width:32px;
  height:32px;
  background:url(img/system-log-out.png);
  left:234px;
  position:absolute;
 }
 .taskbar .gohome {
  border:0;
  width:32px;
  height:32px;
  background:url(img/go-home.png);
  left:234px;
  position:absolute;
 }
 .taskbar .godata {
  border:0;
  width:32px;
  height:32px;
  background:url(img/edit-find.png);
  left:304px;
  position:absolute;
 }
 .alerter {
  border-radius:10px;
  border:1px solid #888;
  background:#a22;
  color:#fff;
  height:auto;
  left:20px;
  right:20px;
  top:auto;
  bottom:70px;
  margin-top:-150px;
  position:fixed;
  padding:10px;
  z-index:10000;
  box-shadow: 0px 1px 8px #000;
 }
 .hider {
  position:fixed;
  z-index:9000;
  background:#000;
  opacity:0.5;
  left:0;top:0;right:0;bottom:0;
 }
 .alerter p {
  border-radius:5px;
  font:$(fz);color:#fff;
  padding:5px;
  position:relative;
 }
 .alerter h1 {
  font:16pt arial;color:#fff;font-weight:bold;text-align:center;position:absolute;
  left:10px;top:0px;right:10px;
 }
 .alerter button {position:relative;width:100px;left:50%;margin-left:-50px}
 
 input[type=text] {border-radius:4px;border:1px solid #888;padding:3px;font:$(fz)}
 textarea {border-radius:4px;border:1px solid #888;padding:3px;font:$(fz)}
 select {padding:3px;}
 .wndbox .title {
  display:block;
  border-radius:10px 10px 0 0;
  left:0;top:0;right:0;height:25px;
  padding:5px;
  vertical-align:center;
  text-align:center;
  font:16px arial;
  background:#888;
  color:#fff;
 }
 .radius {  border-radius:10px;}
 .wndbox .info {
  display:block;
  left:0;top:0;right:0;height:auto;
  border-radius:0 0 10px 10px;
  padding:5px;
  vertical-align:center;
  text-align:center;
  font:13px arial;
  background:#383;
  color:#fff;
 }
 .wndbox .content {
  position:relative;
  left:0;margin-top:20px;right:0;bottom:0px;
 }
 .menu {display:block;background:#ccffcc;
        }
 .bt200 {width:300px}
 .bt300 {width:300px}
 .btimage {border:0;background:none;text-decoration:none}
 a img {text-decoration:none;border:0}
 .abarcode {border-radius:5px;background:#000;color:#fff;font-weight:bold;padding:3px;margin:0;cursor:pointer;border:2px solid white;display:inline-block}
</style>
</head>
<html>

<body>
<!
alert=''
alertcolor='#a22'
session_start()
sdb=sqlite3.connect('database.sdb')

cur=sdb.cursor()
def query(sql):
  print sql
  cur.execute(sql)
  return cur.fetchall()
def qexec(sql):
  print sql
  cur.execute(sql)
     
if form.aksi=='pilihklien':
  session.idauditmain=form.idauditmain
  form.view='pilihprinsip'
if form.aksi=='pilihprinsip':
  session.prinsip=form.prinsip
  form.view='prinsip'+form.prinsip
def fillcombo(sql,sel=None):
  print "fillcombo "+sql
  cur.execute(sql)
  for row in cur:
    a="";
    
    if str(row[0])==str(sel):a="selected"
    @<option value="$(row[0])" $a>$(row[1])</option>
def fillcombo1(sql,sel=None):
  print "fillcombo1"+sql
  cur.execute(sql)
  for row in cur:
    a="";
    
    if str(row[0])==str(sel):a="selected"
    @<option value="$(row[0])" $a>$(row[0])</option>
def fillcombo3(sql,sel=None):
  print "fillcombo"
  cur.execute(sql)
  for row in cur:
    a="";
    
    if str(row[0])==str(sel):a="selected"
    @<option value="$(row[0])" filter="$(row[2])" $a>$(row[1])</option>
  
print form.view,':::'
if(not form.view):form.view='pilihklien'
if (form.view=='pilihklien'):
  klien=query("select idauditmain,klien,tanggal from auditsvlkmain where status=1")
  @<table width=100% border=0>
  @<tr><td colspan=3><b>PILIH KLIEN AUDIT SVLK</b>
  n=1
  for k in klien:
    @<tr><td>$n<td><a href="index.py?aksi=pilihklien&idauditmain=$(k[0])">$(k[1])</a><td>$(k[2])
    n+=1
  @</table>
if form.view=='pilihprinsip':
  @<table width=100% border=0>
  @<tr><td colspan=2><b>PILIH DOKUMEN AUDIT</b><br>
  @<tr><td>1<td><a href='index.py?aksi=pilihprinsip&prinsip=1'>PRINSIP 1</a>
  @<tr><td>2<td><a href='index.py?aksi=pilihprinsip&prinsip=2'>PRINSIP 2</a>
  @<tr><td>3<td><a href='index.py?aksi=pilihprinsip&prinsip=3'>PRINSIP 3</a>
  @</table>
if form.ver:
  form.view='prinsip'+session.prinsip  
if form.view=='prinsip1':
  data=query("select klien,tanggal,b.data from auditsvlkmain a left join auditsvlk b on (a.idauditmain=b.idauditmain and b.prinsip=$(session.prinsip)) where a.idauditmain='$(session.idauditmain)'")
  data=data[0]
  @<B>AUDIT PRINSIP 1</B><BR>
  @Klien: $(data[0])<br>
  @Tanggal: $(data[1])<hr>
  
  include('prinsip1.py')    
if form.view=='prinsip3':
  data=query("select klien,tanggal,b.data from auditsvlkmain a left join auditsvlk b on (a.idauditmain=b.idauditmain and b.prinsip=$(session.prinsip)) where a.idauditmain='$(session.idauditmain)'")
  data=data[0]
  @<B>AUDIT PRINSIP 3</B><BR>
  @Klien: $(data[0])<br>
  @Tanggal: $(data[1])<hr>
  
  include('prinsip3.py')    
!>    
</body>

<FINALIZE>
print "Closing DB"
try:
  sdb.commit()
  sdb.close()
except:pass
