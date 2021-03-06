import sys,md5,urllib2,shutil
import os
try:
    import sqlite3,MySQLdb,_mysql
except:pass
sqliteRes=[]
base=os.path.split(sys.argv[0])[0].replace('\\','/')
"""
    ULO web server. Version 1.5
Programmer: Ryan Widi Saputra
            Nining Kurniattin

Features:  - Direktori web dinamis (bisa direktori / file ZIP)
           - Server script (pyp)
           - Lightning Fast !
           - Metode Pekerja Thread, mampu melayani banyak permintaan sekaligus
"""
import cPickle,calendar,datetime,time,cStringIO,random,math
import traceback,thread
import socket,SocketServer
import string
import zlib
import threading

# write log file
serverlog=[]
def printlog(a,b='',c='',d='',e=''):
    global serverlog
    log="%s%s%s%s%s" %(a,b,c,d,e)
    serverlog.append(log)
    if len(serverlog)>100:del serverlog[0]
# default setting
servername="Python Web Server (ryannining)"
strictimport = 0
TcpPort      = 8085
serverSocket = 0
starterWorker= 1
serverThread = 60000
echo         = 0
verbose      = 1
multithread  = 1
server       = 0

maxSessionAge= 60*60*24 # 24 jam maksimum umur session
SVORIfile    = file
# mysql persistent connection
mysqlconn={}
def mysql_connect(serv,user,pasw,db):
    global mysqlconn
    conn="%s%s%s%s" %(serv,user,pasw,db)
    if mysqlconn.has_key(conn):return mysqlconn[conn]
    else:
        printlog( "Connecting to database %s %s" % (serv,db))
        con=MySQLdb.connect(serv,user,pasw,db)
        if con:mysqlconn[conn]=con
        return con
# class direktori standar dan zip
listdir = 0
def compress(r):return zlib.compress(r,9),'deflate'
def getfilelist(path):
    ls=os.listdir(path)
    result=[]
    for f in ls:
        fn=os.path.join(path,f)
        if os.path.isfile(fn):
            result.append(fn)
    for f in ls:
        fn=os.path.join(path,f)
        if os.path.isdir(fn):
            result.append(fn+'/')
            for r in getfilelist(fn):
                result.append(r)
    return result
        
class stdDir:
    def close(me):pass
    def cekakses(me,fn):
        if fn[0]=='/':fn=fn[1:]
        else:fn=os.path.join(getworker().baseurl,fn)
        if (':' in fn) and (not 'temp.ryf' in fn):
            getworker().die('Tidak boleh mengakses %s'%fn)
        else: return fn
    def file(me,fn,mode=''):
        fn=me.cekakses(fn)
        if fn:
            if 'w' in mode or 'a' in mode or mode=='rb':
                return SVORIfile(fn,mode)
            elif 'o' in mode:
                return SVORIfile(fn)
            else:
                return cStringIO.StringIO(me.fileRead(fn,1))
    def rename(me,old,new):
        new=me.cekakses(new)
        old=me.cekakses(old)
        if new and old:
            os.rename(old,new)
    def copyfile(me,old,new):
        new=me.cekakses(new)
        old=me.cekakses(old)
        if new and old:
            shutil.copyfile(old,new)
    def remove(me,fn):
        fn=me.cekakses(fn)
        if fn:
            os.remove(fn)
    def rmdir(me,dn):
        dn=me.cekakses(dn)
        if dn:
            os.rmdir(dn)
    def mkdir(me,dn):
        dn=me.cekakses(dn)
        if dn:
            os.mkdir(dn)
    def makedirs(me,dn):
        dn=me.cekakses(dn)
        if dn:
            os.makedirs(dn)
    def removedirs(me,dn):
        dn=me.cekakses(dn)    
        if dn:os.removedirs(dn)
    def chdir(me,fn):pass
    def listdir(me,dir):
        files=me.getnames()
        r=[]
        rd=[]
        dir=dir.replace('\\','/')
        if dir and dir[0]=='/':dir=dir[1:]
        if dir and dir[-1]=='/':dir=dir[:-1]
        for item in files:
            ite=item.replace('\\','/')
            d,f=os.path.split(ite)
            if d and d[0]=='/':d=d[1:]
            if d==dir and f:r.append(f)
            dd=''
            if dir:
                if d[:len(dir)]==dir: dd=d[len(dir)+1:].split('/',1)[0]
            else: dd=d.split('/',1)[0]
            if dd<>''and not dd in rd:
                rd.append(dd)
        return r,rd
    def __init__(me,folder):
        me.folder=folder
        try:       os.chdir(folder)
        except:    pass
    def getFileTime(me,fn):     return os.path.getmtime(fn)
    def fileExists(me,fn):      return os.path.exists(fn)
    def isExists(me,fn):return me.fileExists(me.cekakses(fn))
    def getnames(me): return getfilelist('.')
    def fileRead(me,fn,binary=1):
        if os.path.exists(fn):
            if os.path.isdir(fn):  return ''
            if binary:   f=SVORIfile(fn,'rb')
            else:        f=SVORIfile(fn)
            r=f.read()
            f.close()
            return r
        return '<html><body><h4>HTML Error:404</h4>File %s tidak ditemukan!' % fn
    def storep(me,fn):
        if fn=='':fn=me.folder.split('.')[0]+'.fs'
        names=me.getnames()
        root    = {}
        print "Make pickle filesystem ",fn 
        for item in names:
            f=item.lower().replace('\\','/')
            f=item.lower().replace('./','')
            if '.fs' in f:continue
            if '~' in f:continue
            print "+ ",f
            ext=os.path.splitext(f)[1]
            try:
                if ext in ('.html','.py','.css','.htm'):
                    data=me.fileRead(f,0)
                else:
                    data=me.fileRead(f)
                root[f]=data
            except:pass
        f=file('../'+fn,'wb')
        f.write(zlib.compress(cPickle.dumps(root,-1),9))
        f.close()
