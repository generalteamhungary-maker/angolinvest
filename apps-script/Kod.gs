/**
 * Angol Invest Kft. – weboldal kapcsolati űrlap (Google Apps Script)
 *
 * Mit csinál: a weboldal űrlapjáról érkező üzenetet
 *   1) e-mailben továbbítja az ERTESITES címre, a csatolmányokkal együtt
 *      (a „Válasz” gomb közvetlenül az érdeklődőnek válaszol),
 *   2) a csatolmányokat elmenti egy Drive-mappába,
 *   3) minden megkeresést felír egy Google-táblázatba,
 *   4) visszaigazoló levelet küld az érdeklődőnek.
 *
 * Telepítés (egyszer):
 *   – Futtasd a „beallitas” függvényt (Futtatás gomb) és engedélyezd a hozzáférést.
 *   – Telepítés → Új telepítés → Webalkalmazás;
 *     Végrehajtás mint: Én · Hozzáférés: Bárki → Telepítés.
 *   – A kapott „/exec” végű linket kell beírni a weboldalba (GAS_URL).
 */

var ERTESITES = 'info@angolinvest.hu';            // ide érkeznek a megkeresések (vesszővel több cím is megadható)
var CEG       = 'Angol Invest Kft.';
var MAPPA_NEV = 'Angol Invest – weboldal megkeresések';
var MAX_FAJL  = 5;
var MAX_OSSZ  = 20 * 1024 * 1024;                 // 20 MB összesen (eredeti méret)

function props_() { return PropertiesService.getScriptProperties(); }

function mappa_() {
  var p = props_(), id = p.getProperty('MAPPA_ID'), f = null;
  if (id) { try { f = DriveApp.getFolderById(id); } catch (e) { f = null; } }
  if (!f) { f = DriveApp.createFolder(MAPPA_NEV); p.setProperty('MAPPA_ID', f.getId()); }
  return f;
}

function tabla_() {
  var p = props_(), id = p.getProperty('TABLA_ID'), ss = null;
  if (id) { try { ss = SpreadsheetApp.openById(id); } catch (e) { ss = null; } }
  if (!ss) {
    ss = SpreadsheetApp.create('Angol Invest – megkeresések');
    var sh = ss.getSheets()[0];
    sh.setName('Megkeresések');
    sh.appendRow(['Időpont', 'Téma', 'Név', 'Telefon', 'E-mail', 'Üzenet', 'Csatolmányok', 'Állapot']);
    sh.setFrozenRows(1);
    sh.getRange('A1:H1').setFontWeight('bold');
    DriveApp.getFileById(ss.getId()).moveTo(mappa_());
    p.setProperty('TABLA_ID', ss.getId());
  }
  return ss.getSheets()[0];
}

/** Egyszer futtatandó a szerkesztőből: létrehozza a mappát és a táblázatot, és elkéri az engedélyeket. */
function beallitas() {
  Logger.log('Mappa: ' + mappa_().getUrl());
  Logger.log('Táblázat: ' + tabla_().getParent().getUrl());
  Logger.log('Mai e-mail keret: ' + MailApp.getRemainingDailyQuota());
}

function esc_(x) {
  return String(x == null ? '' : x).replace(/[&<>"]/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
  });
}
function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

function doGet() { return ContentService.createTextOutput('Angol Invest űrlap – működik.'); }

function doPost(e) {
  var d;
  try { d = JSON.parse(e.postData.contents); } catch (x) { return json_({ ok: false, error: 'Hibás kérés.' }); }
  try { return json_(uzenet_(d || {})); }
  catch (x) { return json_({ ok: false, error: String((x && x.message) || x) }); }
}

