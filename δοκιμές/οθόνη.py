#!/usr/bin/env python3
"""δοκιμές/οθόνη.py — drive the interactive screen through a real pty.

This is the ONLY test here written outside Zymbol, and it is the only
one that has to be: `>>|` refuses to start without a TTY and `<<|`
cannot be fed from a pipe, so no golden and no module call can reach
the editor. Everything else — the world, the rule, the end
conditions, the locales, the geometry, the whole command line — is
asserted from Zymbol in δοκιμές/*.zy and decided by their exit codes.

`>>|` refuses to start without a TTY and `<<|` cannot be fed from a
pipe, so the editor is the one part of this program a golden file
cannot reach. This asks it questions a human would: does the status
line say what the world holds, does `n` advance exactly one
generation, does SPACE change the population by one, does ENTER
switch to RUN.

    python3 δοκιμές/οθόνη.py            # both Rust engines
    python3 δοκιμές/οθόνη.py --vm       # just the register VM

Exit status: 0 every case passed, 1 a case failed, 2 could not run.
"""
import os, re, sys, subprocess

ΕΔΩ = os.path.dirname(os.path.abspath(__file__))
ΡΙΖΑ = os.path.dirname(ΕΔΩ)
ΟΔΗΓΟΣ = os.path.join(ΡΙΖΑ, "..", "zyquality", "tui", "ptydrive.py")

sys.path.insert(0, os.path.dirname(os.path.abspath(ΟΔΗΓΟΣ)))
try:
    from ptydrive import run as οδήγησε
except ImportError:
    sys.stderr.write("cannot import zyquality/tui/ptydrive.py — is zyquality/ checked out?\n")
    sys.exit(2)

ZYMBOL = os.environ.get("ZYMBOL_BIN", "zymbol")


def καθάρισε(κείμενο):
    """Strip ANSI so a test can look for text rather than for escapes."""
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]|\x1b[()][B0]|\x1b[=>]", "", κείμενο)


def τρέξε(μηχανή, ορίσματα, πλήκτρα, rows=24, cols=80, ΕΙΣΟΔΟΣ="ζωή.zy"):
    εντολή = [ZYMBOL, "run"]
    if μηχανή == "zyvm":
        εντολή.append("--vm")
    εντολή.append(os.path.join(ΡΙΖΑ, ΕΙΣΟΔΟΣ))
    εντολή += ορίσματα
    return καθάρισε(οδήγησε(εντολή, πλήκτρα, rows=rows, cols=cols))