class pDir(stdDir):
    def __init__(me,folder):
        me.cache=cPickle.loads(zlib.decompress(open(folder,'rb').read()))
    def getFileTime(me,fn):  return 1000
    def fileExists(me,fn):return fn in me.cache
    def fileRead(me,fn,binary=1):return me.cache[fn]
    def getnames(me):return me.cache


# Klas yang digunakan di aplikasi ini. 
# Fungsi utama: menghilangkan exception apabila atribut yang diminta tidak ada
#               dapat bersifat sebagai dictionary
class tWebObject(dict):
    __name__ = '__main__'
    def __getattr__(me,key):
        if not key in me:
            me.__setattr__(key,'')
        return dict.__getitem__(me,key)
    def __setattr__(me,key,value):
        dict.__setitem__(me,key,value)
    def count(me): return len(me.__dict__)
class tResponse:
    def __init__(me):      me.text=[]
    def clear(me):         me.text=[]
class tDummy:pass

# Kontanta pendukung webworker
# File-file yang didukung : html,jpeg,gif,py,(script)

SVmoduleChanged  = 1     # menyimpan data modul
SVscriptDate     = {}    # menyimpan datetime dari file script
SVscriptBinary   = {}    # menyimpan hasil kompilasi file script
SVglobalSession  = {}    # menyimpan data web session
SVworkID         = 0
SVdefaultHeader  ={'.html':['text/html',1],
                   '.htm' :['text/html',1],
                   '.css' :['text/css',1],
                   '.js'  :['text/javascript',1],

                   '.pycss':['text/css',1],
                   '.pyjs' :['text/javascript',1],
                   '.py'  :['text/html',1],
                   
                   '.text':['text/plain',1],
                   '.gif' :['image/gif',0],
                   '.png' :['image/png',0],
                   '.jpg' :['image/jpeg',0],
                   '.ico' :['image/icon',0],
                   '.pdf' :['image/pdf',0]}

masterdir        = os.path.abspath('.')
SVlibdir         = os.path.join(masterdir,'weblib')
workerbuff       = {}
clientloopcount  = 0
workerthread     = {}

# ======================================================================

def webtext(txt): # mengkonversi format teks query (%xx) menjadi ASCII
    hexdec = '0123456789ABCDEF'
    tmp,n='',0
    while n<len(txt):
        c=txt[n]
        if c=='+':c=' '
        elif c=='%':
            c=chr(hexdec.index(txt[n+1])*16+hexdec.index(txt[n+2]))
            n+=2
        tmp+=c
        n+=1
    return tmp
def clearsession(): # pembersihan terhadap session yang kadaluarsa
    skr=time.time()
    key=SVglobalSession.keys()
    for ses in key:
        dses=SVglobalSession[ses]
        if skr-dses[0]>maxSessionAge: del SVglobalSession[ses]
def filldata(x,force=0): # copy all from global to our locals
    if SVmoduleChanged<>x.moduleCtr or force:
        for d in globals().keys():
            if d[0:2]<>'SV' and not d in ('echo','os','thread','traceback','sys','select'):
                x.__setattr__(d,globals()[d])
        x.moduleCtr=SVmoduleChanged
        x.__import__=__import__
