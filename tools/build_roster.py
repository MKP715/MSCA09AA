# -*- coding: utf-8 -*-
"""
data/trusted-servants.csv — built from every tab of the Panel 76 Teammates workbook.

Tabs covered: P 76 Board, P 76 DCMCs, P 76 Com. Chairs, D6, D8, D12, D14, D15
(both sheets), D18, D30, Distrito 20-25, YPAA, P74 Board, P74 DCMCs,
P74 Comm. Chairs.

Deliberately NOT published: the "P76 - Get to know you!" tab (personal
introductions), the "zoom schedule" tab (covered by data/calendar.ics), and
every personal e-mail address, phone number, sobriety date and home group in
the workbook.

ANONYMITY (Traditions 11 & 12, and the Ad Hoc Website Committee's P1 finding):
first name + last initial only; contact through a role-based service address.
"""
import csv, io, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "data", "trusted-servants.csv")

HEADER = ["panel", "level", "body", "body_sort", "position", "position_sort",
          "name", "language", "email", "email_alt", "website", "status", "notes"]

rows = []


def add(panel, level, body, body_sort, position, name, language,
        email="", email_alt="", website="", notes="", position_sort=None):
    rows.append(dict(
        panel=panel, level=level, body=body, body_sort=body_sort,
        position=position,
        position_sort=position_sort if position_sort is not None
        else len([r for r in rows if r["body"] == body and r["panel"] == panel]) + 1,
        name=name, language=language, email=email, email_alt=email_alt,
        website=website, status="Vacant" if not name else "Filled", notes=notes))


# ══════════════════════════════ PANEL 76 ═══════════════════════════════════
# ── Area officers ("P 76 Board") ───────────────────────────────────────────
B = "Area Officers"
add("76", "Area", B, 10, "Delegate", "Debra L.", "English",
    "P76delegatemsca09@gmail.com", "delegate@msca09aa.org")
add("76", "Area", B, 10, "Alternate Delegate", "Tara F.", "English",
    "delegatealt@msca09aa.org", "msca09.altdelegate@gmail.com")
add("76", "Area", B, 10, "Chairperson", "Eric G.", "English",
    "msca09chair@gmail.com", "chair@msca09aa.org")
add("76", "Area", B, 10, "Treasurer (A/P)", "Vicki R.", "English", "treasurerap@msca09aa.org")
add("76", "Area", B, 10, "Treasurer (A/R)", "Martin J.", "English", "treasurerar@msca09aa.org")
add("76", "Area", B, 10, "Registrar", "Charles A.", "English",
    "registrar@msca09aa.org", "mscaa09p76registrar@gmail.com")
add("76", "Area", B, 10, "Secretary", "Brian S.", "English", "secretary@msca09aa.org")