function uzenet_(d) {
  if (d.website) return { ok: true };                               // spamcsapda
  var nev = String(d.name || '').trim().slice(0, 120);
  var email = String(d.email || '').trim().slice(0, 160);
  var tel = String(d.phone || '').trim().slice(0, 60);
  var tema = String(d.topic || 'Érdeklődés').trim().slice(0, 100);
  var uzen = String(d.message || '').trim().slice(0, 5000);
  if (!nev) throw new Error('Kérjük, adja meg a nevét.');
  if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new Error('Az e-mail-cím formátuma hibás.');
  if (!email && !tel) throw new Error('Adjon meg e-mail-címet vagy telefonszámot.');
  if (!d.gdpr) throw new Error('A küldéshez fogadja el az adatkezelést.');

  var lock = LockService.getScriptLock(); lock.waitLock(30000);
  try {
    var most = new Date();
    var idoStr = Utilities.formatDate(most, 'Europe/Budapest', 'yyyy-MM-dd HH:mm');
    var blobs = [], linkek = [], ossz = 0;
    var fajlok = (d.files || []).slice(0, MAX_FAJL);
    if (fajlok.length) {
      var almappa = mappa_().createFolder(Utilities.formatDate(most, 'Europe/Budapest', 'yyyy-MM-dd HHmm') + ' ' + nev.slice(0, 40));
      fajlok.forEach(function (f) {
        if (!f || !f.b64) return;
        var bytes = Utilities.base64Decode(f.b64);
        ossz += bytes.length;
        if (ossz > MAX_OSSZ) throw new Error('A csatolmányok együtt legfeljebb 20 MB-osak lehetnek.');
        var b = Utilities.newBlob(bytes, f.t || 'application/octet-stream', String(f.n || 'fajl').slice(0, 120));
        var df = almappa.createFile(b);
        blobs.push(b); linkek.push([df.getName(), df.getUrl()]);
      });
    }

    tabla_().appendRow([idoStr, tema, nev, tel, email, uzen, linkek.map(function (l) { return l[1]; }).join('\n'), 'új']);

    var html = '<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.55;color:#1b1b1b">' +
      '<p>Új megkeresés érkezett az angolinvest.hu weboldalról.</p>' +
      '<table style="border-collapse:collapse">' +
      [['Téma', tema], ['Név', nev], ['Telefon', tel], ['E-mail', email], ['Időpont', idoStr]].map(function (r) {
        return r[1] ? '<tr><td style="padding:3px 14px 3px 0;color:#666">' + r[0] + '</td><td><b>' + esc_(r[1]) + '</b></td></tr>' : '';
      }).join('') + '</table>' +
      (uzen ? '<p style="white-space:pre-line;background:#f4f4f4;padding:12px">' + esc_(uzen) + '</p>' : '') +
      (linkek.length ? '<p><b>Csatolmányok</b> (a levélhez is csatolva):<br>' + linkek.map(function (l) { return '<a href="' + l[1] + '">' + esc_(l[0]) + '</a>'; }).join('<br>') + '</p>' : '') +
      '</div>';
    var o = { to: ERTESITES, subject: 'Weboldal: ' + tema + ' – ' + nev, htmlBody: html, name: CEG + ' weboldal' };
    if (email) o.replyTo = email;
    if (blobs.length && ossz <= 20 * 1024 * 1024) o.attachments = blobs;
    MailApp.sendEmail(o);

    if (email) {
      MailApp.sendEmail({
        to: email, name: CEG, replyTo: ERTESITES.split(',')[0],
        subject: 'Megkaptuk üzenetét – ' + CEG,
        htmlBody: '<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.55">' +
          '<p>Tisztelt ' + esc_(nev) + '!</p><p>Köszönjük megkeresését, megkaptuk. Munkatársunk hamarosan jelentkezik.</p>' +
          '<p>Üdvözlettel:<br>' + CEG + '<br>1118 Budapest, Pannonhalmi út 39. · +36 1 226 47 35 · info@angolinvest.hu</p></div>'
      });
    }
    return { ok: true };
  } finally { lock.releaseLock(); }
}
