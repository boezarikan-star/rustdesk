#!/usr/bin/env python3
# Compendus Remote Branding
import re, sys, glob, os

APPLY = "--apply" in sys.argv
NEW = "Compendus Remote"
APPNAME = "Compendus-Remote"
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

edit("libs/hbb_common/src/config.rs", [
    ('RwLock::new("RustDesk".to_owned());', 'RwLock::new("%s".to_owned());' % APPNAME),
    ('pub const RENDEZVOUS_SERVERS: &[&str] = &["rs-ny.rustdesk.com"];',
     'pub const RENDEZVOUS_SERVERS: &[&str] = &["%s"];' % SERVER),
    ('pub const RS_PUB_KEY: &str = "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw=";',
     'pub const RS_PUB_KEY: &str = "%s";' % PUBKEY),
])

edit("flutter/windows/runner/Runner.rc", [
    ('VALUE "FileDescription", "RustDesk Remote Desktop" "\\0"', 'VALUE "FileDescription", "Compendus Remote" "\\0"'),
    ('VALUE "InternalName", "rustdesk" "\\0"', 'VALUE "InternalName", "Compendus Remote" "\\0"'),
    ('VALUE "OriginalFilename", "rustdesk.exe" "\\0"', 'VALUE "OriginalFilename", "Compendus Remote.exe" "\\0"'),
    ('VALUE "ProductName", "RustDesk" "\\0"', 'VALUE "ProductName", "Compendus Remote" "\\0"'),
], must=False)

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
print("Sprachdateien: %d  Werte: %d  Keys: %d" % (files, total, keyhits))
print("FERTIG (%s)." % ("ANGEWENDET" if APPLY else "VORSCHAU"))