# ── Area standing committees ("P 76 Com. Chairs") ──────────────────────────
C = "Area Standing Committees"
COMMITTEES = [
    # position, name, language, email, email_alt
    ("Accessibilities",                                  "Bob K.",        "English", "accessibilitieschair@msca09aa.org", ""),
    ("Accesibilidades",                                  "",              "Spanish", "accessibilitieschair-es@msca09aa.org", ""),
    ("Archives",                                         "Todd W.",       "English", "archiveschair@msca09aa.org", ""),
    ("Archivist",                                        "",              "English", "archivist@msca09aa.org", ""),
    ("Cooperation with the Elder Community (CEC)",       "Lisa Marie P.", "English", "cecchair@msca09aa.org", ""),
    ("Cooperacion con la Comunidad de Ancianos (CEC)",   "Jose F.",       "Spanish", "cecchair@msca09aa.org", ""),
    ("Communications",                                   "",              "English", "communicationschair@msca09aa.org", ""),
    ("Comunicaciones",                                   "Maria P.",      "Spanish", "communicationschair-es@msca09aa.org", ""),
    ("Newsletter Editor",                                "",              "English", "editor@msca09aa.org", ""),
    ("Convention Liaison",                               "Cyndi B.",      "English", "conventionliaison@msca09aa.org", ""),
    ("Enlace de Convencion",                             "",              "Spanish", "conventionliaison-es@msca09aa.org", ""),
    ("Corrections",                                      "Erika D.",      "English", "correctionschair@msca09aa.org", ""),
    ("Correcciones",                                     "",              "Spanish", "correctionschair@msca09aa.org", ""),
    ("Cooperation with the Professional Community (CPC)", "Louis T.",     "English", "cpcchair@msca09aa.org", ""),
    ("Cooperacion con la Comunidad Profesional (CCP)",   "Dario D.",      "Spanish", "cpcchair-es@msca09aa.org", ""),
    ("DCM School",                                       "",              "English", "dcmschoolchair@msca09aa.org", ""),
    ("Escuela de MCD",                                   "Gildardo B.",   "Spanish", "dcmschoolchair-es@msca09aa.org", ""),
    ("Finance",                                          "Alan D.",       "English", "financechair@msca09aa.org", ""),
    ("Grapevine",                                        "Jennifer J.",   "English", "grapevinechair@msca09aa.org", ""),
    ("La Vina",                                          "Ursula F.",     "Spanish", "lavinachair@msca09aa.org", ""),
    ("Guidelines & Procedures",                          "Spencer D.",    "English", "gapchair@msca09aa.org", ""),
    ("GSR School",                                       "Scott B.",      "English", "gsrschoolchair@msca09aa.org", ""),
    ("Escuela de RSG",                                   "Alejandro G.",  "Spanish", "gsrschoolchair-es@msca09aa.org", ""),
    ("Literature",                                       "Dean C.",       "English", "literaturechair@msca09aa.org", ""),
    ("Literatura",                                       "Abel",          "Spanish", "literaturechair-es@msca09aa.org", ""),
    ("Public Information",                               "",              "English", "pichair@msca09aa.org", ""),
    ("Informacion Publica",                              "",              "Spanish", "pichair-es@msca09aa.org", ""),
    ("Registration",                                     "Teddi P.",      "English", "registrationchair@msca09aa.org", ""),
    ("Registro",                                         "Leopoldo E.",   "Spanish", "registrationchair@msca09aa.org", ""),
    ("Remote Communities",                               "Tony P.",       "English", "remotecommunitieschair@msca09aa.org", ""),
    ("Comunidades Remotas",                              "Mauricio T.",   "Spanish", "remotecommunitieschair-es@msca09aa.org", ""),
    ("Technology",                                       "Teri M.",       "English", "technologychair@msca09aa.org", ""),
    ("Website / Web Servant",                            "Devin",         "English", "webmaster@msca09aa.org", ""),
    ("Treatment",                                        "Daisy F.",      "English", "treatmentchair@msca09aa.org", "area9treatment@gmail.com"),
    ("Tratamiento",                                      "",              "Spanish", "treatmentchair@msca09aa.org", ""),
    ("Young People in A.A. (YPAA)",                      "Marissa S.",    "English", "ypchair@msca09aa.org", ""),
]
for i, (pos, nm, lang, em, alt) in enumerate(COMMITTEES, 1):
    add("76", "Area Committee", C, 20, pos, nm, lang, em, alt, position_sort=i)

# ── Area sub-committees and support roles ──────────────────────────────────
S = "Area Sub-Committees & Support"
SUB = [
    ("Sound",                         "Hugo N.",     "English"),
    ("Inter-District Hispanic Chair", "Adrian G.",   "Spanish"),
    ("Hospitality / Coffee",          "Hypatia L.",  "English"),
    ("Hospitality / Coffee",          "Demetrio T.", "Spanish"),
    ("Hispanic Women's Committee",    "Claudia N.",  "Spanish"),
]
for i, (pos, nm, lang) in enumerate(SUB, 1):
    add("76", "Area Committee", S, 30, pos, nm, lang, "chair@msca09aa.org",
        notes="No dedicated Area address yet — reaches the Area Chairperson.",
        position_sort=i)

# ── YPAA committee ("YPAA" tab) ────────────────────────────────────────────
Y = "Young People in A.A. (YPAA)"
for i, nm in enumerate(["Marissa S.", "Matt", "Hailie W.", "Kevin", "James", "Teddi G."], 1):
    add("76", "Area Committee", Y, 35,
        "Chairperson" if i == 1 else "Committee member",
        nm, "English", "ypchair@msca09aa.org", position_sort=i)

