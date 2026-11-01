#!/usr/bin/env python3
"""Génère Tournoi_Veterans.html (menu 12/16/20/24) à partir des 4 fichiers sources.
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

TEMPLATE = r'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#0f4a1f">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>">
<title>⚽ Tournoi Vétérans UST</title>
<style>
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:none;align-items:center;justify-content:center;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;color:#fff;background:radial-gradient(ellipse at top,#145a28 0%,#0a2e15 60%,#04140a 100%)}
.box{width:100%;max-width:460px;text-align:center}
h1{font-size:26px;margin:0 0 6px}
p{margin:0 0 26px;color:#b9d8c1;font-size:14px}
a.card{display:flex;align-items:center;gap:16px;margin:12px 0;padding:18px 20px;border-radius:16px;text-decoration:none;color:#fff;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);transition:.15s}
a.card:hover,a.card:active{background:rgba(255,255,255,.16);transform:translateY(-1px)}
a.card.last{border-color:#6ee790;box-shadow:0 0 0 2px rgba(110,231,144,.25)}
.num{font-size:34px;font-weight:800;min-width:56px;color:#6ee790}
.lbl{text-align:left;font-size:18px;font-weight:700}
.lbl small{display:block;font-weight:400;font-size:12px;color:#b9d8c1;margin-top:2px}
</style>
</head>
<body>
<div class="box">
  <h1>⚽ Tournoi Vétérans UST</h1>
  <p>Choisissez le nombre d'équipes</p>
@@CARDS@@
</div>
@@BLOCKS@@
<script>
(function(){
  var f = new URLSearchParams(location.search).get('f');
  var el = f && document.getElementById('app'+f);
  function unesc(s){ return s.replace(/<\\\/script/g,'</script').replace(/<\\script/g,'<script').replace(/<\\!--/g,'<!--'); }
  function start(){
    if(!el){
      try{ var last=localStorage.getItem('footFormat'); var c=document.querySelector('a.card[data-f="'+last+'"]'); if(c) c.classList.add('last'); }catch(e){}
      document.querySelectorAll('a.card').forEach(function(a){ a.addEventListener('click',function(){ try{localStorage.setItem('footFormat',a.dataset.f);}catch(e){} }); });
      document.body.style.display='flex';
      return;
    }
    var html = unesc(el.textContent);
    // petit bouton « changer de format » (retour au menu), injecté avant la dernière balise </body>
    var btn = '<a href="'+location.pathname+'" title="Changer de format (12 / 16 / 20 / 24 équipes)" style="position:fixed;left:8px;bottom:8px;z-index:150;width:30px;height:30px;border-radius:50%;background:rgba(0,0,0,.55);color:#fff;font:16px/30px sans-serif;text-align:center;text-decoration:none;opacity:.5">⚽</a>';
    var i = html.lastIndexOf('</body>');
    if(i>-1) html = html.slice(0,i)+btn+html.slice(i);
    document.open(); document.write(html); document.close();
  }
  // document.open() n'est effectif qu'une fois le parsing terminé
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',function(){ setTimeout(start,0); });
  else setTimeout(start,0);
})();
</script>
</body>
</html>
'''
open(os.path.join(BASE,OUT),'w',encoding='utf-8',newline='\n').write(TEMPLATE.replace('@@BLOCKS@@','\n'.join(blocks)).replace('@@CARDS@@','\n'.join('  <a class="card" data-f="%d" href="?f=%d"><span class="num">%d</span><span class="lbl">%d équipes</span></a>'%(n,n,n,n) for n in SRC)))
print('OK ->',OUT, round(os.path.getsize(os.path.join(BASE,OUT))/1024),'Ko')
