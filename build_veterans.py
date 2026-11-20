#!/usr/bin/env python3
"""Génère index.html « Tournoi Vétérans UST » (menu 12/16/20/24) à partir des 4 fichiers sources.
Usage : python3 build_veterans.py   (les 4 fichiers vétérans dans le même dossier)"""
import re, sys, json, os
SRC = {12:'Tournoi_Veterans_12.html', 16:'Tournoi_vétérans_UST_16.html', 20:'Tournoi_vétérans_UST_20.html', 24:'Tournoi_vétérans_UST_24.html'}
OUT = 'index.html'   # page d'accueil du dépôt (GitHub Pages)

import unicodedata
BASE = os.path.dirname(os.path.abspath(__file__))
def find_src(name):
    """Cherche le fichier dans Sources/, sources/ ou à côté du script (insensible aux accents NFC/NFD)."""
    want = unicodedata.normalize('NFC', name)
    for d in ('Sources', 'sources', '.'):
        folder = os.path.join(BASE, d)
        if not os.path.isdir(folder): continue
        for f in os.listdir(folder):
            if unicodedata.normalize('NFC', f) == want:
                return os.path.join(folder, f)
    sys.exit('Fichier manquant : ' + name + ' (à placer dans le dossier Sources/)')

def esc(s):  # protège le contenu dans <script type="text/plain">
    return s.replace('<!--','<\\!--').replace('</script','<\\/script').replace('<script','<\\script')

blocks=[]
for n,fn in SRC.items():
    s=open(find_src(fn),encoding='utf-8',newline='').read().replace('\r\n','\n')
    blocks.append(f'<script type="text/plain" id="app{n}">\n{esc(s)}\n</script>')

# Logo UST (déjà intégré dans les apps sous forme de data-URI) -> réutilisé pour le menu
_first = open(find_src(SRC[12]),encoding='utf-8').read()
_m1 = re.search(r'--logo-ust:url\((data:[^)]+)\)', _first)
_m2 = re.search(r'<link rel="icon" type="image/png" href="(data:[^"]+)">', _first)
if not (_m1 and _m2): sys.exit('Logo introuvable dans ' + SRC[12] + ' (utiliser les apps « Tournoi Vétérans UST » avec le logo)')
LOGO, FAV = _m1.group(1), _m2.group(1)


# ── Hub (inscription commune) : configuration Firebase / tags / comptes organisateur lus dans les sources ──
_hub_fb, _hub_tags, _hub_admins = None, {}, []
for _n,_fn in SRC.items():
    _s = open(find_src(_fn),encoding='utf-8').read()
    if _hub_fb is None:
        _m = re.search(r"const firebaseConfig = \{(.*?)\};", _s, re.S)
        if _m: _hub_fb = dict(re.findall(r'(\w+):\s*"([^"]*)"', _m.group(1)))
    _t = re.search(r"REG_TOURNAMENT_TAG = '([^']+)'", _s)
    if _t: _hub_tags[str(_n)] = _t.group(1)
    for _blk in re.findall(r"HARDCODED_ADMIN_EMAILS\s*=\s*\[([^\]]*)\]", _s):
        for _e in re.findall(r"'([^']+)'", _blk):
            if _e not in _hub_admins: _hub_admins.append(_e)