# ── D.C.M.C.s ("P 76 DCMCs") ───────────────────────────────────────────────
DCMC = [
    # district, name, language, email, website
    ("1 & 3", "Richie S.",     "English", "d01dcmc@msca09aa.org", "https://mscadistrict1.org/",       "district1msca09@gmail.com"),
    ("2",     "Carolyne H.",   "English", "d02dcmc@msca09aa.org", "", ""),
    ("4",     "Titus D.",      "English", "d04dcmc@msca09aa.org", "https://longbeachaa.org/", ""),
    ("5",     "Joshua O.",     "English", "d05dcmc@msca09aa.org", "https://district5msca09.com/", ""),
    ("6",     "Cathy L.",      "English", "d06dcmc@msca09aa.org", "https://district6area09.org/", ""),
    ("7",     "Lisa Marie P.", "English", "d07dcmc@msca09aa.org", "", "cecchair@msca09aa.org"),
    ("8",     "Alan D.",       "English", "d08dcmc@msca09aa.org", "", ""),
    ("9",     "Jodi B.",       "English", "d09dcmc@msca09aa.org", "https://www.district9gs.com/", ""),
    ("10",    "Heather S.",    "English", "d10dcmc@msca09aa.org", "", ""),
    ("12",    "Trish G.",      "English", "dcmc@mscadistrict12.org", "https://www.mscadistrict12.org/", "d12dcmc@msca09aa.org"),
    ("14",    "Cyndi B.",      "English", "d14dcmc@msca09aa.org", "", ""),
    ("15",    "Todd W.",       "English", "d15dcmc@msca09aa.org", "https://www.aadistrict15.com/", ""),
    ("17",    "Marissa S.",    "English", "d17dcmc@msca09aa.org", "https://aadistrict17.info/", ""),
    ("18",    "Spencer D.",    "English", "district18dcmc@gmail.com", "", "d18dcmc@msca09aa.org"),
    ("19",    "Daniel H.",     "English", "d19dcmc@msca09aa.org", "", ""),
    ("30",    "Ernesto M.",    "English", "d30dcmc@msca09aa.org", "https://www.district30area09.org/", ""),
    ("20",    "Juan M.",       "Spanish", "d20dcmc@msca09aa.org", "", ""),
    ("21",    "Jorge M.",      "Spanish", "d21dcmc@msca09aa.org", "", ""),
    ("22",    "Maria P.",      "Spanish", "d22dcmc@msca09aa.org", "", ""),
    ("23",    "Ramon D.",      "Spanish", "d23dcmc@msca09aa.org", "", ""),
    ("24",    "Jose E.",       "Spanish", "d24dcmc@msca09aa.org", "", ""),
    ("25",    "Ruben G.",      "Spanish", "d25dcmc@msca09aa.org", "", ""),
]
DIST_MAIL = {}
for num, nm, lang, em, web, alt in DCMC:
    label = ("District %s" % num) if lang == "English" else ("Distrito %s" % num)
    DIST_MAIL[label] = em
    add("76", "District", label, 40, "DCMC" if lang == "English" else "MCD",
        nm, lang, em, alt, web, position_sort=1)

# alternates recorded on the DCMC tab
add("76", "District", "Distrito 20", 40, "Alternate MCD", "Luciano G.", "Spanish",
    "d20dcmc@msca09aa.org", position_sort=2)
add("76", "District", "Distrito 22", 40, "Alternate MCD", "Leopoldo E.", "Spanish",
    "d22dcmc@msca09aa.org", position_sort=2)

