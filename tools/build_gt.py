#!/usr/bin/env python3
"""GeneralTeam-verzió: az angolinvest.html tartalmából Angol Invest-mentes, beágyazott (nem iframe-es)
uj-lakasok.html oldalt készít a generalteam repóba.  Használat: python3 build_gt.py /home/claude/generalteam"""
import re, sys, os, shutil

SRC = '/home/claude/angolinvest.html'
IMG = '/home/claude/img'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/generalteam'
TPL = os.path.join(OUT, 'belsoepiteszet.html')
DIR = 'lakasok'

s = open(SRC, encoding='utf-8').read()
tpl = open(TPL, encoding='utf-8').read()

def rep(text, a, b, cnt=1):
    n = text.count(a)
    assert n >= 1, 'nem található: ' + a[:80]
    if cnt is not None:
        assert n == cnt, f'{n}× található: {a[:80]}'
    return text.replace(a, b)

# ---------- CSS: hatókörbe zárás .aiw alá, .lb -> .ailb ----------
css = s[s.find('<style>') + 7:s.find('</style>')]
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
css = re.sub(r'\.lb(?=[\s\-{.,:\[>])', '.ailb', css)

def scope_sel(sel):
    sel = sel.strip()
    if not sel:
        return sel
    if sel in (':root', 'html', 'body'):
        return '.aiw'
    if sel == '*':
        return '.aiw,.aiw *'
    if sel.startswith('html ') or sel.startswith('body '):
        sel = sel.split(' ', 1)[1]
    return '.aiw ' + sel

def scope(block):
    out, i = [], 0
    while i < len(block):
        j = block.find('{', i)
        if j < 0:
            out.append(block[i:]); break
        head = block[i:j].strip()
        depth, k = 1, j + 1
        while depth:
            if block[k] == '{': depth += 1
            elif block[k] == '}': depth -= 1
            k += 1
        body = block[j + 1:k - 1]
        if head.startswith('@media') or head.startswith('@supports'):
            if 'prefers-reduced-motion' in head:
                i = k; continue
            out.append(head + '{' + scope(body) + '}')
        elif head.startswith('@'):
            out.append(head + '{' + body + '}')
        else:
            out.append(','.join(scope_sel(x) for x in head.split(',')) + '{' + body + '}')
        i = k
    return '\n'.join(out)

css = scope(css)
css += '''
/* GeneralTeam arculat a beágyazott részen */
.aiw{--ink:#0F2B36;--dark:#0F2B36;--text:#24363E;--muted:#56656D;--line:#DCE2E4;--band:#EBEEEC;--bg:transparent;
  --f-head:'Archivo',system-ui,sans-serif;--f-body:'Archivo',system-ui,sans-serif;--f-label:'Archivo',system-ui,sans-serif;background:transparent}
.aiw h2{text-transform:none;letter-spacing:-.015em}
.aiw .label{color:#8A6430}
.aiw .rule{background:#C49A5C}
.aiw .project{background:#fff}
.aiw .how{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:26px}
.aiw .how div{background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px}
.aiw .how b{display:block;font-size:1.05rem;color:var(--ink);margin:6px 0 4px}
.aiw .how span.n{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:50%;background:#0F2B36;color:#fff;font-weight:700}
.aiw .gk{margin-top:22px;background:#0F2B36;color:#fff;border-radius:12px;padding:22px 24px;display:flex;gap:18px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.aiw .gk p{color:#E6ECEE;max-width:70ch}.aiw .gk b{color:#fff}
/* linkek a fehér űrlapon */
.aiw form a{color:#8A6430;text-decoration:underline}
.aiw .gk .btn{background:#C49A5C;border-color:#C49A5C;color:#0F2B36}
@media (max-width:760px){.aiw .how{grid-template-columns:1fr}}
'''

# ---------- JS ----------
js = s[s.find('<script>') + 8:s.rfind('</script>')]

INTRO1 = ('Négylakásos, új építésű társasház Sasad csendes, zöld utcájában, 2027-es átadással. '
          'Minden lakás önálló albetét, így saját otthonnak és befektetésnek is jó választás. '
          'Jó tájolás, átgondolt alaprajzok; a belső elrendezésen és a burkolatokon még lehet módosítani.')