born=0
class tWebWorker:
    def __init__(s):
        global SVworkID,running
        if verbose:s.born=born
        s.no                   = str(SVworkID)
        SVworkID              +=1
        s.work                 = 0
        s.data                 = tWebObject()
        s.host                 = tWebObject()
        s.url                  = '' 
        # isi data-data fungsi yang dibutuhkan
        s.data.require          = s.includeonce
        s.data.requireonce      = s.includeonce
        s.data.include          = s.include
        s.data.includeModule    = s.includeModule
        s.data.setoutput        = s.setoutput
        
        s.data.session_start    = s.session_start
        s.data.session_stop     = s.session_stop
        s.data.start            = s.start
        s.data.stop             = s.stop
        s.data.startbuffering   = s.startbuffering
        s.data.stopbuffering    = s.stopbuffering
        s.data.die              = s.die
        s.data.timer            = s.timer
        s.data.exitweb          = exitweb
        
        s.data.cookie           = tWebObject()
        s.data.TEMP             = tWebObject()
        s.data.form             = tWebObject()
        s.data.SVglobalSession  = SVglobalSession
        s.data.recho            = tResponse()
        s.data.xecho            = tResponse()
        s.baseurl=''
        s.moduleCtr             = 0
        s.assigned              = 0
        s.hasIncluded           = {}
        filldata(s.data)
        global workerbuff
        workerbuff[id(s)]=s
    def __del__(me):
        if me.data<>0:me.free()
    def free(me):
        #if verbose:print "Pekerja no %s dihapus."%me.no
        global workerbuff
        del workerbuff[id(me)]
        me.data=0
        me.recho=0
        me.globals=0
    def timer(me): return time.time()-me.data.timer0
    def setoutput(me,output):
        me.data.recho.text=[output]
        me.stop()
    def compile(me,url,modul=0):
        return compile(parsefile(url),url,'exec')
    def includeModule(me,source):
        me.include(source,0,1)
    def getabsfile(me,source,cek=0):
        if not cek and me.data.fileurl=='':
            res=me.getabsfile(me.data.baseurl+'index.html',1)
            if not res[1]:
                res=me.getabsfile(me.data.baseurl+'index.py',1)
            return res
        if source[0]=='/':source=source[1:]
        sourcef=source
        if webroot.fileExists(me.data.baseurl+sourcef):
            sourcef = me.data.baseurl+source
        elif webroot.fileExists(sourcef): pass
        elif webroot.fileExists(os.path.join(SVlibdir,source)):
            sourcef=os.path.join(SVlibdir,source)
        elif webroot.fileExists(os.path.join(SVlibdir,os.path.split(source)[1])):
            sourcef=os.path.join(SVlibdir,os.path.split(source)[1])
        ok=webroot.fileExists(sourcef)
        return sourcef,ok
    def include(me,source,once=0,asmodule=0):
        url,ok=me.getabsfile(source)
        me.data.fileurl='x'
        if not ('.py' in url):
            me.data.echo.text.append(webroot.fileRead(url))
            return
        try:
            # cek tanggal apakah file diubah
            w=webroot.getFileTime(url)
            tglscrip=SVscriptDate.get(url,0)
            if once and (url in me.hasIncluded) and (w==tglscrip): return
            me.hasIncluded[url]=1
            global SVmoduleChanged,echo
            if w<>tglscrip:
               printlog( 'Script changed ',url )
               # kalau berubah berarti harus dikompile
               bin=me.compile(url)
               SVscriptBinary[url]=bin
               if asmodule: # jalankan script binary modul
                   echo = me.data.echo
                   try:  exec(bin,globals(),globals())
                   except SystemExit:  raise
                   #if verbose: print " ~~ Kompilasi modul : %s" % sourcef
                   SVmoduleChanged+=1
               #elif verbose: print " ~~ Kompilasi script : %s" % sourcef
               SVscriptDate[url]=w
            filldata(me.data)
            if not asmodule: # jalankan script binary
                try: exec(SVscriptBinary[url],me.data,me.data)
                except SystemExit: raise
                if me.data.finalize:
                    printlog( "Finalizing ",url)
                    me.data.finalize()
        except SystemExit: raise
        except:  # kalau ada yang ndak beres, tampilkan
            me.data.recho.text.append('\n</a></p></select></form></table></body></html><pre>')
            prn='KESALAHAN PADA SCRIPT:'
            for e in traceback.format_exception(sys.exc_type,sys.exc_value,sys.exc_traceback):
                if e=='' or 'ulo.py' in e or 'exc_value' in e:continue
                me.data.recho.text.append(e)
                prn+=e
            if me.data.PYERRORLOG:
                me.data.recho.text.append('Info dari script:'+me.data.PYERRORLOG)
                prn+='\nInfo dari script:'+me.data.PYERRORLOG
            if verbose:printlog( prn)
            sys.exc_clear()
    def includeonce(me,source):    me.include(source,1)
    def session_start(me,sid=0):
        # kasih udah mulai ndak usah dimulai lagi
        if me.sessionstarted:return
        # kasih tanda kalau session sudah dimulai
        me.sessionstarted = True
        printlog( "SESID:",me.data.cookie.SESID)
        id=sid or me.data.cookie.SESID or str(time.time())
        if id in SVglobalSession:
            # kalau ada load
            me.data.session=SVglobalSession[id][1]
            SVglobalSession[id][0]=time.time()
            if verbose: printlog( " ~~ Session id:[%s] dipakai" % id)
        else:
            # bikin data session baru
            me.data.cookie.SESID=id
            me.data.session=tWebObject()
            SVglobalSession[id]=[time.time(),me.data.session]
            if verbose: printlog( " ~~ Session baru dibuat id:%s" % id)
        # coba hapus yang kadaluarsa
        me.data.cookie['SESID']=id
        clearsession()
        if verbose: print( " ~~ Jumlah session di sistem:",len(SVglobalSession))
    def session_stop(me):
        # stop session dengan menghapusnya
        if me.data.cookie.SESID in SVglobalSession:
            me.data.session=0
            del SVglobalSession[me.data.cookie.SESID]
            me.sessionstarted = False
            del me.data.cookie['SESID']
    def stop(me):
        me.data.echo=me.data.xecho # stop output ke HTML
        me.data.oform=me.data.form
        me.data.form=tWebObject()
    def start(me):
        me.data.echo=me.data.recho # start output ke HTML
        me.data.form=me.data.oform
    def stopbuffering(me):
        me.data.echo=me.data.recho 
        return me.data.xecho.text
    def startbuffering(me):
        me.data.echo=me.data.xecho 
        me.data.xecho.text=[]
    def die(me,info,more=0):
        me.work=0
        if info:
            if verbose: printlog( '(DIE) Informasi:',info)
            me.data.recho.text.append("<br><font color=#880000><b>(DIE) Informasi:</b>%s</font><br>"%info)
            if more:
                for e in traceback.format_exception(sys.exc_type,sys.exc_value,sys.exc_traceback):
                    if e=='' or 'ulo.py' in e or 'exc_value' in e:continue
                    me.data.recho.text.append(e)
        raise SystemExit
    def servePage(me,url,host,query):
        me.data.baseurl=''
        if (not '.' in url) and (url[-1:]<>'/'): url+='/'
        if '/' in url:
            me.data.baseurl,me.data.fileurl=os.path.split(url)
            if me.data.baseurl and me.data.baseurl[0]=='/':
                me.data.baseurl=me.data.baseurl[1:]
        if me.data.baseurl:me.data.baseurl+='/'
        # apakah yang diminta adalah file script
        url,ok=me.getabsfile(url)
        me.data.baseurl,me.data.fileurl=os.path.split(url)
        #if serverscript and verbose: print " ~~ Serving Script : %s " % url
        while url<>'' and url[0]=='/': url=url[1:]
        # jika script maka butuh beberapa persiapan
        if '.py' in url:
            me.data.PY_me=url
            me.data.PY_QUERY=query
            # inisialisasi data session dan local
            # me.data.session=tWebObject()
            # ambil data-data cookie apabila ada
            if 'Cookie' in host:
                printlog( "Hcookie:",host.Cookie)
                params=host.Cookie.split(';')#[0]
                
                #params=params.split(', ')
                
                for par in params:
                    p=par.split('=',1)
                    p.append("")
                    me.data.cookie[p[0].strip()]=p[1]
                #print host.Cookie
            # ambil data-data query baik metode POST maupun GET
            if query<>'':
                params=query.split('&')
                for parw in params:
                    par=webtext(parw)
                    p=par.split('=',1)
                    if len(p)==2:
                        if '[' in p[0]:
                            p[0]=p[0].replace(']','[')
                            nama=p[0].split('[')
                            if not nama[0] in me.data.form:
                                me.data.form[nama[0]]={}
                            try:  k=int(nama[1])
                            except: k=nama[1]
                            me.data.form[nama[0]][k]=p[1]
                        else:
                            me.data.form[p[0]]=p[1]
            # simpan data form(query)        
            me.data.oform=me.data.form
            me.start()
            if serverThread==1:  pass
            else:
                try:   me.include(url)
                except SystemExit:  pass
            return me.data.recho
        else:return url
    def process(me,conn,data,keepalive,port=0,addr=0):
        global running
        me.data.globals=globals()
        me.data.onfinish=None
        me.data.addr=addr
        me.data.httpheader=''
        me.data.headers={}
        me.data.PYERRORLOG=''
        me.data.workerno = me.no
        me.data.cookie.clear()
        me.data.recho.clear()
        me.data.xecho.clear()
        me.sessionstarted = False
        me.data.timer0    = time.time()
        me.data.form.clear()
        me.host.clear()
        me.data.socketPort= port
        me.data.basepath=base
        filemethod=0
        if '; boundary=' in data:
            filemethod=1
            if '\r\n\r\n' in data:
                data,chunk=data.split('\r\n\r\n',1)
            else: chunk=''
        data = data.split('\r\n')
        host = me.host
        for item in data:
            pitem=item.split(': ')
            if len(pitem)==2: host[pitem[0]]=pitem[1]
        request  = data[0].split(' ')
        if len(request)<=1:
            
            return "HTTP/1.1 400 ERROR";
        url      = request[1].split('?',1)
        query    = ''
        if filemethod:
            left=int(host['Content-Length'].strip()) #-len(chunk)
            boundary=host['Content-Type'].strip().split('boundary=')[1]
            datasplit=chunk
            while len(datasplit)<left:
                  datasplit=datasplit+conn.recv(left)
            data=(datasplit).split('--'+boundary+'\r\n')
            boundary2='--'+boundary
            for chunk in data:
                chunksplit=chunk.split('\r\n\r\n',1)
                if len(chunksplit[0])<10:continue
                heads=chunksplit[0].split('\r\n')[0].split('form-data; ')[1]
                filename=0
                exec(heads.replace('\\','\\\\'))
                if filename:
                    afile=tDummy()
                    afile.filename=filename
                    afile.data=chunksplit[1]
                    me.data.form[name]=afile
                else:
                    isi=chunksplit[1].split(boundary2)[0][:-2]
                    me.data.form[name]=isi
        else:
            if len(url)==2:         query=(url[1])
            if request[0]=='POST':  query=(data[len(data)-1])
        url      = url[0].replace('.php','.py')
        durl=os.path.split(url)
        if not durl[1]:url=os.path.join(durl[0],'index.py')
        me.data.recho.exts=os.path.splitext(url)[1]
        fn       = me.servePage(url,host,query)
        me.url = url
        if me.data.onfinish:
            try:me.data.onfinish()
            except:pass
        tipestr  = type(fn) is str
        if tipestr: exts=os.path.splitext(url)[1]
        else: exts=fn.exts
        exts=exts.lower()
        hdr,com=SVdefaultHeader.get(exts,SVdefaultHeader['.html'])
        res=["HTTP/1.1 200 OK"]
        resh={}
        resh["Content-Type"]=hdr
        resh["Server"]=servername
        resh["Connection"]="Keep-Alive"
        r=''
        if exts=='.py':
            if (len(me.data.cookie)>0):
                cook=""
                for k in me.data.cookie.keys():
                    if cook:cook+=';\nSet-Cookie: '
                    cook+=k+'='+me.data.cookie[k]
                resh['Set-Cookie']=cook
                printlog( "Set Cookie:",cook)

                me.data.cookie.clear()
            resh['Cache-Control']='no-store, no-cache, must-revalidate, post-check=1, pre-check=1'
            for k in me.data.headers: 
                resh[k]=me.data.headers[k]
        if tipestr: 
            if webroot.fileExists(fn):
                tm=webroot.getFileTime(fn)
                #tx='"%s%x"'%(fn,tm)
                tx='"%x"'%(tm)
                if host.get('If-None-Match','')==tx:return "HTTP/1.1 304 OK\n"
                #res+='last-modified: %s\n'%datetime.datetime.fromtimestamp(tm).strftime("%a, %d %b %Y %H:%M:%S GMT")
                resh['etag']=tx
                resh['Cache-Control']='max-age=18000, must-revalidate'
                resh['Expires']=(datetime.datetime.today()+datetime.timedelta(days=365)).strftime("%a, %d %b %Y %H:%M:%S GMT")
                r = webroot.fileRead(fn)
            elif fn=='log.sys':
                global serverlog
                r=string.joinfields(serverlog,"\n")
                resh["Content-Type"]="text/plain"
            else:return "HTTP/1.1 404 OK\n"
        else:r = string.joinfields(fn.text,'')
        #if verbose:print res
        if com:
            if 'javascript' in hdr:r=compressjs(r)
            #r,m=compress(r)
            #resh['Content-Encoding']=m
        resh['Content-Length']=str(len(r))
        # merge headers
        for k in resh:
            res.append("%s: %s" % (k,resh[k]))
        #res.append('\n')
        h=string.joinfields(res,'\n')
        me.data.TEMP    = 0
        return "%s\n\n%s" % (h,r)
        
