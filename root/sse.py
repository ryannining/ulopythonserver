<?
#import _mysql
global running
db=mysql_connect("localhost","root","norikosakai","diggersf_android")
cur=db.cursor()
session_start(form.sid)
headers['Content-Type']='text/event-stream'
headers['Cache-Control']='no-cache'
headers['Access-Control-Allow-Origin']='*'
if not session.lastkomenp:
    cur.execute("select max(idkomentar) from komentar")
    r=cur.fetchone()
    session.lastkomena=r[0]
    cur.execute("select max(idkomen) from home_komen")
    r=cur.fetchone()
    session.lastkomenp=r[0]
    session.users=''
if form.sid=='123123':session.lastkomenp=0    
n=100
while n>0:
    if getworker().work==0:break
    time.sleep(0.8)

    n=n-1
    cur.execute("select max(idkomentar) from komentar")
    r1=cur.fetchone()
    cur.execute("select max(idkomen) from home_komen")
    r2=cur.fetchone()

    cur.execute("select a.idcustomer,customer,nick  from user_online a left join customer b on(a.idcustomer=b.idcustomer) where a.idcustomer>0 and lastonline+INTERVAL 30 MINUTE>NOW() order by lastonline desc")
    
    x=0
    ul=''
    while 1:
        r=cur.fetchone()
        if (r==None):break
        ul=ul+"<b>$(r[2])</b>, "
        x+=1
    cur.execute("select count(*) from user_online where idcustomer=0 and lastonline+INTERVAL 30 MINUTE>NOW()")
    r4=cur.fetchone()
    uo="User online("+str(r4[0]+x)+"): "
    ul=uo+ul+ " dan $(r4[0]) tamu"
    if session.users<>ul:
        session.users=ul
        @data: $ul
        put('\n\n')
        n=0    
        
    if (r1[0]>session.lastkomena) or (r2[0]>session.lastkomenp ):
        cur.execute("select count(*) as c from komentar where idkomentar>$(session.lastkomena)")
        r3=cur.fetchone()
        cur.execute("select count(*) as c from home_komen where idkomen>$(session.lastkomenp)")
        r4=cur.fetchone()
        session.lastkomena=r1[0]
        session.lastkomenp=r2[0]
        nc=r3[0]+r4[0]
        @data: Load $nc komen terkini
        put('\n\n')
        
        n=0

?>