if not _hub_fb or len(_hub_tags) != len(SRC): sys.exit('Configuration Firebase / tags introuvables dans les sources')
HUBCFG = json.dumps({'fb':_hub_fb,'admins':_hub_admins,'tags':_hub_tags,'formats':list(SRC.keys()),'col':'hub','docId':'settings'}, ensure_ascii=False)
HUBCSS = r''':root{--hub-ac:#ffb066}
/* ── HUB : inscription commune + espace organisateur ── */
.hub-banner{margin:14px 0 18px;padding:14px 16px;border-radius:14px;background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.25);text-align:center;font-size:13px;line-height:1.5}
.hub-banner b{display:block;font-size:15px;margin-bottom:4px}
.hub-btn{display:inline-block;margin-top:10px;padding:12px 18px;border:0;border-radius:12px;background:var(--hub-ac,#6ee790);color:#10200f;font-weight:700;font-size:15px;line-height:1.2;font-family:inherit;cursor:pointer}
.hub-btn.sec{background:#e9ecef;color:#222}
.hub-btn.warn{background:#c0281a;color:#fff}
.hub-btn:disabled{opacity:.5;cursor:default}
.hub-foot{margin:22px 0 0;font-size:12px;text-align:center}
.hub-foot a{color:inherit;opacity:.55;text-decoration:none}
.hub-foot a:hover{opacity:1;text-decoration:underline}
.hub-ov{position:fixed;inset:0;z-index:1000;background:rgba(0,0,0,.72);display:flex;align-items:flex-start;justify-content:center;overflow:auto;padding:18px}
.hub-card{background:#fff;color:#1b1b1b;border-radius:16px;width:100%;max-width:580px;padding:20px 18px;text-align:left;box-shadow:0 20px 60px rgba(0,0,0,.5)}
.hub-card h2{margin:0 0 4px;font-size:19px}
.hub-card h3{margin:18px 0 8px;font-size:15px}
.hub-card p{margin:0 0 12px;color:#555;font-size:13px}
.hub-card label{display:block;margin:10px 0 4px;font-size:12px;font-weight:700;color:#444}
.hub-card input[type=text],.hub-card input[type=email],.hub-card input[type=password],.hub-card input[type=tel]{width:100%;padding:10px 12px;border:1.5px solid #c9ccd1;border-radius:8px;font-size:16px;font-family:inherit}
.hub-row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.hub-msg{margin:10px 0 0;font-size:13px;font-weight:600}
.hub-msg.err{color:#c0281a}.hub-msg.ok{color:#1a7a3a}
.hub-x{float:right;border:0;background:#eee;border-radius:50%;width:32px;height:32px;font-size:18px;cursor:pointer}
.hub-fmt{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 12px;border:1.5px solid #dde0e4;border-radius:12px;margin:8px 0}
.hub-fmt small{display:block;color:#666;font-size:12px;margin-top:2px}
.hub-fmt.best{border-color:#1a7a3a;background:#f1faf3}
.hub-list{max-height:220px;overflow:auto;border:1px solid #e3e5e8;border-radius:10px;font-size:13px}
.hub-list div{padding:7px 10px;border-bottom:1px solid #eee}.hub-list div:last-child{border-bottom:0}
.hub-radio{display:block;padding:10px 12px;border:1.5px solid #dde0e4;border-radius:12px;margin:8px 0;cursor:pointer}
.hub-radio input{margin-right:8px}
.hub-radio small{display:block;color:#666;font-size:12px;margin:3px 0 0 24px;font-weight:400}
.hub-wait a.card,.hub-wait #menuIntro{visibility:hidden}
.hub-fmt small a{color:#1a5fb4}
'''
HUBJS = r'''(function(){
var H=@@HUBCFG@@;
var SDK='https://www.gstatic.com/firebasejs/10.12.0/', FB=null, SET=null;
function $(id){return document.getElementById(id);}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
async function fb(){
  if(FB) return FB;
  var m=await Promise.all([import(SDK+'firebase-app.js'),import(SDK+'firebase-auth.js'),import(SDK+'firebase-firestore.js')]);
  var app=m[0].initializeApp(H.fb);
  FB={au:m[1],fs:m[2],auth:m[1].getAuth(app),db:m[2].getFirestore(app)};
  return FB;
}
async function loadSettings(){
  try{ var f=await fb(); var s=await f.fs.getDoc(f.fs.doc(f.db,H.col,H.docId)); SET=s.exists()?(s.data()||{}):{}; }
  catch(e){ SET=null; }
  return SET;
}
function overlay(html){
  var o=document.createElement('div'); o.className='hub-ov'; o.setAttribute('role','dialog'); o.setAttribute('aria-modal','true');
  o.innerHTML='<div class="hub-card">'+html+'</div>';
  o.addEventListener('click',function(e){ if(e.target===o) o.remove(); });
  document.body.appendChild(o); return o;
}
function setMsg(el,t,c){ if(el){ el.textContent=t; el.className='hub-msg '+(c||''); } }
function errText(e){
  var c=e&&e.code||'';
  var map={'auth/email-already-in-use':"Cet email a déjà un compte. Connectez-vous avec cet email dans l'appli du tournoi, ou utilisez un autre email.",
    'auth/invalid-email':'Adresse email invalide.','auth/weak-password':'Mot de passe trop faible (6 caractères minimum).',
    'auth/network-request-failed':'Problème de connexion réseau. Réessayez.','auth/operation-not-allowed':"La connexion par email n'est pas activée (à activer dans Firebase Authentication).",
    'auth/wrong-password':'Email ou mot de passe incorrect.','auth/invalid-credential':'Email ou mot de passe incorrect.','auth/user-not-found':'Email ou mot de passe incorrect.',
    'permission-denied':"Écriture refusée par les règles Firestore (permission-denied). L'organisateur doit mettre à jour les règles (voir la notice d'installation)."};
  return map[c]||('Erreur ('+(c||'inconnue')+') : '+(e&&e.message||''));
}

/* ───────── Bannière publique (mode inscription commune) ───────── */
function chosen(s){
  var f=s&&s.format?String(s.format):null; if(!f) return null;
  return document.querySelector('a.card[data-f="'+f+'"]')?f:null;
}
function renderBanner(s){
  var slot=$('hubSlot'); if(!slot) return;
  var open=s.regOpen!==false, fmt=chosen(s);
  if(!open && fmt){ slot.innerHTML=''; return; }
  slot.innerHTML='<div class="hub-banner"><b>📝 Inscription</b>'+
    (open?'Inscrivez votre équipe : l\u2019organisation vous communiquera ensuite l\u2019accès au tournoi.<br><button class="hub-btn" id="hubRegBtn">S\u2019inscrire</button>'
         :'Les inscriptions sont actuellement fermées. Le tournoi sera annoncé prochainement.')+'</div>';
  var b=$('hubRegBtn'); if(b) b.onclick=openReg;
}
/* Menu public : en mode commun, aucun format n'est visible tant que l'organisateur n'en a pas choisi un ;
   ensuite seul le bouton du format choisi apparaît. En cas d'erreur de lecture : menu normal (apps séparées). */
function applyMenu(s){
  var box=document.querySelector('.box');
  var common=!!(s&&s.mode==='common'), fmt=common?chosen(s):null;
  [].forEach.call(document.querySelectorAll('a.card'),function(a){ a.style.display=(common&&a.getAttribute('data-f')!==fmt)?'none':''; });
  var intro=$('menuIntro');
  if(intro){
    if(common&&fmt){ intro.textContent='✅ Le tournoi est ouvert : connectez-vous dans l\u2019appli ci-dessous avec l\u2019email utilisé pour l\u2019inscription.'; intro.style.display=''; }
    else if(common){ intro.style.display='none'; }
  }
  if(common) renderBanner(s);
  if(box) box.classList.remove('hub-wait');
}
function openReg(){
  var o=overlay('<button class="hub-x" aria-label="Fermer">×</button><h2>Inscription au tournoi</h2>'+
    '<p>Votre inscription sera examinée par l\u2019organisation. Vous pourrez ensuite vous connecter dans l\u2019appli du tournoi avec les mêmes identifiants.</p>'+
    '<label for="hr_team">Nom de l\u2019équipe *</label><input id="hr_team" type="text" autocomplete="off">'+
    '<div id="hr_extra"></div><button class="hub-btn sec" id="hr_add" type="button" style="margin-top:8px">+ Inscrire une autre équipe</button>'+
    '<label for="hr_club">Club / Entreprise *</label><input id="hr_club" type="text">'+
    '<label for="hr_contact">Nom du responsable *</label><input id="hr_contact" type="text" autocomplete="name">'+
    '<label for="hr_email">Email *</label><input id="hr_email" type="email" autocomplete="email">'+
    '<label for="hr_phone">Téléphone *</label><input id="hr_phone" type="tel" autocomplete="tel">'+
    '<label for="hr_pwd">Mot de passe * (6 caractères minimum)</label><input id="hr_pwd" type="password" autocomplete="new-password">'+
    '<label for="hr_pwd2">Confirmer le mot de passe *</label><input id="hr_pwd2" type="password" autocomplete="new-password">'+
    '<div class="hub-msg" id="hr_msg" role="status"></div>'+
    '<button class="hub-btn" id="hr_go" style="margin-top:12px;width:100%">Envoyer mon inscription</button>');
  o.querySelector('.hub-x').onclick=function(){o.remove();};
  var add=o.querySelector('#hr_add');
  add.onclick=function(){
    var w=o.querySelector('#hr_extra'), n=w.querySelectorAll('input').length+2;
    if(n>6) return;
    var i=document.createElement('input'); i.type='text'; i.className='hr_x'; i.placeholder='Nom de l\u2019équipe '+n; i.style.marginTop='8px'; w.appendChild(i);
    if(n>=6) add.style.display='none';
  };
  o.querySelector('#hr_go').onclick=async function(){
    var g=function(id){return (o.querySelector('#'+id).value||'').trim();}, msg=o.querySelector('#hr_msg');
    var team=g('hr_team'), club=g('hr_club'), contact=g('hr_contact'), email=g('hr_email'), phone=g('hr_phone');
    var pwd=o.querySelector('#hr_pwd').value, pwd2=o.querySelector('#hr_pwd2').value;
    if(!team||!club||!contact||!email||!phone||!pwd){ setMsg(msg,'Merci de remplir tous les champs.','err'); return; }
    var names=[team].concat([].slice.call(o.querySelectorAll('.hr_x')).map(function(i){return i.value.trim();})).filter(Boolean);
    var low=names.map(function(n){return n.toLowerCase();});
    if(low.filter(function(n,i){return low.indexOf(n)!==i;}).length){ setMsg(msg,'Deux équipes ont le même nom : merci de les différencier.','err'); return; }
    if(pwd.length<6){ setMsg(msg,'Le mot de passe doit faire au moins 6 caractères.','err'); return; }
    if(pwd!==pwd2){ setMsg(msg,'Les deux mots de passe ne correspondent pas.','err'); return; }
    var btn=this; btn.disabled=true; setMsg(msg,'Envoi en cours…','');
    var f,cred;
    try{
      var cur=await loadSettings();
      if(cur && cur.regOpen===false){ setMsg(msg,'Les inscriptions sont fermées.','err'); btn.disabled=false; return; }
      f=await fb(); cred=await f.au.createUserWithEmailAndPassword(f.auth,email,pwd);
    }catch(e){ setMsg(msg,errText(e),'err'); btn.disabled=false; return; }
    try{
      await f.fs.setDoc(f.fs.doc(f.db,'users',cred.user.uid),{email:email,name:contact,role:'registrant',tournament:'hub',teamName:team,teamNames:names,club:club,phone:phone,regStatus:'pending',createdAt:f.fs.serverTimestamp()},{merge:true});
      o.querySelector('.hub-card').innerHTML='<button class="hub-x" aria-label="Fermer">×</button><h2>✅ Inscription enregistrée</h2><p>Merci ! Votre inscription ('+names.length+' équipe'+(names.length>1?'s':'')+') est en attente. Revenez sur cette page : l\u2019accès au tournoi y apparaîtra dès son ouverture par l\u2019organisation. Connectez-vous alors avec l\u2019email '+esc(email)+'.</p>';
      o.querySelector('.hub-x').onclick=function(){o.remove();};
    }catch(e){
      try{ await cred.user.delete(); }catch(e2){}
      setMsg(msg,errText(e),'err'); btn.disabled=false;
    }
  };
}

/* ───────── Espace organisateur ───────── */
function openAdmin(){
  var o=overlay('<button class="hub-x" aria-label="Fermer">×</button><h2>⚙️ Espace organisateur</h2><div id="ha_body"></div>');
  o.querySelector('.hub-x').onclick=function(){o.remove();};
  var body=o.querySelector('#ha_body');
  (async function(){
    var f; try{ f=await fb(); }catch(e){ body.innerHTML='<p class="hub-msg err">Impossible de charger Firebase (réseau ?).</p>'; return; }
    if(f.auth.currentUser) return afterAuth(f.auth.currentUser,body);
    body.innerHTML='<p>Connectez-vous avec votre compte organisateur.</p>'+
      '<label for="ha_email">Email</label><input id="ha_email" type="email" autocomplete="email">'+
      '<label for="ha_pwd">Mot de passe</label><input id="ha_pwd" type="password" autocomplete="current-password">'+
      '<div class="hub-msg" id="ha_msg" role="status"></div>'+
      '<div class="hub-row" style="margin-top:12px"><button class="hub-btn" id="ha_go">Se connecter</button><button class="hub-btn sec" id="ha_g">Continuer avec Google</button></div>';
    var msg=body.querySelector('#ha_msg');
    body.querySelector('#ha_go').onclick=async function(){
      try{ var c=await f.au.signInWithEmailAndPassword(f.auth,body.querySelector('#ha_email').value.trim(),body.querySelector('#ha_pwd').value); afterAuth(c.user,body); }
      catch(e){ setMsg(msg,errText(e),'err'); }
    };
    body.querySelector('#ha_g').onclick=async function(){
      try{ var c=await f.au.signInWithPopup(f.auth,new f.au.GoogleAuthProvider()); afterAuth(c.user,body); }
      catch(e){ setMsg(msg,errText(e),'err'); }
    };
  })();
}
async function isAdmin(user){
  if(user.email && H.admins.indexOf(user.email)>=0) return true;
  try{ var f=await fb(); var s=await f.fs.getDoc(f.fs.doc(f.db,'users',user.uid)); return s.exists() && (s.data().role==='admin' || s.data().role==='users'); }catch(e){ return false; }
}
async function afterAuth(user,body){
  if(!(await isAdmin(user))){ body.innerHTML='<p class="hub-msg err">Ce compte n\u2019a pas les droits d\u2019organisateur.</p><button class="hub-btn sec" id="ha_out">Se déconnecter</button>';
    body.querySelector('#ha_out').onclick=async function(){ var f=await fb(); await f.au.signOut(f.auth); body.innerHTML='<p>Déconnecté.</p>'; }; return; }
  renderPanel(body);
}
function teamCount(u){ return (u.teamNames&&u.teamNames.length)||1; }
async function renderPanel(body){
  body.innerHTML='<p>Chargement…</p>';
  var f=await fb(), s=await loadSettings();
  if(s===null){ body.innerHTML='<p class="hub-msg err">Réglages illisibles (règles Firestore à mettre à jour : collection « '+esc(H.col)+' »). Le menu reste en mode « apps séparées ».</p>'; s={}; }
  var regs=[], err='';
  try{
    var snap=await f.fs.getDocs(f.fs.query(f.fs.collection(f.db,'users'),f.fs.where('tournament','==','hub')));
    snap.forEach(function(d){ var u=d.data(); if(u&&u.role==='registrant') regs.push(Object.assign({id:d.id},u)); });
  }catch(e){ err=errText(e); }
  // inscrits déjà affectés à un format mais encore « en attente » (réaffectation possible)
  var prev=[], asg=null;
  try{ var ad=await f.fs.getDoc(f.fs.doc(f.db,H.col,'assigned')); if(ad.exists()) asg=ad.data(); }catch(e){}
  if(asg && asg.uids){
    for(var i=0;i<asg.uids.length;i++){
      try{ var d=await f.fs.getDoc(f.fs.doc(f.db,'users',asg.uids[i])); if(d.exists()){ var u=d.data(); if(u.role==='registrant'&&u.regStatus==='pending'&&u.tournament===asg.tag) prev.push(Object.assign({id:d.id},u)); } }catch(e){}
    }
  }
  regs.sort(function(a,b){ var x=a.createdAt&&a.createdAt.seconds||0,y=b.createdAt&&b.createdAt.seconds||0; return x-y; });
  var targets=regs.concat(prev), total=targets.reduce(function(n,u){return n+teamCount(u);},0);
  var mode=s.mode==='common'?'common':'separate', open=s.regOpen!==false;
  var best=null; H.formats.forEach(function(n){ if(total>=n && (best===null||n>best)) best=n; });
  if(best===null) best=H.formats[0];
  var h='';
  if(err) h+='<p class="hub-msg err">'+esc(err)+'</p>';
  h+='<h3>1. Mode des inscriptions</h3>'+
    '<label class="hub-radio"><input type="radio" name="ha_mode" value="separate"'+(mode==='separate'?' checked':'')+'>Inscriptions séparées (comme avant)<small>Un QR code par format. Chaque appli gère ses propres inscriptions.</small></label>'+
    '<label class="hub-radio"><input type="radio" name="ha_mode" value="common"'+(mode==='common'?' checked':'')+'>Inscription commune<small>Un seul QR code (cette page). Vous choisissez ensuite le format selon le nombre d\u2019équipes.</small></label>'+
    '<label class="hub-radio"><input type="checkbox" id="ha_open"'+(open?' checked':'')+'>Inscriptions ouvertes (mode commun)</label>'+
    '<p>En mode commun, tant qu\u2019aucun format n\u2019est choisi (étape 3), le public ne voit que l\u2019inscription : ni les formats, ni l\u2019organisation.</p>'+
    '<button class="hub-btn" id="ha_save">Enregistrer le mode</button><div class="hub-msg" id="ha_msg1" role="status"></div>';
  h+='<h3>2. Inscrits en attente de format ('+total+' équipe'+(total>1?'s':'')+', '+targets.length+' responsable'+(targets.length>1?'s':'')+')</h3>';
  if(!targets.length) h+='<p>Aucune inscription commune pour l\u2019instant.</p>';
  else h+='<div class="hub-list">'+targets.map(function(u){ return '<div><b>'+esc(u.club||'?')+'</b> — '+esc((u.teamNames&&u.teamNames.join(', '))||u.teamName||'')+'<br><small>'+esc(u.name||'')+' · '+esc(u.email||'')+(u.tournament!=='hub'?' · déjà affecté ('+esc(u.tournament)+')':'')+'</small></div>'; }).join('')+'</div>';
  h+='<h3>3. Choisir le format du tournoi</h3><p>Les équipes seront transférées dans l\u2019appli choisie, où vous les validez comme d\u2019habitude. Possible tant que le tirage n\u2019est pas fait.</p>';
  H.formats.forEach(function(n){
    var diff=total-n, note= diff===0?'Complet : '+total+' / '+n : (diff<0?'Il manque '+(-diff)+' équipe'+(diff<-1?'s':'')+' ('+total+' / '+n+')':diff+' équipe'+(diff>1?'s':'')+' en liste d\u2019attente ('+total+' / '+n+')');
    h+='<div class="hub-fmt'+(n===best?' best':'')+'"><div><b>'+n+' équipes</b>'+(n===best?' · suggéré':'')+'<small>'+esc(note)+' · <a href="?f='+n+'" target="_blank" rel="noopener">Ouvrir l\u2019appli</a></small></div><button class="hub-btn'+(n===best?'':' sec')+'" data-n="'+n+'"'+(targets.length?'':' disabled')+'>Utiliser</button></div>';
  });
  var pub=s.format&&s.mode==='common';
  h+='<p style="margin-top:10px">Affiché au public (mode commun) : '+(pub?'<b>format '+esc(s.format)+' équipes</b> <button class="hub-btn sec" id="ha_unpub" style="margin:0 0 0 6px;padding:6px 10px;font-size:12px">Retirer</button>':'<b>aucun format</b> (le public ne voit que l\u2019inscription)')+'</p>';
  h+='<div class="hub-msg" id="ha_msg2" role="status"></div><div class="hub-row" style="margin-top:14px"><button class="hub-btn sec" id="ha_out">Se déconnecter</button></div>';
  body.innerHTML=h;
  body.querySelector('#ha_save').onclick=async function(){
    var m=body.querySelector('input[name=ha_mode]:checked').value, op=body.querySelector('#ha_open').checked, msg=body.querySelector('#ha_msg1');
    try{ await f.fs.setDoc(f.fs.doc(f.db,H.col,H.docId),{mode:m,regOpen:op,updatedAt:f.fs.serverTimestamp()},{merge:true}); setMsg(msg,'Enregistré ✅ (le menu public est mis à jour).','ok'); }
    catch(e){ setMsg(msg,errText(e),'err'); }
  };
  body.querySelector('#ha_out').onclick=async function(){ await f.au.signOut(f.auth); body.innerHTML='<p>Déconnecté.</p>'; };
  var unp=body.querySelector('#ha_unpub');
  if(unp) unp.onclick=async function(){
    try{ await f.fs.setDoc(f.fs.doc(f.db,H.col,H.docId),{format:null,updatedAt:f.fs.serverTimestamp()},{merge:true}); renderPanel(body); }
    catch(e){ setMsg(body.querySelector('#ha_msg2'),errText(e),'err'); }
  };
  [].forEach.call(body.querySelectorAll('button[data-n]'),function(b){
    b.onclick=async function(){
      var n=+b.getAttribute('data-n'), tag=H.tags[n], msg=body.querySelector('#ha_msg2');
      var diff=total-n, txt='Ce format deviendra le seul bouton visible sur la page publique.\n\nTransférer '+targets.length+' inscription'+(targets.length>1?'s':'')+' ('+total+' équipes) vers le format '+n+' équipes ?'+(diff>0?'\n\n'+diff+' équipe(s) resteront en liste d\u2019attente (l\u2019appli ne valide que '+n+' équipes).':(diff<0?'\n\nIl manquera '+(-diff)+' équipe(s).':''))+'\n\nÀ faire AVANT le tirage.';
      if(!confirm(txt)) return;
      var ok=0, ids=[]; b.disabled=true; setMsg(msg,'Transfert en cours…','');
      try{
        for(var i=0;i<targets.length;i++){ await f.fs.updateDoc(f.fs.doc(f.db,'users',targets[i].id),{tournament:tag}); ok++; ids.push(targets[i].id); }
        await f.fs.setDoc(f.fs.doc(f.db,H.col,'assigned'),{format:n,tag:tag,uids:ids,at:f.fs.serverTimestamp()});
        await f.fs.setDoc(f.fs.doc(f.db,H.col,H.docId),{format:n,updatedAt:f.fs.serverTimestamp()},{merge:true});
        setMsg(msg,'✅ '+ok+' inscription'+(ok>1?'s':'')+' transférée'+(ok>1?'s':'')+' vers le format '+n+'. Ouvrez l\u2019appli '+n+' équipes pour les valider.','ok');
        setTimeout(function(){ renderPanel(body); },1800);
      }catch(e){ setMsg(msg,'Arrêt après '+ok+' transfert(s) : '+errText(e),'err'); b.disabled=false; }
    };
  });
}


/* ───────── Garde d'accès direct aux applis (mode commun) ─────────
   Mode commun : seule l'appli du format choisi est accessible au public ; avant le choix, aucune.
   L'organisateur (admin / rôle users connecté) peut ouvrir toutes les applis.
   Toute erreur ou lenteur : accès normal (comportement d'origine). */
function authUser(f){
  return new Promise(function(res){
    var done=false, un=null;
    var t=setTimeout(function(){ if(!done){ done=true; res(null); } },2500);
    un=f.au.onAuthStateChanged(f.auth,function(u){ if(done) return; done=true; clearTimeout(t); try{ if(un) un(); }catch(e){} res(u); });
  });
}
window.__guardApp=async function(f){
  try{
    var s=await loadSettings();
    if(!s || s.mode!=='common') return true;
    if(s.format && String(s.format)===String(f)) return true;
    var x=await fb(), u=await authUser(x);
    if(u && await isAdmin(u)) return true;
    return false;
  }catch(e){ return true; }
};

window.__initHub=async function(){
  var a=$('hubAdminLink'); if(a) a.onclick=function(e){ e.preventDefault(); openAdmin(); };
  var s=await loadSettings();
  applyMenu(s);
};
})();
'''