import SocketServer
try:
    import psyco
    psyco.full()
    print 'Psyco-enabled'
except:pass
workerpool=[]    
def exitweb():
    global running
    global server
    running=0
    for w in workerpool:
        print w
        w.die('Killed')
    print server
    server.shutdown()
    
def newworker(): 
    global workerpool
    for w in workerpool:
        if not w.work:return w
    w=tWebWorker()    
    workerpool.append(w)
    return w
class HTTPHandler(SocketServer.BaseRequestHandler):
    def handle(me):
        global running
        global serverThread,SVmoduleChanged,workerthread,clientloopcount
        born=datetime.datetime.today()
        tid=thread.get_ident()
        if serverThread>1: serverThread-=1
        clientloopcount+=1
        worker=workerthread.get(tid,newworker())
        worker.work= 1
        worker.baseurl=''
        workerthread[tid]=worker
        data=me.request.recv(7000)
        res=worker.process(me.request,data,1)
        me.request.send(res)
        worker.work=0
        now=datetime.datetime.today()
        if verbose: printlog( "!%s %s (%ssec) URL:%s"%(worker.no,born,(now-born),worker.url))
def serverloop():
    global server,running
    server = HTTPServer(('', TcpPort), HTTPHandler)
    server.serve_forever()
def startapp():
    global serverSocket,running
    if verbose:print " ULO Web Server version 2"
    running=1
    thread.start_new_thread(serverloop,())
    if verbose:
        while running:
            q=raw_input()
            if q=='q':
                exitweb()
            elif 'stoz' in q:  webroot.storez(q.split(',')[1])
            elif 'stop' in q:  webroot.storep(q.split(',')[1])
    else:
        while running: time.sleep(10)

