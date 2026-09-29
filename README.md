# GoL — Το Παιχνίδι της Ζωής

[English](README.md) · [Español](README_ES.md)

Conway's [Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) as a
full-screen terminal editor and simulator, in **four languages** — Ελληνικά,
Español, English, हिन्दी — written in [Zymbol](https://zymbol-lang.org) v0.0.9.

```bash
zymbol run ζωή.zy                     # ελληνικά
zymbol run vida.zy                    # español
zymbol run life.zy                    # english
zymbol run जीवन.zy                    # हिन्दी
```

Mark the starting cells with the cursor, press ENTER, and watch. Press `l` at any
moment to change language — including in the middle of a run.

---

## Why this exists

Not as a demo. It began as a **measuring bench**: its job was to say what one
generation of Life costs in each Zymbol engine, and to record what the language
did and did not make easy. Findings: [HALLAZGOS.md](HALLAZGOS.md). Numbers:
[`μέτρηση/`](μέτρηση/).

Since **2026-09-29** it is a Language-Driven Validation project, the ninth
(`zymbol-design/LDV.md` § 5.1). It was held back at first on purpose — LDV § 6
says the method *"scales with domain distance, not with size"*, and this is the
fifth terminal grid game after 囲碁, चतुरङ्गम्, Serpiente and Hov veS — and
escalated because its findings earned it: the distance that paid was not the grid
but an application testing itself from inside the language. The last section of
HALLAZGOS.md has the argument. Its suite is in the gate as `gol`
(`zyquality/project/apps.toml`), and it is the one application there that agrees
under all three engines.

---

## The screen

```
▸ ΤΡΕΧΕΙ    γενιά 6/24   41 ζωντανά   8×40 τόρος   B3/S23   150 ms   κανόνι του Gosper
────────────────────────────────────────────────────────────────────────────────
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟩🟩⬛⬛⬛⬛⬛⬛🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟩🟩⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟩⬛⬛⬛🟩⬛⬛⬛⬛🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟩🟩⬛⬛⬛
────────────────────────────────────────────────────────────────────────────────
↑↓←→ κίνηση  SPACE άλλαξε  ↵ τρέξε/στοπ  n βήμα  p σχήμα  c σβήσε  q έξοδος
```

Every word of that is from the locale, and every width is measured: the status
line, the help line and the menus are rebuilt for whatever language is active,
and the help line drops trailing entries rather than truncating past the key that
quits.

| Key | Does |
|-----|------|
| `↑ ↓ ← →` | move the cursor (it wraps) |
| `SPACE` | toggle the cell under the cursor |
| `↵` | run / stop — and, at the end, reset and re-arm |
| `n` | advance exactly one generation |
| `p` | **open the pattern catalogue** (all 18, by category) |
| `1`–`9` | stamp one of nine shortcut patterns at the cursor |
| `c` `r` | clear / fill at random |
| `t` | next theme — `emoji`, `block`, `ascii` |
| `l` | **change language**, at any moment |
| `+` `-` | halve / double the delay |
| `q` | quit |

The world can be edited **while it runs** — Life has no setup phase, and a mode
switch would have invented one.

### It stops on its own

Life never ends, so the program has to know when there is no point continuing. It
keeps the last 16 generations and stops when the world **dies out**, **freezes**,
or **repeats a frame it has already shown** — naming the period:

```
■ ο κόσμος ταλαντώνεται με περίοδο 15, από τη γενιά 15   ·   ↵ τρέξε/στοπ   q έξοδος
```

16 because the pentadecathlon has period 15 and is the longest cycle you meet
without looking for it. A glider is **not** a stop: it repeats its shape every 4
generations in a different place, and a shape that is travelling has not stopped.
`-n N` adds a turn limit on top, so a growing pattern also ends.

### The world never exceeds the screen

Whatever you ask for, the world is cut to what fits — and it says so. A grid wider
than the terminal would be drawn half, and the cells you cannot see still count
neighbours: what you would be watching would not be Life.

```bash
$ zymbol run vida.zy -r 200 -c 200 -p glider -b -n 3
21×40 toro  B3/S23  glider (planeador)
el mundo se ajustó a la pantalla
```

---

## Patterns

All eighteen are in the `p` catalogue, grouped by what they are:

| Category | Patterns |
|---|---|
| **still life** | block · beehive · loaf · boat · tub |
| **oscillator** | blinker · toad · beacon · pulsar (p3) · pentadecathlon (p15) |
| **spaceship** | glider · lwss · mwss · hwss |
| **methuselah** | rpentomino · diehard (dies at gen 130) · acorn |
| **gun** | gosper (first glider at gen 30) |

Every one of those parenthesised facts is asserted by
[`δοκιμές/κόσμος.zy`](δοκιμές/κόσμος.zy) against the literature, not against a
previous run.

---

## Options

```bash
zymbol run ζωή.zy -- --help          # `--` first: -h/--help never reach a program
```

| Flag | Means |
|---|---|
| `-r, --rows N` / `-c, --cols N` | world size (capped to the screen) |
| `-p, --pattern NAME` | start from a named pattern, centred |
| `-R, --rule RULE` | `B3/S23` (default), `B36/S23` (HighLife), `B2/S` (Seeds), … |
| `-t, --theme NAME` | `emoji` (default), `block`, `ascii` |
| `-d, --delay MS` | milliseconds per generation |
| `-x, --random` / `-s, --seed N` | random start, reproducible from its seed |
| `-e, --edges` | the world has edges (default: it is a torus) |
| `-n, --turns N` | stop after N generations |
| `--run` | start running instead of editing |
| `-b, --batch` | run with no screen at all and report |
| `--every K` / `--print` / `--time` | with `--batch`; `--time` adds the elapsed milliseconds |
| `-L, --lang CODE` | `el` `es` `en` `hi` |
| `-l, --list` | patterns, themes and languages |

**The flags are ASCII and English while everything inside the program is Greek.**
A command line is the one surface written for a *machine* to read back — a shell, a
Makefile, a CI job — which is the same rule `std/time::format` follows when it
refuses the numeral mode. It is not a hypothetical constraint: `μέτρηση/όλα.zy`
builds shell command lines with `<\ … \>` to start the other engines, and every
one of them is ASCII — a size, a generation count, a path. Greek is fine in a
Zymbol identifier and a syntax error in a shell variable name.

---

## The four languages

Built against `zymbol-design/USERAPPI18N.md`, all
fourteen checklist items:

- **The locale is module state, never a parameter.** Not one function in this
  project takes a language argument (§1, §2).
- **The keys are Greek** — the language the program is written in — with a domain
  prefix on every one (`τέλος.ακίνητο`, never `ακίνητο`), which is what keeps
  *"translation equals key means missing"* decidable in Greek too (§3).
- **Sentences with numbers are locale functions**, not concatenation at the call
  site: `φράση_πληθυσμού`, `φράση_τέλους`, `φράση_κόσμου`, `φράση_ρυθμού` (§4).
- **Every width goes through `std/term::width`**, via a Greek re-export layer
  ([`πρότυπο/τερματικό.zy`](πρότυπο/τερματικό.zy)) so the render code never reads an
  English identifier (§5, §9).
- **Frames are built from measured content** ([`εμφάνιση/πλαίσιο.zy`](εμφάνιση/πλαίσιο.zy)),
  never typed as literals with their padding inside (§6).
- **Language switches inside the game**, with a full redraw, and each language's
  name is written in itself — `Español` is `Español` whether you are reading Greek
  or Hindi (§7).
- **One entry point per language** (§8), and **a gate** that walks 87 keys × 4
  locales × every composed branch, in both engines (§10).
- **हिन्दी drives the digit script.** Choosing it sets `#०९#` once in the dispatcher,
  and every number the program prints follows — `पीढ़ी १३० में सब मर गए` — with no
  call site knowing anything about it (§14).

```bash
$ zymbol run जीवन.zy -p diehard -r 20 -c 40 -b --every 60
२०×४० टोरस  B3/S23  diehard (अड़ियल)
पीढ़ी ०  ७ कोशिकाएँ जीवित
पीढ़ी ६०  ३३ कोशिकाएँ जीवित
पीढ़ी १२०  ११ कोशिकाएँ जीवित
पीढ़ी १३०  ० कोशिकाएँ जीवित
पीढ़ी १३० में सब मर गए
```

Adding a fifth language is **three edits**: a `γλώσσα/<Name>.zy` against the
five-function contract, one import in the dispatcher, one arm in each dispatch.
The gate then checks it key by key.

---

## Testing

**Every assertion is written in Zymbol and every suite decides for itself.** Each
exits 1 if something broke, so a suite that crashes half way through cannot be
mistaken for one that passed — which `grep -q FAIL` over a program's output always
could be.

```bash
zymbol run      δοκιμές/όλα.zy           # every suite
zymbol run --vm δοκιμές/όλα.zy           # on the register VM
zymbol run      δοκιμές/όλα.zy -v        # with every ✓
zymbol run      δοκιμές/όλα.zy κόσμος    # one suite
node ../web/tests/run_one.mjs δοκιμές/όλα.zy    # on the browser engine
```

**The runner is Zymbol too.** [`δοκιμές/όλα.zy`](δοκιμές/όλα.zy) imports the five
suites as modules and calls them — there is no shell anywhere, which matters
because a shell runner would have been claiming that running Zymbol programs
needs something that is not Zymbol. It also means the runner breaks in the same
run the modules do.

That shape was not a free choice: `<\ … \>` returns a command's stdout and
**discards its exit status**, so a runner built the obvious way could not have
reported which suite failed ([GAP-GOL-011](HALLAZGOS.md#gap-gol-011)).

| Suite | Asserts | Cases |
|---|---|---|
| [`κόσμος.zy`](δοκιμές/κόσμος.zy) | the rule, and every pattern against the literature | 42 |
| [`τέλος.zy`](δοκιμές/τέλος.zy) | when the world stops, and with what period | 39 |
| [`γλώσσα.zy`](δοκιμές/γλώσσα.zy) | 87 keys × 4 locales, every composed branch, the rotation | 34 |
| [`όψη.zy`](δοκιμές/όψη.zy) | two columns per glyph, frames aligned in every language, the screen cap | 60 |
| [`εκκίνηση.zy`](δοκιμές/εκκίνηση.zy) | the whole command line, by calling the module | 20 |

The command line is tested by calling `εκκίνηση::ξεκίνα(lang, args)` directly, so
no shell is needed to drive the program either — though those 20 cases can only
assert the **exit code**, because a program cannot capture what its own code
prints ([GAP-GOL-010](HALLAZGOS.md#gap-gol-010)). What the program *said* is
printed where a human can see it and asserted by nothing.

**One test is not in Zymbol, and cannot be.**
[`δοκιμές/οθόνη.py`](δοκιμές/οθόνη.py) drives the editor through a real pty —
sixteen cases, including the pattern catalogue, the live language switch, the
stop conditions and the Hindi digits, and it caught three real defects on its
first runs. It is not there because Python was convenient. `>>|` errors unless
the process has a TTY, `<<|` cannot be handed a scripted key sequence, and
nothing in the language starts a process at all, so **the editor is the one part
of this program that no Zymbol code can reach**
([GAP-GOL-009](HALLAZGOS.md#gap-gol-009)). Six applications in this workspace
draw a screen; none of them tests it.

**The expected values do not come from this program.** The periods, the glider's
displacement, the populations of the R-pentomino at generations 1/10/20/50, the
diehard dying at 130, the Gosper gun emitting its first glider at 30 — all
computed by an independent reference implementation and cross-checked against the
Life literature. A golden recorded from the thing under test only proves it still
does what it did.

---

## What it measures

`μέτρηση/βάση.zy` runs the same generation three ways — a call per cell, the count
inlined, and without building the next grid — so the number separates three costs
instead of blending them.

```bash
zymbol run μέτρηση/όλα.zy               # 32 48 64, ten generations
zymbol run μέτρηση/όλα.zy 100 -g 20     # one bigger world, more generations
zymbol run μέτρηση/όλα.zy 48 --no-js    # skip the browser engine
```

This runner **is** Zymbol as well, and here it genuinely does start other
processes — the question is what three *engines* cost, and a program runs in one.
`<\ … \>` is enough because the only thing needed back is the output; the exit
status it discards ([GAP-GOL-011](HALLAZGOS.md#gap-gol-011)) is why a failed run
shows as `—` rather than as an error.

| side | engine | A call+build | B build | C count | ns/cell-step | A/B |
|------|--------|--------|--------|--------|--------------|-----|
| 64 | `zytw` | 1626 ms | 1625 | 1653 | 19 849 | 1.00 |
| 64 | `zyvm` | 252 ms | 181 | 183 | **3 076** | 1.39 |
| 64 | `zyjs` | 6050 ms | 5195 | 4831 | 147 705 | 1.16 |
| 100 | `zytw` | 3990 ms | 3963 | 4043 | 19 950 | 1.01 |
| 100 | `zyvm` | 618 ms | 451 | 448 | **3 090** | 1.37 |

- the register VM is **6.4×** the tree-walker here, stable to ±1.7%, flat across sizes
- the browser engine is **7.4× slower than the tree-walker**, 48× slower than the VM
- **building a fresh grid every generation is free** (B ≈ C everywhere) — the `Rc` +
  copy-on-write model from HLZ-012/HLZ-014, measured on a real aggregate workload
- **a call per cell costs 39% under the VM and nothing under the tree-walker** —
  [IDEA-GOL-007](HALLAZGOS.md#idea-gol-007)

Re-measure before quoting: these are the interpreter of 2026-09-04.

---

## Layout

```
ζωή.zy  vida.zy  life.zy  जीवन.zy   entry points — each picks a language and nothing else
εκκίνηση.zy                        the command line and setting the world up
παιχνίδι.zy                        the loop: edit, run, end
πυρήνας/   κόσμος.zy               grid, rule, one generation, the stop diagnosis
           σχήματα.zy              the eighteen patterns
εμφάνιση/  όψη.zy                  themes, status line, help, menus
           πλαίσιο.zy              frames built from measured content
γλώσσα/    διανομέας.zy            the dispatcher — the only holder of the locale
           Ελληνικά.zy  Español.zy  English.zy  हिन्दी.zy
πρότυπο/   τερματικό.zy            the Greek layer over std/term
δοκιμές/                           five Zymbol suites, a Zymbol runner, one pty suite
μέτρηση/                           the benchmark and its Zymbol runner
HALLAZGOS.md                       the findings — the primary artifact
```

---

## Authorship

Written with [Claude Code](https://claude.ai/code) under the author's direction, as
the interpreter and the LDV applications are (`interpreter/README.md` § Authorship
& AI Collaboration).