INTRO2 = ('Háromszintes, liftes társasház három lakással, Sasad egyik csendes zsákutcájában. '
          'Korszerű, alacsony fenntartási költségű gépészet; a belső kialakítás és a burkolatok igény szerint választhatók.')

js = re.sub(r"id:'baradla',name:'[^']*',eyebrow:'[^']*',address:'[^']*'",
            "id:'p1',name:'Sasadi társasház – 4 lakás',eyebrow:'Építés alatt',address:'Budapest XI., Sasad'", js)
js = re.sub(r"id:'lanka',name:'[^']*',eyebrow:'[^']*',address:'[^']*'",
            "id:'p2',name:'Sasadi liftes társasház – 3 lakás',eyebrow:'Átadás 2026-ban',address:'Budapest XI., Sasad'", js)
js = re.sub(r"(id:'p1'.*?intro:)'[^']*'", lambda m: m.group(1) + repr(INTRO1).replace('"', "'"), js, count=1, flags=re.S)
js = re.sub(r"(id:'p2'.*?intro:)'[^']*'", lambda m: m.group(1) + repr(INTRO2).replace('"', "'"), js, count=1, flags=re.S)
assert 'Baradla' not in js and "Lanka utca 17" not in js, 'utcanév maradt'
js = js.replace("n:'Olt utca 26.'", "n:'Olt utca'")

# képek
imgmap = {}
def img(src_rel, new):
    imgmap[src_rel] = new
    return f'{DIR}/{new}'
for fl in ['pince', 'fsz', '1em', '2em']:
    js = rep(js, f"'img/baradla-{fl}.jpg'", f"'{img('gt/baradla-'+fl+'.jpg', 'p1-'+fl+'.jpg')}'")
for fl in ['pince', 'fsz', '1em', 'teto']:
    js = rep(js, f"'img/lanka-{fl}.jpg'", f"'{img('gt/lanka-'+fl+'.jpg', 'p2-'+fl+'.jpg')}'")
js = rep(js, "img:'img/baradla.jpg'", f"img:'{img('baradla.jpg', 'p1.jpg')}'")
js = rep(js, "img:'img/lanka-render.jpg'", f"img:'{img('lanka-render.jpg', 'p2.jpg')}'")
for c in re.findall(r"img:'img/(cat-[\w-]+\.jpg)'", js):
    js = rep(js, f"img:'img/{c}'", f"img:'{img(c, c)}'")
for x in set(re.findall(r"'((?:ref|cat)-[\w\-]+)'", js)):
    imgmap[x + '.jpg'] = x + '.jpg'
js = rep(js, "src:'img/'+x+'.jpg'", f"src:'{DIR}/'+x+'.jpg'")
js = rep(js, '<img src="img/${r.p[0]}.jpg"', f'<img src="{DIR}/${{r.p[0]}}.jpg"')

js = rep(js, ".value='Lakásvásárlás'", ".value='Új lakás – érdeklődés'")
js = rep(js, 'Kérem, küldjék el a részletes műszaki leírást.', 'Kérem, küldjék el a részletes műszaki leírást, és egyeztessünk megtekintési időpontot.')
js = js.replace('info@angolinvest.hu', 'info@generalteam.hu')
js = rep(js, 'const MAXF=15*1024*1024', 'const MAXF=10*1024*1024')
js = rep(js, 'nagyobb 15 MB-nál', 'nagyobb 10 MB-nál')

# űrlap -> GeneralTeam backend
js = re.sub(r"/\* Az űrlap a Google Apps Script.*?\nconst GAS_URL='[^']*';",
            "const API='https://script.google.com/macros/s/AKfycbxYgeSJEPj4zQlQoxu1woLnLV8YQdEm2bXwhjzd2IbayPJULP6pmNfQOj3PonUnmEnA/exec';",
            js, flags=re.S)