# ==================================================================
# scanner and parser for script
# ==================================================================
def parsestring(input):
    var,l=[],len(input)
    invar,res,p,n=0,'',-1,0
    while p<l-1:
        p+=1
        c=input[p]
        if not invar:
            if c=='$':
                invar,svar=1,''
                continue
            if c=='%':
                res+='%s'
                var.append('"%"')
            else:res+=c
        else:
            if c=='(':
                p+=1
                de=1
                while de>0 and p<l:
                    c=input[p]
                    if c=='(':de+=1
                    if c==')':de-=1
                    if de>0:
                        svar+=c
                        p+=1
                p+=1
                c=' '
            if c in '"{}\\/\',.;:%&?$<>()[] ':
                invar=0
                if svar<>'':
                    res+='%s'
                    var.append(svar)
                    n+=1
                else:res+='$'
                p-=1
            else :svar+=c
    if n>0:
        res+='%('
        i=0
        for item in var:
            if i>0:res+=','
            res+=item
            i+=1
        res+=')'
        return res
    return input
        
# converting to python
def parseline(line):
    res=''
    l=len(line)
    p=0
    invar=0
    while p<l:
        c=line[p]
        if c=='$': invar=1
        elif invar==1:
            if c=='(':
                invar=2
                de=0
            else:invar=0
        if invar==2:
            if c=='(':de+=1
            if c==')':de-=1
            if de==0:invar=0
        if invar==0:
            if c=='"': c='\\"'
            elif c=='\\' and (p==l-1 or line[p+1]<>'\\'): c='\\\\'
        res+=c
        p+=1
    return res