# ── district officers (one tab per district) ───────────────────────────────
DISTRICT_TABS = [
    ("District 6", "English", [
        ("Alternate DCMC", "Tony P."), ("District Secretary", "Leif J."),
        ("District Treasurer", "Jennifer L."), ("District Registrar", "Cindy M."),
        ("District GSR Professor", "Drew B."), ("Public Information Chair", "Lucky Lisa"),
    ]),
    ("District 8", "English", [
        ("Alternate DCMC", "Teri M."), ("District Secretary", "Daisy F."),
        ("District Registrar", "Rebecca S."), ("District Treasurer", "Steve R."),
        ("DCM — Redlands / Yucaipa / Mentone", "Michelle G."),
        ("DCM — Moreno Valley", "Kim H."), ("DCM — Corona / Norco", "Sharon K."),
        ("Archives", "Bob H."), ("Coffee", "Olivia P."),
        ("Convention Liaison", "Michelle G."),
        ("Cooperation with the Professional Community", "Ron W."),
        ("Cooperation with the Elder Community", "Jill I."),
        ("Grapevine", "Dean C."), ("H&I Liaison", "Cindy V."),
        ("Intergroup Liaison", "Emily"), ("Literature", "Desiree T."),
        ("YPAA Liaison", "Halie W."), ("Technology", "Teri M."),
    ]),
    ("District 15", "English", [
        ("District Secretary", "Jennifer L."), ("District Treasurer", "Meredith L."),
    ]),
    ("District 30", "English", [
        ("District Secretary", "Celia H."), ("District Treasurer", "Jeff M."),
        ("District Registrar", "Katy P."), ("Intergroup Representative", "Jessica P."),
        ("Grapevine", "Larry F."), ("Literature Chair", "Rashea G."),
        ("G.S.R.", "John L."), ("G.S.R.", "Kim S."), ("G.S.R.", "Tim M."),
        ("G.S.R. for District 22", "Gus"),
    ]),
    ("Distrito 22", "Spanish", [
        ("Secretario", "Aurelio M."), ("Tesorero", "Miguel Z."),
        ("Alt. Tesorero", "Leopoldo E."), ("Comite de Archivos", "Julieta C."),
        ("Alt. Archivos", "Gerardo M."), ("Registrador", "Alejo G."),
        ("Foro Local", "Leopoldo E."),
    ]),
    ("Distrito 23", "Spanish", [
        ("Alt. MCD", "Demetrio T."), ("Secretaria", "Gabriela S."),
        ("Alt. Secretario", "Lico R."), ("Tesorero", "Alfredo V."),
        ("Alt. Tesorero", "Luis G."), ("CCP", "Fabiola P."),
        ("Boletin", "Luis J."), ("Informacion Publica", "Herminio S."),
    ]),
    ("Distrito 24", "Spanish", [
        ("Secretario", "Gabriel T."), ("Alt. Secretaria", "Elvia A."),
        ("Tesorero", "Mario C."), ("Alt. Tesorero", "Fernando T."),
        ("Registradora", "Elvia A."),
    ]),
    ("Distrito 25", "Spanish", [
        ("Alt. MCD", "Benigno M."), ("Secretaria", "Mirian R."),
        ("Tesorero", "Juan H."), ("Alt. Tesorero / Comite La Vina", "Felipe A."),
        ("Registrador", "Alfredo A."), ("Comite de Archivos", "Joel Q."),
        ("Comite Boletin", "Adrian G."),
    ]),
]
for label, lang, people in DISTRICT_TABS:
    for i, (pos, nm) in enumerate(people, 2):
        add("76", "District", label, 40, pos, nm, lang,
            DIST_MAIL.get(label, ""), position_sort=i)

# districts that publish their own role addresses
for i, (pos, nm, em) in enumerate([
        ("Alternate DCMC", "Tom K.",  "altdcmc@mscadistrict12.org"),
        ("District Secretary", "Stan M.", "secretary@mscadistrict12.org"),
        ("District Treasurer", "Cyndi C.", "treasurer@mscadistrict12.org"),
        ("District Registrar", "Dawn M.", "registrar@mscadistrict12.org")], 2):
    add("76", "District", "District 12", 40, pos, nm, "English", em,
        website="https://www.mscadistrict12.org/", position_sort=i)

for i, (pos, nm, em) in enumerate([
        ("Alternate DCMC", "Julia B.", "district18altdcmc@gmail.com"),
        ("District Secretary", "Taylor", "district18gsr@gmail.com"),
        ("District Treasurer", "Phil G.", "district18treasurerarea09@gmail.com"),
        ("District Registrar", "Marco A.", "district18registrar@gmail.com")], 2):
    add("76", "District", "District 18", 40, pos, nm, "English", em, position_sort=i)


# ══════════════════════════════ PANEL 74 ═══════════════════════════════════
# Kept so the previous panel's record is not lost when the old site goes.
P74B = "Area Officers"
for i, (pos, nm, em) in enumerate([
        ("Delegate", "Alex W.", "delegate@msca09aa.org"),
        ("Alternate Delegate", "Manya W.", "delegatealt@msca09aa.org"),
        ("Chairperson", "Rozanne P.", "chair@msca09aa.org"),
        ("Treasurer (A/P)", "Louis T.", "treasurerap@msca09aa.org"),
        ("Treasurer (A/R)", "Ryan W.", "treasurerar@msca09aa.org"),
        ("Registrar", "Martin J.", "registrar@msca09aa.org"),
        ("Secretary", "Ramon R.", "secretary@msca09aa.org")], 1):
    add("74", "Area", P74B, 10, pos, nm, "English", em, position_sort=i)

