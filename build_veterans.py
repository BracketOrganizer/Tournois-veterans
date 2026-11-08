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
</style>
</head>
<body>
<div class="box">
  <img class="logo" src="@@LOGO@@" alt="Logo Thouaré-Loire UST Football">
  <h1>Tournoi Vétérans UST</h1>
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
INFO = {
    12: '3 formules · 4 à 6 matchs par équipe',
    16: '4 poules de 4 · 6 matchs par équipe',
    20: '4 poules de 5 · 6 matchs par équipe',
    24: '4 poules de 6 · 8 matchs par équipe',
}
cards = ''
for n in SRC:
    cards += '  <a class="card" data-f="' + str(n) + '" href="?f=' + str(n) + '"><span class="num">' + str(n) + '</span><span class="lbl">' + str(n) + ' équipes<small>' + INFO.get(n, '') + '</small></span></a>' + chr(10)
html = TEMPLATE.replace('@@BLOCKS@@', chr(10).join(blocks)).replace('@@CARDS@@', cards).replace('@@LOGO@@', LOGO).replace('@@FAV@@', FAV)
with open(os.path.join(BASE, OUT), 'w', encoding='utf-8', newline=chr(10)) as fh:
    fh.write(html)
print('OK ->', OUT, round(os.path.getsize(os.path.join(BASE, OUT)) / 1024), 'Ko')
