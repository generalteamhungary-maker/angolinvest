import re,shutil,os
s=open('/home/claude/angolinvest.html').read()
import sys
O=sys.argv[1] if len(sys.argv)>1 else '/mnt/user-data/outputs/angolinvest-weboldal/'
os.makedirs(O+'img',exist_ok=True)
for x in os.listdir(O+'img'): os.remove(O+'img/'+x)
for f in ['adatvedelem.html','favicon.ico','favicon.png','apple-touch-icon.png']: shutil.copy('/home/claude/site/'+f,O+f)
used=set(re.findall(r"img/[\w\-]+\.(?:jpg|png)",s))|{'img/logo.png'}
used|={'img/'+x+'.jpg' for x in re.findall(r"'((?:ref|cat)-[\w\-]+)'",s)}
for u in used: shutil.copy('/home/claude/'+u,O+u)
s=re.sub(r'<title>.*?</title>','',s,count=1)
head='''<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Angol Invest Kft. – Ingatlanfejlesztés és generálkivitelezés, eladó lakások Budán</title>
<meta name="description" content="Angol Invest Kft. – ingatlanfejlesztés és generálkivitelezés Budapesten 2006 óta. Eladó új lakások Sasadon: Baradla utca 3., Lanka utca 17. 91 megvalósult projekt, 164 átadott lakás.">
<link rel="canonical" href="https://www.angolinvest.hu/">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:title" content="Angol Invest Kft.">
<meta property="og:description" content="Ingatlanfejlesztés | Generálkivitelezés – eladó új lakások Sasadon">
<meta property="og:image" content="https://www.angolinvest.hu/img/baradla.jpg">
<style>html{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
</head>
<body>
'''
open(O+'index.html','w').write(head+s+'\n</body>\n</html>\n')
open(O+'robots.txt','w').write('User-agent: *\nAllow: /\nSitemap: https://www.angolinvest.hu/sitemap.xml\n')
open(O+'sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<url><loc>https://www.angolinvest.hu/</loc><lastmod>2026-10-08</lastmod></url>\n<url><loc>https://www.angolinvest.hu/adatvedelem.html</loc><lastmod>2026-10-08</lastmod></url>\n</urlset>\n')
print(len(used),'images')