def parsescript(isi):
    inpython=0
    tab=2
    res=['put=echo.text.append\ntry:\n']
    ctab='  '
    isfinal=0
    for ln in isi.split(chr(10)):
        lns=ln.strip()
        if lns<>'' and lns[0]=='#': pass
        if lns=='<FINALIZE>':
            isfinal=1
            inpython=1
            res.append('finally:\n')
            ctab='  '
            tab=2
        elif lns in ('<!>','<!!>'): inpython,tab=0,ln.index('<!')+2;ctab=' '*tab
        elif lns=='<!':             inpython=1;ctab=' '*tab
        elif lns=='!>':             inpython,tab=0,ln.index('!')+2;ctab=' '*tab
        elif lns in ('<?>','<??>'): inpython,tab=0,ln.index('<?')+2;ctab=' '*tab
        elif lns=='<?':             inpython=1;ctab=' '*tab
        elif lns=='?>':             inpython,tab=0,ln.index('?')+2;ctab=' '*tab
        else:
            if not inpython:
                if ln<>'' and '^' in ln and lns.index('^')==0:
                    res+=ctab+lns[1:]+'\n'
                    continue
                if lns<>'': res.append(ctab+'put("'+parseline(ln)+' ")\n')
                else:       res.append(ctab+'put(\'\')\n')
            else:
                if ln<>'' and '@' in ln:
                    ps=0
                    n=0
                    fail=1
                    for ch in ln:
                        if ch in ("'",'"'):ps=not ps
                        if ch=='@' and ps==0:
                            p=lns.index('@')
                            tab1=ln.index('@')
                            if p==0: res.append('  '+' '*tab1+'put("'+parseline(lns[1:])+' ")\n')
                            else: res.append('  '+ln[0:tab1]+'put("'+parseline(ln[tab1+1:])+' ")\n')
                            fail=0
                            break
                    if fail:res.append('  '+ln+chr(10))
                else:  res.append('  '+ln+chr(10))
            continue
    # get string
    if not isfinal:res.append('finally:pass#')
    data,ld,ldd='','',''
    mystr=[]
    instring,invar,de=0,0,0
    for d in string.joinfields(res,''):
        if instring and d=='$':  invar=1
        elif instring and invar==1:
            if d=='(':  invar,de=2,0
            else:       invar=0
        if instring and invar==2:
            if d=='(':de+=1
            if d==')':de-=1
            if de==0:invar=0
        if invar==0 and ((d=='"' and (not "\\" in ld+ldd))):
            if instring:
                instring=0
                astr+=d
                data+=parsestring(astr)
            else:
                instring,astr=1,d
            ld,ldd=d,ld
            continue
        if instring : astr+=d
        else:   data+=d
        ld,ldd=d,ld
    if instring:
        astr+=d
        data+=parsestring(astr)
    return data
