#!/usr/bin/env python3
# ============================================================================
#  Compendus Remote - Komplettes Branding eines frischen RustDesk-Forks.
#  Im Wurzelverzeichnis des Forks ausfuehren (mit Submodul hbb_common!):
#      git clone --recurse-submodules <dein-fork> && cd <fork>
#      python3 brand-all.py --apply
#  Macht aus "RustDesk" ueberall "Compendus Remote": Verzeichnis, Dienst, Exe,
#  Konfig-Ordner, Verknuepfungen, Firewall (ueber APP_NAME), Serveradresse+Key
#  fest einkompiliert, alle sichtbaren Texte, EXE-Metadaten und "Info"-Attribution.
# ============================================================================
import re, sys, glob, os

APPLY = "--apply" in sys.argv
NEW = "Compendus Remote"
SERVER = "rd.compendus.com"
PUBKEY = "kHHHF5NmyguOcvoxM9dTpPsBNjh42Om9yEJZoIOcjrU="

def edit(path, pairs, must=True):
    if not os.path.exists(path):
        print("  ! fehlt:", path); return
    s = open(path, encoding="utf-8").read(); o = s
    for a, b in pairs:
        if a in s:
            s = s.replace(a, b)
        elif must:
            print("  ! nicht gefunden in %s: %s" % (path, a[:60]))
    if APPLY and s != o:
        open(path, "w", encoding="utf-8").write(s)
    print("  %-55s %s" % (path, "geaendert" if s != o else "unveraendert"))

print("== 1) Kern (hbb_common/config.rs): APP_NAME + Server + Key ==")
edit("libs/hbb_common/src/config.rs", [
    ('RwLock::new("RustDesk".to_owned());', 'RwLock::new("%s".to_owned());' % NEW),
    ('pub const RENDEZVOUS_SERVERS: &[&str] = &["rs-ny.rustdesk.com"];',
     'pub const RENDEZVOUS_SERVERS: &[&str] = &["%s"];' % SERVER),
    ('pub const RS_PUB_KEY: &str = "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw=";',
     'pub const RS_PUB_KEY: &str = "%s";' % PUBKEY),
])

print("== 2) EXE-Metadaten (Runner.rc) ==")
edit("flutter/windows/runner/Runner.rc", [
    ('VALUE "FileDescription", "RustDesk Remote Desktop" "\\0"', 'VALUE "FileDescription", "Compendus Remote" "\\0"'),
    ('VALUE "InternalName", "rustdesk" "\\0"', 'VALUE "InternalName", "Compendus Remote" "\\0"'),
    ('VALUE "OriginalFilename", "rustdesk.exe" "\\0"', 'VALUE "OriginalFilename", "Compendus Remote.exe" "\\0"'),
    ('VALUE "ProductName", "RustDesk" "\\0"', 'VALUE "ProductName", "Compendus Remote" "\\0"'),
], must=False)

print("== 3) Info/Ueber-Attribution (Powered by RustDesk + AGPL) ==")
edit("flutter/lib/desktop/pages/desktop_setting_page.dart", [
    ("""              SelectionArea(
                  child: Text('${translate('ID')}: $myId')
                      .marginSymmetric(vertical: 4.0)),
              InkWell(
                  onTap: () {
                    launchUrlString('https://rustdesk.com/privacy.html');""",
     """              SelectionArea(
                  child: Text('${translate('ID')}: $myId')
                      .marginSymmetric(vertical: 4.0)),
              SelectionArea(
                  child: Text('Powered by RustDesk (AGPL-3.0)')
                      .marginSymmetric(vertical: 4.0)),
              SelectionArea(
                  child: Text('© Compendus Bilisim Ltd. Sti. Türkiye')
                      .marginSymmetric(vertical: 4.0)),
              InkWell(
                  onTap: () {
                    launchUrlString('https://rustdesk.com/privacy.html');"""),
], must=False)

print("== 4) Sichtbare Texte (src/lang/*.rs): Werte -> Compendus Remote, Keys bleiben ==")
pat = re.compile(r'^(\s*\(\s*"(?:[^"\\]|\\.)*"\s*,\s*")((?:[^"\\]|\\.)*)("\s*\)\s*,?\s*)$')
total = 0; files = 0; keyhits = 0
for f in glob.glob("src/lang/*.rs"):
    files += 1; out = []; ch = 0
    for line in open(f, encoding="utf-8"):
        m = pat.match(line.rstrip("\n"))
        if m:
            kp, val, tail = m.group(1), m.group(2), m.group(3)
            keyhits += kp.count("RustDesk")
            if "RustDesk" in val:
                ch += val.count("RustDesk"); val = val.replace("RustDesk", NEW)
            out.append(kp + val + tail + "\n")
        else:
            out.append(line)
    total += ch
    if APPLY and ch:
        open(f, "w", encoding="utf-8").write("".join(out))
print("  Sprachdateien: %d  Werte ersetzt: %d  Keys unveraendert: %d" % (files, total, keyhits))

print()
print("FERTIG (%s)." % ("ANGEWENDET" if APPLY else "VORSCHAU - mit --apply anwenden"))
print("Noch per Hand: Icons ersetzen (res/icon.ico, res/tray-icon.ico,")
print("  flutter/windows/runner/resources/app_icon.ico, flutter/assets/*.png).")
print("Danach committen und ueber GitHub Actions bauen (siehe WEG2-BUILD-ANLEITUNG.md).")