js = rep(js, "if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(v('email'))&&!v('phone')){err.textContent='Adjon meg e-mail-címet vagy telefonszámot, hogy válaszolni tudjunk.';",
             "if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(v('email'))){err.textContent='Kérjük, adjon meg érvényes e-mail-címet, hogy válaszolni tudjunk.';")
old_try = js[js.find("    const payload={topic"):js.find("  }catch(_){ok=false}")]
new_try = """    const ctx=v('msg').match(/iránt: (.*?lakás) \\(/);
    const o={hp:form.website.value,ut:'visszahivas',elso:'Visszahívás',nev:v('name'),email:v('email'),tel:v('phone'),
      tipus:v('topic'),ingatlan:/kivitelez|felújítás/i.test(v('topic'))?'Egyéb':'Új lakás',hely:'Budapest XI.',
      megj:v('msg'),reszlet:'Új lakások oldal'+(ctx?' – '+ctx[1]:''),
      files:await Promise.all(files.map(async f=>({n:f.name,t:f.type||'application/octet-stream',b64:await b64(f)})))};
    const r=await fetch(API,{method:'POST',body:JSON.stringify({ten:'gt',fn:'ajanlatkeres',args:[o]}),credentials:'omit',redirect:'follow'});
    const j=await r.json();ok=!!(j&&!j.err);if(!ok&&j&&j.err)err.textContent=String(j.err);
"""
js = js.replace(old_try, new_try)
js = rep(js, 'Kérjük, írjon közvetlenül az <b>info@generalteam.hu</b> címre, vagy hívjon minket: <b>+36 1 226 47 35</b>.',
             'Kérjük, írjon közvetlenül az <b>info@generalteam.hu</b> címre, vagy hívjon minket: <b>+36 70 627 67 06</b>.')
js = js.replace("const lb=document.getElementById('lb')", "const lb=document.getElementById('ailb')")
for bad in ['angol', 'Angol', '226 47 35', 'Pannonhalmi út 39', 'GAS_URL', 'Baradla', 'baradla']:
    assert bad not in js, 'tiltott szöveg a JS-ben: ' + bad

# ---------- HTML törzs ----------
lbhtml = s[s.find('<div class="lb" id="lb"'):s.find('<section class="block" id="referenciak">')].strip()
lbhtml = lbhtml.replace('class="lb" id="lb"', 'class="ailb" id="ailb"')
lbhtml = re.sub(r'class="lb-', 'class="ailb-', lbhtml)