def parsefile(fn):
    xx=parsescript(webroot.fileRead(fn,binary=0).replace(chr(13),''))
    if verbose:
        printlog ("Parse ", fn)
        f=SVORIfile(fn+'.txt','w')
        f.write(xx)
        f.close()
    return xx
def compressjs(isi):
    return jsmin(isi)
# JAVA MINI"    
from StringIO import StringIO
def jsmin(js):
    ins = StringIO(js)
    outs = StringIO()
    JavascriptMinify().minify(ins, outs)
    str = outs.getvalue()
    if len(str) > 0 and str[0] == '\n':
        str = str[1:]
    return str

def isAlphanum(c):
    """return true if the character is a letter, digit, underscore,
           dollar sign, or non-ASCII character.
    """
    return ((c >= 'a' and c <= 'z') or (c >= '0' and c <= '9') or
            (c >= 'A' and c <= 'Z') or c == '_' or c == '$' or c == '\\' or (c is not None and ord(c) > 126));
class UnterminatedComment(Exception): pass
class UnterminatedStringLiteral(Exception): pass
class UnterminatedRegularExpression(Exception): pass
class JavascriptMinify(object):

    def _outA(self):
        self.outstream.write(self.theA)
    def _outB(self):
        self.outstream.write(self.theB)

    def _get(self):
        """return the next character from stdin. Watch out for lookahead. If
           the character is a control character, translate it to a space or
           linefeed.
        """
        c = self.theLookahead
        self.theLookahead = None
        if c == None:
            c = self.instream.read(1)
        if c >= ' ' or c == '\n':
            return c
        if c == '': # EOF
            return '\000'
        if c == '\r':
            return '\n'
        return ' '

    def _peek(self):
        self.theLookahead = self._get()
        return self.theLookahead

    def _next(self):
        """get the next character, excluding comments. peek() is used to see
           if an unescaped '/' is followed by a '/' or '*'.
        """
        c = self._get()
        if c == '/' and self.theA != '\\':
            p = self._peek()
            if p == '/':
                c = self._get()
                while c > '\n':
                    c = self._get()
                return c
            if p == '*':
                c = self._get()
                while 1:
                    c = self._get()
                    if c == '*':
                        if self._peek() == '/':
                            self._get()
                            return ' '
                    if c == '\000':
                        raise UnterminatedComment()

        return c

    def _action(self, action):
        """do something! What you do is determined by the argument:
           1   Output A. Copy B to A. Get the next B.
           2   Copy B to A. Get the next B. (Delete A).
           3   Get the next B. (Delete B).
           action treats a string as a single character. Wow!
           action recognizes a regular expression if it is preceded by ( or , or =.
        """
        if action <= 1:
            self._outA()

        if action <= 2:
            self.theA = self.theB
            if self.theA == "'" or self.theA == '"':
                while 1:
                    self._outA()
                    self.theA = self._get()
                    if self.theA == self.theB:
                        break
                    if self.theA <= '\n':
                        raise UnterminatedStringLiteral()
                    if self.theA == '\\':
                        self._outA()
                        self.theA = self._get()


        if action <= 3:
            self.theB = self._next()
            if self.theB == '/' and (self.theA == '(' or self.theA == ',' or
                                     self.theA == '=' or self.theA == ':' or
                                     self.theA == '[' or self.theA == '?' or
                                     self.theA == '!' or self.theA == '&' or
                                     self.theA == '|' or self.theA == ';' or
                                     self.theA == '{' or self.theA == '}' or
                                     self.theA == '\n'):
                self._outA()
                self._outB()
                while 1:
                    self.theA = self._get()
                    if self.theA == '/':
                        break
                    elif self.theA == '\\':
                        self._outA()
                        self.theA = self._get()
                    elif self.theA <= '\n':
                        raise UnterminatedRegularExpression()
                    self._outA()
                self.theB = self._next()


    def _jsmin(self):
        """Copy the input to the output, deleting the characters which are
           insignificant to JavaScript. Comments will be removed. Tabs will be
           replaced with spaces. Carriage returns will be replaced with linefeeds.
           Most spaces and linefeeds will be removed.
        """
        self.theA = '\n'
        self._action(3)

        while self.theA != '\000':
            if self.theA == ' ':
                if isAlphanum(self.theB):
                    self._action(1)
                else:
                    self._action(2)
            elif self.theA == '\n':
                if self.theB in ['{', '[', '(', '+', '-']:
                    self._action(1)
                elif self.theB == ' ':
                    self._action(3)
                else:
                    if isAlphanum(self.theB):
                        self._action(1)
                    else:
                        self._action(2)
            else:
                if self.theB == ' ':
                    if isAlphanum(self.theA):
                        self._action(1)
                    else:
                        self._action(3)
                elif self.theB == '\n':
                    if self.theA in ['}', ']', ')', '+', '-', '"', '\'']:
                        self._action(1)
                    else:
                        if isAlphanum(self.theA):
                            self._action(1)
                        else:
                            self._action(3)
                else:
                    self._action(1)

    def minify(self, instream, outstream):
        self.instream = instream
        self.outstream = outstream
        self.theA = '\n'
        self.theB = None
        self.theLookahead = None

        self._jsmin()
        self.instream.close()