P74C = "Area Standing Committees"
P74_CHAIRS = [
    ("Audio / Area Sound",                    "Mauricio T.",  "Spanish"),
    ("Accessibilities",                       "",             "English"),
    ("Accesibilidades",                       "Mauricio L.",  "Spanish"),
    ("Archives",                              "Robert H.",    "English"),
    ("Communications",                        "Vicki R.",     "English"),
    ("Cooperation with the Elder Community",  "Cynthia B.",   "English"),
    ("Cooperation with the Professional Community", "Katherine C.", "English"),
    ("Convention Liaison",                    "Angela B.",    "English"),
    ("Corrections",                           "Erica D.",     "English"),
    ("Area Coffee Maker",                     "Ed L.",        "English"),
    ("Registration",                          "Charles A.",   "English"),
    ("Technology",                            "Eric G.",      "English"),
    ("H&I Liaison",                           "",             "English"),
    ("Literature",                            "Debra L.",     "English"),
    ("Literatura",                            "Gildardo B.",  "Spanish"),
    ("Public Information",                    "",             "English"),
    ("Informacion Publica",                   "Blanca L.",    "Spanish"),
    ("Grapevine",                             "Francine W.",  "English"),
    ("Escuela de MCD",                        "Rolando T.",   "Spanish"),
    ("Escuela de RSG",                        "Adrian G.",    "Spanish"),
    ("La Vina",                               "Hector R.",    "Spanish"),
    ("Guidelines & Policies",                 "Don S.",       "English"),
    ("Finance",                               "Carmen M.",    "English"),
    ("DCM School",                            "Deborah A.",   "English"),
    ("Remote Communities",                    "Rob A.",       "English"),
    ("Treatment",                             "Teri M.",      "English"),
    ("Tratamiento",                           "",             "Spanish"),
    ("GSR School",                            "Scott B.",     "English"),
    ("Young People in A.A. (YPAA)",           "Lauren C.",    "English"),
]
for i, (pos, nm, lang) in enumerate(P74_CHAIRS, 1):
    add("74", "Area Committee", P74C, 20, pos, nm, lang, position_sort=i)

P74_DCMC = [
    ("1 & 3", "Eric G.",   "English"), ("2",  "Jane E.",   "English"),
    ("4",     "Angela B.", "English"), ("5",  "Vicki R.",  "English"),
    ("6",     "Rob A.",    "English"), ("7",  "Erica D.",  "English"),
    ("8",     "Sharon K.", "English"), ("9",  "Larry B.",  "English"),
    ("10",    "Alicia B.", "English"), ("12", "Tara F.",   "English"),
    ("14",    "Dawn C.",   "English"), ("15", "Allen T.",  "English"),
    ("17",    "Teddi P.",  "English"), ("18", "Brian S.",  "English"),
    ("30",    "Ernesto M.","English"),
    ("20",    "Erika R.",  "Spanish"), ("21", "Abel G.",   "Spanish"),
    ("22",    "Miguel Z.", "Spanish"), ("23", "Luis J.",   "Spanish"),
    ("24",    "Victor D.", "Spanish"), ("25", "Felipe O.", "Spanish"),
]
for num, nm, lang in P74_DCMC:
    label = ("District %s" % num) if lang == "English" else ("Distrito %s" % num)
    add("74", "District", label, 40, "DCMC" if lang == "English" else "MCD",
        nm, lang, position_sort=1)
for num, nm, pos in [("8", "Stacey J.", "Alternate DCMC"),
                     ("8", "Aran B.", "Alternate DCMC"),
                     ("9", "Juanita Q.", "Alternate DCMC"),
                     ("10", "Alicia B.", "Alternate DCMC"),
                     ("14", "Dawn W.", "Alternate DCMC")]:
    add("74", "District", "District " + num, 40, pos, nm, "English", position_sort=2)

with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=HEADER)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in HEADER})

import collections
print("rows:", len(rows))
print("by panel:", collections.Counter(r["panel"] for r in rows))
print("by level:", collections.Counter(r["level"] for r in rows))
print("vacancies:", sum(1 for r in rows if r["status"] == "Vacant"))
print("bodies:", len({(r["panel"], r["body"]) for r in rows}))