TEMPLATE = r'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#c1440e">
<link rel="icon" type="image/png" href="@@FAV@@">
<title>⚽ Tournoi Vétérans UST</title>
<style>
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:none;align-items:center;justify-content:center;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;color:#fff;background:radial-gradient(ellipse at 50% 0%,#c1440e 0%,#7a2a08 55%,#2a1204 100%)}
.box{width:100%;max-width:460px;text-align:center}
.logo{display:block;width:150px;height:auto;aspect-ratio:800/1082;margin:0 auto 14px;filter:drop-shadow(0 8px 18px rgba(0,0,0,.55))}
h1{font-family:Oswald,'Segoe UI',system-ui,sans-serif;font-size:30px;line-height:1.1;margin:0 0 6px;text-transform:uppercase;letter-spacing:1.5px;text-shadow:0 2px 6px rgba(0,0,0,.4)}
p{margin:0 0 24px;color:#ffd9b8;font-size:14px}
a.card{display:flex;align-items:center;gap:16px;margin:12px 0;padding:18px 20px;border-radius:16px;text-decoration:none;color:#fff;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);transition:.15s}
a.card:hover,a.card:active{background:rgba(255,255,255,.16);transform:translateY(-1px)}
a.card.last{border-color:#ffb066;box-shadow:0 0 0 2px rgba(255,176,102,.28)}
.num{font-size:34px;font-weight:800;min-width:56px;color:#ffb066}
.lbl{text-align:left;font-size:18px;font-weight:700}
.lbl small{display:block;font-weight:400;font-size:12px;color:#ffd9b8;margin-top:2px}
@@HUBCSS@@
</style>
</head>
<body>
<div class="box hub-wait">
  <img class="logo" src="@@LOGO@@" alt="Logo Thouaré-Loire UST Football">
  <h1>Tournoi Vétérans UST</h1>
  <p id="menuIntro">Choisissez le nombre d'équipes</p>
  <div id="hubSlot"></div>
@@CARDS@@
  <div class="hub-foot"><a href="#" id="hubAdminLink">⚙️ Espace organisateur</a></div>
</div>
@@BLOCKS@@
<script>
@@HUBJS@@
</script>
<script>
(function(){
  var f = new URLSearchParams(location.search).get('f');
  var el = f && document.getElementById('app'+f);
  function unesc(s){ return s.replace(/<\\\/script/g,'</script').replace(/<\\script/g,'<script').replace(/<\\!--/g,'<!--'); }
  function showMenu(){
    try{ var last=localStorage.getItem('footFormat'); var c=document.querySelector('a.card[data-f="'+last+'"]'); if(c) c.classList.add('last'); }catch(e){}
    document.querySelectorAll('a.card').forEach(function(a){ a.addEventListener('click',function(){ try{localStorage.setItem('footFormat',a.dataset.f);}catch(e){} }); });
    document.body.style.display='flex';
    try{ if(window.__initHub) window.__initHub(); }catch(e){}
    setTimeout(function(){ var bx=document.querySelector('.box'); if(bx) bx.classList.remove('hub-wait'); }, window.__initHub ? 3500 : 0);
  }
  function loadApp(){
    var html = unesc(el.textContent);
    // petit bouton « changer de format » (retour au menu), injecté avant la dernière balise </body>
    var btn = '<a href="'+location.pathname+'" title="Changer de format (12 / 16 / 20 / 24 équipes)" style="position:fixed;left:8px;bottom:8px;z-index:150;width:30px;height:30px;border-radius:50%;background:rgba(0,0,0,.55);color:#fff;font:16px/30px sans-serif;text-align:center;text-decoration:none;opacity:.5">⚽</a>';
    var i = html.lastIndexOf('</body>');
    if(i>-1) html = html.slice(0,i)+btn+html.slice(i);
    document.open(); document.write(html); document.close();
  }
  function start(){
    if(!el){ showMenu(); return; }
    // inscription commune : accès direct aux applis contrôlé (erreur ou délai dépassé = accès normal)
    var done=false;
    function go(ok){
      if(done) return; done=true;
      if(ok){ loadApp(); }
      else { try{ history.replaceState(null,'',location.pathname); }catch(e){} showMenu(); }
    }
    setTimeout(function(){ go(true); }, 3500);
    try{ if(window.__guardApp) window.__guardApp(f).then(go,function(){ go(true); }); else go(true); }catch(e){ go(true); }
  }
  // document.open() n'est effectif qu'une fois le parsing terminé
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',function(){ setTimeout(start,0); });
  else setTimeout(start,0);
})();
</script>
</body>
</html>
'''
INFO = {
    12: '3 formules · 4 à 6 matchs par équipe',
    16: '4 poules de 4 · 6 matchs par équipe',
    20: '4 poules de 5 · 6 matchs par équipe',
    24: '4 poules de 6 · 8 matchs par équipe',
}
cards = ''
for n in SRC:
    cards += '  <a class="card" data-f="' + str(n) + '" href="?f=' + str(n) + '"><span class="num">' + str(n) + '</span><span class="lbl">' + str(n) + ' équipes<small>' + INFO.get(n, '') + '</small></span></a>' + chr(10)
html = TEMPLATE.replace('@@HUBCSS@@', HUBCSS).replace('@@HUBJS@@', HUBJS.replace('@@HUBCFG@@', HUBCFG)).replace('@@BLOCKS@@', chr(10).join(blocks)).replace('@@CARDS@@', cards).replace('@@LOGO@@', LOGO).replace('@@FAV@@', FAV)
with open(os.path.join(BASE, OUT), 'w', encoding='utf-8', newline=chr(10)) as fh:
    fh.write(html)
print('OK ->', OUT, round(os.path.getsize(os.path.join(BASE, OUT)) / 1024), 'Ko')