ΠΕΡΙΠΤΩΣΕΙΣ = [
    # name, entry file, args, keys, substrings that must appear
    ("ξεκινά σε ΣΥΝΤΑΞΗ με το σχήμα στη θέση του", "ζωή.zy",
     ["-p", "glider", "-r", "10", "-c", "10", "-t", "ascii"],
     [b"q"],
     ["ΣΥΝΤΑΞΗ", "γενιά 0", "5 ζωντανά", "10×10 τόρος", "B3/S23", "ολισθητής"]),

    ("το n προχωρά ακριβώς μία γενιά", "ζωή.zy",
     ["-p", "blinker", "-r", "10", "-c", "10", "-t", "ascii"],
     [b"n", b"q"],
     ["γενιά 1", "3 ζωντανά"]),

    ("το SPACE αλλάζει το κύτταρο κάτω από τον δρομέα", "ζωή.zy",
     ["-r", "10", "-c", "10", "-t", "ascii"],
     [b" ", b"q"],
     ["1 ζωντανό"]),

    ("το ↵ περνά σε ΤΡΕΧΕΙ", "ζωή.zy",
     ["-p", "glider", "-r", "10", "-c", "10", "-t", "ascii", "-d", "500"],
     [b"\r", b"q"],
     ["ΤΡΕΧΕΙ"]),

    ("ένα ψηφίο πατάει σχήμα", "ζωή.zy",
     ["-r", "16", "-c", "16", "-t", "ascii"],
     [b"1", b"q"],
     ["4 ζωντανά", "τετράγωνο"]),

    ("το p ανοίγει τον κατάλογο σχημάτων", "ζωή.zy",
     ["-r", "16", "-c", "40", "-t", "ascii"],
     [b"p", b"q"],
     ["Διάλεξε σχήμα", "τετράγωνο", "κανόνι"]),

    # Δύο ↓ από το block φτάνουν στο loaf, που είναι το τρίτο της
    # λίστας και έχει 7 κύτταρα. Η σειρά είναι η σειρά κατηγορίας
    # του πυρήνας/σχήματα.zy, όχι αλφαβητική.
    ("ο κατάλογος διαλέγει και τοποθετεί", "ζωή.zy",
     ["-r", "16", "-c", "40", "-t", "ascii"],
     [b"p", b"\x1b[B", b"\x1b[B", b"\r", b"q"],
     ["7 ζωντανά", "καρβέλι"]),

    ("το l ανοίγει τον κατάλογο γλωσσών, με κάθε όνομα στη γλώσσα του", "ζωή.zy",
     ["-r", "12", "-c", "40", "-t", "ascii"],
     [b"l", b"q"],
     ["Διάλεξε γλώσσα", "Ελληνικά", "Español", "English"]),

    ("η γλώσσα αλλάζει μέσα στο παιχνίδι", "ζωή.zy",
     ["-p", "block", "-r", "12", "-c", "40", "-t", "ascii"],
     [b"l", b"\x1b[B", b"\r", b"q"],
     ["EDITAR", "bloque", "4 células vivas"]),

    ("το + μισιάζει την καθυστέρηση", "ζωή.zy",
     ["-r", "10", "-c", "10", "-t", "ascii", "-d", "200"],
     [b"+", b"q"],
     ["100 ms"]),

    ("ένας ταλαντωτής σταματά μόνος του και λέει γιατί", "ζωή.zy",
     ["-p", "blinker", "-r", "10", "-c", "10", "-t", "ascii", "-d", "20", "--run"],
     [b"q"],
     ["ΤΕΛΟΣ", "ταλαντώνεται", "περίοδο 2"]),

    ("ένα ακίνητο σχήμα παγώνει και το λέει", "ζωή.zy",
     ["-p", "block", "-r", "10", "-c", "10", "-t", "ascii", "-d", "20", "--run"],
     [b"q"],
     ["ΤΕΛΟΣ", "πάγωσε"]),

    ("το όριο γύρων σταματά το τρέξιμο", "ζωή.zy",
     ["-p", "glider", "-r", "12", "-c", "12", "-t", "ascii", "-d", "20", "-n", "3", "--run"],
     [b"q"],
     ["ΤΕΛΟΣ", "γενιά 3/3"]),

    ("η γραμμή βοήθειας δείχνει την έξοδο", "ζωή.zy",
     ["-r", "10", "-c", "10", "-t", "ascii"],
     [b"q"],
     ["έξοδος"]),

    ("το σημείο εισόδου διαλέγει τη γλώσσα της πρώτης οθόνης", "vida.zy",
     ["-p", "block", "-r", "10", "-c", "10", "-t", "ascii"],
     [b"q"],
     ["EDITAR", "4 células vivas", "bloque"]),

    ("και στα χίντι, με τα δικά της ψηφία", "जीवन.zy",
     ["-p", "block", "-r", "10", "-c", "10", "-t", "ascii"],
     [b"q"],
     ["संपादन", "कोशिकाएँ जीवित", "खंड", "१०×१०"]),
]


def main():
    μηχανές = ["zytw", "zyvm"]
    if "--vm" in sys.argv:
        μηχανές = ["zyvm"]
    if "--tw" in sys.argv:
        μηχανές = ["zytw"]
    αναλυτικά = "-v" in sys.argv

    αποτυχίες = 0
    for μηχανή in μηχανές:
        print(f"── {μηχανή} " + "─" * 50)
        for όνομα, είσοδος, ορίσματα, πλήκτρα, αναμενόμενα in ΠΕΡΙΠΤΩΣΕΙΣ:
            οθόνη = τρέξε(μηχανή, ορίσματα, πλήκτρα, ΕΙΣΟΔΟΣ=είσοδος)
            λείπουν = [α for α in αναμενόμενα if α not in οθόνη]
            if λείπουν:
                αποτυχίες += 1
                print(f"  FAIL  {όνομα}")
                print(f"        missing: {λείπουν}")
                if αναλυτικά:
                    for γρ in οθόνη.splitlines()[:8]:
                        print(f"          |{γρ}")
            else:
                print(f"  ok    {όνομα}")
    print()
    if αποτυχίες:
        print(f"{αποτυχίες} case(s) failed")
        return 1
    print("all cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
