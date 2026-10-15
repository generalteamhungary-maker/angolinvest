# Angol Invest Kft. – weboldal

Statikus weboldal (GitHub Pages). A kapcsolati űrlap egy Google Apps Script webalkalmazásnak küld
(„Angol Invest – weboldal űrlap”, a generalteamhungary Google-fiókban), amely e-mailben továbbítja
az üzenetet és a csatolmányokat az info@angolinvest.hu címre, és felírja egy Google-táblázatba.

- Lakások, árak, állapotok: `index.html`, a `const PROJECTS` részben (`sold:true` = Elkelt).
- Űrlap végpont: `index.html`, `const GAS_URL`.
- Az Apps Script forráskódja: `apps-script/Kod.gs`.
