<style>
 textarea {width:95%;height:50px;overflow-y:scroll}
 .warna1 {color:rgb(16,128,255);font-weight:bold}
 .bukti {color:rgb(16,128,255);font-weight:bold}
 .verifier td {background:rgb(16,128,255);color:#fff;font-weight:bold}
 .verifier a {color:#fff}
 .tambah td{background:#eee;padding:10px;text-align:center;height:50px}
 .save td{background:#eee;padding:10px;text-align:center;height:50px}
 .save a{text-decoration:none}
 .daftarisi {font:14px arial}
 .wideinput {width:95%}
 .shortinput {width:95%}
 .middletd {width:25%;min-width:150px}
 .lefttd {width:30px}
 tr>td {vertical-align:top;padding-bottom:3px;min-height:40px} 
</style>
<!
if form.ver:
  session.verifier=form.ver
  include("Prinsip 1/p1ver$(form.ver).html")
  !>
  <script>
  prinsip='$(session.prinsip)';
  verifier='$(session.verifier)';
  auditmain='$(session.idauditmain)';
  function loadverifier(ver,callback){
    jq.ajax({url:'service.py?call=loadverifierdata&prinsip='+prinsip+'&verifier='+ver+'&idauditmain='+auditmain,success:function(x){
        if(x){ 
          data=JSON.parse(x);
          if (callback)callback(data);
        }
        
      }
    });
  }
  function fillthisform(data){
    if (confirm("Gunakan data yg sudah tersimpan ?")){
      beforefillthisform(data);
      inputs=jq(':input');
      ctr={}
      for (i=0;i<inputs.length;i++){
        inp=inputs[i];
        if (inp.toString()=="[object HTMLButtonElement]")continue;
        tinp=jq(inp);
        nm=tinp.attr('name');
        ct=ctr[nm];
        if(!ct)ct=0;
        if (data[nm]){
          d=data[nm][ct];
          if (inp.type=='radio'){if (inp.value==d)tinp.attr('checked',true);}
          else if (inp.type=='checkbox')tinp.attr('checked',inp.value==d);
          else tinp.val(d);
          ctr[nm]=ct+1
        }
      }
    }
  }
  jq('input[type=radio]').removeAttr('checked');
  jq('input[type=checkbox]').removeAttr('checked');
  loadverifier(verifier,fillthisform);
  function saveverifier(par){
    ver=par.attr('verifier');
    inputs=jq(':input');
    data={};
    for (i=0;i<inputs.length;i++){
      inp=inputs[i];
      if (inp.toString()=="[object HTMLButtonElement]")continue;
      tinp=jq(inp);
      nm=tinp.attr('name');
      if (!data[nm])data[nm]=[];
      if (inp.type=='radio') {
        if (inp.checked)data[nm].push(tinp.val());
      }
      else if (inp.type=='checkbox'){
        if (inp.checked)data[nm].push(tinp.val());
      }
      else {
        data[nm].push(tinp.val());
      }
    }
    sdata=JSON.stringify(data);
    jq.ajax({
    'url':'service.py?call=saveverifierdata&prinsip='+prinsip+'&verifier='+ver+'&idauditmain='+auditmain+'&data='+sdata,
    'success':function(x){
        c=x.substr(0,3);
        x=x.substr(4);
        if (c=='ERR')return alert(x);
        if (x)return alert(x);
        alert('Data sukses tersimpan');
      }
    });
  }
  jq('.save td').html("<a id=btmenu1 href='index.py'><button>Menu 1</button></a>"+
                      "<a id=btmenu2 href='index.py?aksi=pilihklien&idauditmain=$(session.idauditmain)'><button>Menu 2</button></a>"+
                      "<a id=btmenu3 href='index.py?aksi=pilihprinsip&prinsip=$(session.prinsip)'><button>Menu 3</button></a>"+
                      "<button verifier='$(session.verifier)'>Save Verifier</button>");
  jq('button').each(function(x){
    var jt=jq(this);
    if (jt.attr('verifier')){
      jt.click(function xsave(){saveverifier(jt);});  
    }
  });

  </script>
  <!
else:  
  !>
<table cellspacing=0 cellpadding=0  width=100% class="daftarisi"><tr align=center><td colspan=2>
<a name=atas></a>
<b>Daftar isi</b><br>
<tr align=center><td>
<a href="index.php?view=prinsip1&ver=1.1.1.a">Verifier 1.1.1.a</a><br>
<a href="index.php?view=prinsip1&ver=1.1.1.b">Verifier 1.1.1.b</a><br>
<a href="index.php?view=prinsip1&ver=1.1.1.c">Verifier 1.1.1.c</a><br>
<a href="index.php?view=prinsip1&ver=1.1.1.d">Verifier 1.1.1.d</a><br>
<a href="index.php?view=prinsip1&ver=1.1.1.e">Verifier 1.1.1.e</a><br>
<a href="index.php?view=prinsip1&ver=1.1.1.f">Verifier 1.1.1.f</a><br>
<a href="index.php?view=prinsip1&ver=1.1.1.g">Verifier 1.1.1.g</a><br>
<td>
<a href="index.php?view=prinsip1&ver=1.1.2.a">Verifier 1.1.2.a</a><br>
<a href="index.php?view=prinsip1&ver=1.1.2.b">Verifier 1.1.2.b</a><br>
<a href="index.php?view=prinsip1&ver=1.1.2.c">Verifier 1.1.2.c</a><br>
<a href="index.php?view=prinsip1&ver=1.1.2.d">Verifier 1.1.2.d</a><br>
<a href="index.php?view=prinsip1&ver=1.1.2.e">Verifier 1.1.2.e</a><br>
<a href="index.php?view=prinsip1&ver=1.1.2.f">Verifier 1.1.2.f</a><br>
<a href="index.php?view=prinsip1&ver=1.1.2.g">Verifier 1.1.2.g</a><br>
<a href="index.php?view=prinsip1&ver=1.1.2.h">Verifier 1.1.2.h</a><br>
</table>
<br><br>
  <!
!>  