# ==================================================================
modulesNeed=[]

if os.path.exists('config.ini'):  execfile('config.ini',globals())
else:webroot     = stdDir('root')

if multithread:
    class HTTPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer): pass
    print 'Using multithread'
else:    
    class HTTPServer(SocketServer.TCPServer): pass
# ======================================================================
empty=tWebWorker()
def fakeIO(data):   return cStringIO.StringIO(data)
def getworker():    return workerthread.get(thread.get_ident(),empty)
def getecho():      return workerthread[thread.get_ident()].echo
if strictimport:
    import __builtin__        
    SVimport=__builtin__.__import__
    def SVximport(fn,g=None,l=None,fr=None):
        if fn in ('os','thread','traceback','sys','select'):
            getworker().die('PY Script tidak boleh mengimport modul %s, letakkan modul yang dibutuhkan di konfigurasi !' % fn)
        else:
            __builtin__.__import__=SVimport
            res=SVimport(fn,g,l,fr)
            __builtin__.__import__=SVximport
            return res
    __builtin__.__import__=SVximport
# ============ check argument ============
# -x exit
# -s store in pickle fs
# -r [root folder] set root folder
    
oktorun=1
larg=''
for arg in sys.argv:
    if arg=='-s':webroot.storep('')
    if arg=='-x':oktorun=0
    if larg=='-r':webroot=stdDir(arg)
    if larg=='-rp':webroot=pDir(arg)
    larg=arg

listdir    = webroot.listdir
file       = webroot.file
open       = webroot.file
splitpath  = os.path.split
splitext   = os.path.splitext
joinpath   = os.path.join
mkdir      = webroot.mkdir 
makedirs   = webroot.makedirs
remove     = webroot.remove
rename     = webroot.rename
copyfile   = webroot.copyfile
rmdir      = webroot.rmdir
removedirs = webroot.removedirs
# ======================================================================

if oktorun:startapp()
webroot.close()