main = f'''<div class="phero"><div class="grid-bg" aria-hidden="true"></div><div class="wrap"><p class="crumb"><a href="index.html">Kezdőlap</a> / <a href="szolgaltatasok.html">Szolgáltatások</a> / Új lakások</p><h1>Új építésű lakások Budán, Sasadon</h1><p class="lead">Fejlesztő-kivitelező partnerünkkel közösen kínálunk új építésű, kulcsrakész lakásokat a XI. kerületben. Minden kérdéssel hozzánk fordulhat: alaprajz, műszaki tartalom, ár, megtekintés – mi egyeztetünk Ön helyett.</p></div></div>
<div class="aiw">
<section class="block" id="menete"><div class="wrap">
  <div class="label">Így működik</div>
  <h2 style="margin-top:12px">Lakásválasztás három lépésben</h2>
  <div class="rule"></div>
  <div class="how">
    <div><span class="n">1</span><b>Válasszon lakást</b><span>Lent minden lakásnál megnézheti az alaprajzot, a helyiségeket, a teraszt vagy erkélyt és a bruttó árat.</span></div>
    <div><span class="n">2</span><b>Írjon nekünk</b><span>Az űrlapon elküldheti kérdéseit; ha egyedi átalakítást szeretne, csatolhat vázlatot vagy fotót is.</span></div>
    <div><span class="n">3</span><b>Mi intézzük a többit</b><span>Egyeztetjük a megtekintést, a műszaki tartalmat és a módosítási igényeket, és végig mi tartjuk Önnel a kapcsolatot.</span></div>
  </div>
  <div class="gk"><p><b>Nem kész lakást keres, hanem építene?</b> Családi ház, társasház vagy teljes felújítás generálkivitelezését is vállaljuk, ugyanezzel a szakmai háttérrel: tervezéstől a kulcsátadásig.</p><a class="btn" href="szolgaltatasok.html">Generálkivitelezés</a></div>
</div></section>

<section class="block" id="lakasok"><div class="wrap">
  <div class="sechead">
    <div>
      <div class="label">Budapest XI., Sasad</div>
      <h2 style="margin-top:12px">Elérhető lakások</h2>
      <div class="rule"></div>
    </div>
    <p class="sechead-note">Kattintson egy lakásra: megjelenik az alaprajza, a helyiséglistája és az ára. Az alaprajz nagyítható.</p>
  </div>
  <div id="projects"><!--PRE:projects--></div>
  <p class="note">Bruttó árak. A helyiségek területei az engedélyezési tervek szerinti nettó értékek; a lakás hivatalos alapterülete a lista fölött látható. A pontos címet és a műszaki leírást érdeklődés után küldjük el.</p>
</div></section>

{lbhtml}

<section class="block" id="referenciak"><div class="wrap">
  <div class="label">A partner munkái</div>
  <h2 style="margin-top:12px">Megépült társasházak és épületek</h2>
  <div class="rule"></div>
  <p style="margin-top:18px">Fejlesztő-kivitelező partnerünk 2006 óta épít Budán: társasházakat, családi házakat, gazdasági épületeket és vasbeton szerkezeteket. Néhány elkészült munkája:</p>
  <div class="refs" id="refCats"><!--PRE:refCats--></div>
  <h3 class="gal-title">Társasházak</h3>
  <div class="gallery" id="galTarsashaz"><!--PRE:galTarsashaz--></div>
  <h3 class="gal-title">Családi házak</h3>
  <div class="gallery" id="galCsaladi"><!--PRE:galCsaladi--></div>
  <div class="clients">
    <span class="label">Megrendelők között</span>
    <span>Csepeli Szabadkikötő</span><span>BSZL Logisztika</span><span>Masped Logisztika</span><span>Állatorvosi Egyetem</span><span>Lavet Gyógyszergyár</span>
  </div>
</div></section>

<section class="block" id="kapcsolat"><div class="wrap">
  <div class="cgrid">
    <div>
      <div class="label">Érdeklődés, megtekintés</div>
      <h2 style="margin-top:12px">Kérdezzen tőlünk</h2>
      <div class="rule"></div>
      <div style="margin-top:20px">
        <div class="cline"><small>Telefon · hétköznap 8–17</small><span><a href="tel:+36706276706">+36 70 627 67 06</a></span></div>
        <div class="cline"><small>E-mail</small><span><a href="mailto:info@generalteam.hu">info@generalteam.hu</a></span></div>
      </div>
      <p style="margin-top:18px">Az érdeklődését a GeneralTeam fogadja, és mi egyeztetünk a fejlesztővel. Hamarosan jelentkezünk a részletekkel és a megtekintési lehetőségekkel.</p>
    </div>
    <form id="f" name="kapcsolat" novalidate>
      <p class="hp" aria-hidden="true"><label>Weboldal <input name="website" tabindex="-1" autocomplete="off"></label></p>
      <h3>Üzenet küldése</h3>
      <label for="topic">Miben segíthetünk?
        <select id="topic" name="topic">
          <option>Új lakás – érdeklődés</option>
          <option>Új lakás – megtekintés</option>
          <option>Generálkivitelezés / árajánlat</option>
          <option>Felújítás, tetőtér-beépítés</option>
          <option>Egyéb</option>
        </select>
      </label>
      <div class="row2">
        <label for="name">Név<input id="name" name="name" autocomplete="name" placeholder="Kovács Anna"></label>
        <label for="phone">Telefon<input id="phone" name="phone" type="tel" autocomplete="tel" placeholder="+36 30 123 4567"></label>
      </div>
      <label for="email">E-mail<input id="email" name="email" type="email" autocomplete="email" placeholder="anna@pelda.hu"></label>
      <label for="msg">Üzenet<textarea id="msg" name="message" placeholder="Írja le röviden, mit szeretne."></textarea></label>
      <div class="field">
        <span class="flabel">Csatolmányok <small>(nem kötelező)</small></span>
        <label class="dropzone" id="dropzone" for="files">
          <input type="file" id="files" multiple accept=".pdf,.jpg,.jpeg,.png,.heic,.doc,.docx,.xls,.xlsx,.dwg,.dxf,.zip">
          <span><strong>Húzza ide a fájlokat</strong> vagy kattintson a tallózáshoz</span>
          <small>Vázlat, fotó, terv · PDF, JPG, PNG, DOCX, XLSX, DWG, ZIP · legfeljebb 5 fájl, fájlonként 10 MB, összesen 20 MB</small>
        </label>
        <ul class="filelist" id="filelist"></ul>
        <p class="ferr" id="fileerr" role="alert"></p>
      </div>
      <label class="consent" for="gdpr"><input type="checkbox" id="gdpr" name="gdpr" value="igen"> Hozzájárulok, hogy a General Contractor Team Kft. az adataimat az érdeklődésem megválaszolásához kezelje, és ehhez az érintett ingatlan fejlesztőjének továbbítsa. <a href="adatvedelem.html" target="_blank" rel="noopener">Adatkezelési tájékoztató</a></label>
      <p class="ferr" id="formerr" role="alert"></p>
      <button class="btn" type="submit">Üzenet küldése</button>
      <div class="sent" id="sent" hidden></div>
    </form>
  </div>
</div></section>
</div>'''

# ---------- sablon ----------
head_title = '<title>Új lakások Budán, Sasadon – eladó új építésű lakások | GeneralTeam</title>'
desc = ('<meta name="description" content="Új építésű, kulcsrakész lakások Budapest XI. kerületében, Sasadon: alaprajzok, '
        'helyiséglisták, árak. Érdeklődés és megtekintés a GeneralTeamnél – generálkivitelezés tervezéstől a kulcsátadásig.">\n'
        '<link rel="canonical" href="https://generalteam.hu/uj-lakasok.html">\n'
        '<meta property="og:title" content="Új lakások Budán, Sasadon | GeneralTeam">\n'
        '<meta property="og:type" content="website"><meta property="og:url" content="https://generalteam.hu/uj-lakasok.html">\n'
        f'<meta property="og:image" content="https://generalteam.hu/{DIR}/p1.jpg">')
page = tpl
page = re.sub(r'<title>.*?</title>', head_title, page, count=1)
page = re.sub(r'<meta name="description"[^>]*>', desc, page, count=1)
page = page.replace('</head>', '<style>\n' + css + '\n</style>\n</head>', 1)
page = re.sub(r'<main id="top">.*?</main>', lambda m: '<main id="top">\n' + main + '\n</main>', page, count=1, flags=re.S)
# sablon saját (kókai) scriptjei nem kellenek; a lábléc + évszám marad
foot_end = page.find('<script>document.getElementById("yr")')
foot_end = page.find('</script>', foot_end) + 9
page = page[:foot_end] + '\n<script>\n' + js + '\n</script>\n</body>\n</html>\n'
page = page.replace('<a class="btn brass" href="#ajanlatkeres">', '<a class="btn brass" href="#kapcsolat">')
for bad in ['angolinvest', 'Angol Invest', 'Baradla', 'Lanka utca 17', '226 47 35', 'Kókai Zsófia', 'id="kfr"']:
    assert bad not in page, 'tiltott szöveg az oldalon: ' + bad

open(os.path.join(OUT, 'uj-lakasok.html'), 'w', encoding='utf-8').write(page)

os.makedirs(os.path.join(OUT, DIR), exist_ok=True)
for src, dst in imgmap.items():
    shutil.copyfile(os.path.join(IMG, src), os.path.join(OUT, DIR, dst))
import subprocess
subprocess.run(['node','/home/claude/prerender_gt.js',os.path.join(OUT,'uj-lakasok.html')],check=True)
print('kész:', len(imgmap), 'kép,', len(page) // 1024, 'kB')
