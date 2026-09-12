# GoL — findings

> **What this is.** The gap log for the Game of Life project, in the canonical
> form `interpreter/LDV.md` § 5.2 asks for: one file named `HALLAZGOS.md`, four
> sections (`BUG` / `GAP` / `ERROR` / `IDEA`), a summary table, and identifiers
> scoped by project from the first entry.
>
> **What this project is.** Not (yet) an LDV project. It was built as its own
> measuring bench — the retro that opened it said a fifth terminal grid game
> would validate almost nothing, and `LDV.md` § 6 agrees in writing. The rule
> agreed with the author: build it, measure it, and escalate to `LDV.md` **only
> if the findings turn out to be worth it**. This file is the evidence for that
> decision, not a claim that the decision was made.
>
> **Status of every entry below: OPEN.** Nothing here has been fixed, and
> nothing should be fixed on the strength of this document alone — the author
> decides per finding whether to implement, defer or reject it (that is the
> standing rule in this workspace, and `LDV.md` § 3 point 5 says the same).

---

## Summary

| ID | Type | Module | What | Engines | Status |
|----|------|--------|------|---------|--------|
| [BUG-GOL-001](#bug-gol-001) | BUG | `zymbol-compiler` | a name bound by destructuring is invisible inside a named function | **zyvm only** (zytw, zyjs correct) | OPEN |
| [BUG-GOL-002](#bug-gol-002) | BUG | `zymbol.js` (analyzer) | a file-level `_name()` function cannot be called from inside any block | **zyjs only** (zytw, zyvm correct) | OPEN |
| [GAP-GOL-003](#gap-gol-003) | GAP | language | a program cannot construct an error value | all three | OPEN |
| [GAP-GOL-004](#gap-gol-004) | GAP | `zymbol-semantic` | the range-direction warning is a false positive on literal bounds, and cannot be silenced | all three | OPEN |
| [GAP-GOL-005](#gap-gol-005) | GAP | `zymbol-cli` | `-h` / `--help` never reach the program | CLI | OPEN |
| [GAP-GOL-006](#gap-gol-006) | GAP | `web/tests/run_one.mjs` | the browser-engine harness cannot pass CLI arguments | harness | OPEN |
| [IDEA-GOL-007](#idea-gol-007) | IDEA | `zymbol-vm` | a call per cell costs ~39% under the VM and ~0% under the tree-walker | measurement | OPEN |
| [IDEA-GOL-008](#idea-gol-008) | IDEA | `USERAPPI18N.md` | a written `"1"` inside a plural string defeats the numeral mode, silently | doctrine | OPEN |
| [GAP-GOL-009](#gap-gol-009) | GAP | language | an interactive Zymbol program cannot be tested from Zymbol | all three | OPEN |
| [GAP-GOL-010](#gap-gol-010) | GAP | language | a program cannot capture what its own code prints | all three | OPEN |
| [GAP-GOL-011](#gap-gol-011) | GAP | language | `<\ … \>` discards the exit status of what it ran | all three | OPEN |
| [IDEA-GOL-012](#idea-gol-012) | IDEA | the LDV applications | 0 of 44 application suites report their result as an exit code | workshop | OPEN |
| [BUG-GOL-013](#bug-gol-013) | BUG | nav-path ranges | a negative index in a nav-path range raises in `zytw` and returns `[]` in silence under `zyvm`/`zyjs` | **all three disagree** | OPEN |

Every reproduction below is a complete program. Run it as written.

---

## BUG

### BUG-GOL-001

**A name bound by a destructuring pattern at file level is invisible inside a
named function body — under the register VM only.**

```zymbol
(a, H) = ("x", [1, 2, 3])
g() { <~ H$# }
>> g() ¶
```

| Engine | Result |
|--------|--------|
| `zytw` | `3` |
| `zyjs` | `3` |
| `zyvm` | `Runtime error: 'H' is undefined — did you mean 'H°' (hot definition)?` |

**Scope, established by probe:**

| Binding form | Visible under `--vm`? |
|---|---|
| `S = 7` (plain assignment) | yes |
| `(T, U) = (8, 9)` (tuple pattern) | **no** |
| `[V, W] = [10, 11]` (array pattern) | **no** |
| `(Z, *R) = (14, 15, 16)` (rest pattern) | **no** |
| any of the above, read from a **lambda** instead | yes |
| any of the above, followed by a plain `T = T` | yes |

So it is the *named function* path, and it is the compiler's record of which
names exist rather than their values — which is why re-assigning the same value
under the same name repairs it.

**Cause.** `crates/zymbol-compiler/src/lib.rs`, the loop that fills
`file_var_map` before the function bodies are compiled:

```rust
for stmt in &program.statements {
    if let Statement::Assignment(a) = stmt {          // ← only this variant
        ...
        compiler.file_var_map.insert(a.name.clone(), idx);
    }
}
```

`Statement::DestructureAssign` (`zymbol-ast/src/lib.rs:95`) is never visited, so
none of the names it binds are registered, and the read inside a function body
falls through to "undefined".

**Why no suite caught it.** `zyquality/corpus/functions/captura_del_archivo.zy`
is nine cases of exactly this feature — direct call, as a value, write
isolation, two levels deep, read-at-call, parameter shadowing, not-dynamic —
and every one of them binds with `base = 10`. Destructuring has its own corpus
files (`collections/32_destructure_extended.zy`, `35_rest_pattern.zy`). Neither
crosses the other, and the defect lives only in the crossing.

**Why it matters more than it looks.** The tuple return is how this language
gets several values out of a function, and destructuring is how they are
received — so this fires on the *idiomatic* form. It cost this project two
rewrites before it was identified, and the register VM is the engine slated to
become the default.

---

### BUG-GOL-002

**The browser engine refuses to call a file-level `_name()` function from
inside any block. Both Rust engines allow it.**

```zymbol
_f() { <~ 1 }
>> "top level: " _f() ¶
@ 1 { >> "inside a loop: " _f() ¶ }
```

| Engine | Result |
|--------|--------|
| `zytw` | `top level: 1` / `inside a loop: 1` |
| `zyvm` | `top level: 1` / `inside a loop: 1` |
| `zyjs` | `error: cannot access underscore variable '_f' from inner scope` — nothing runs |

`? #1 { _f() }` fails the same way. Inside a **module** the call works in all
three, which is why this project's modules use `_helper()` freely and only a
script trips it.

**Delimited while building the i18n layer:** a module *constant* named `_NAME`
**is** refused from inside a block, by all three engines and correctly — a
constant is a variable, and that is the documented rule. So the defect is
precisely the function namespace, and precisely in `zyjs`:

| Declaration | read from inside a block |
|---|---|
| `_CONST := […]` at module level | refused by all three — correct |
| `_f() { … }` at module level | accepted by all three |
| `_f() { … }` at file level in a script | accepted by `zytw`/`zyvm`, **refused by `zyjs`** |

**Which engine is right.** `GUIDE.md` § 4 defines the rule over *variables*:
*"A variable whose name begins with `_` has exact block scope"*. A function
declaration is not a variable, and `zyjs` is applying a variable rule to the
function namespace. Two engines against one, and the odd one out contradicts
the documented wording.

**Consequence.** No script using `_private()` helpers runs in the playground —
and that is the convention this workspace uses everywhere else. It was found by
running this project's own test suite through `web/tests/run_one.mjs`; the
suite had to rename four functions to get a three-engine comparison at all.

---

### BUG-GOL-013

**A negative index in a nav-path range raises under the tree-walker and returns
an empty array, in silence, under both other engines.**

```zymbol
a = [10, 20, 30, 40, 50]
>> (a$[2..-2]) ¶      // the documented slice
>> (a[2..-2]) ¶       // the nav-path range
```

| Expression | `zytw` | `zyvm` | `zyjs` |
|---|---|---|---|
| `a$[2..-2]` — documented | `[20, 30, 40]` | `[20, 30, 40]` | `[20, 30, 40]` |
| `a[2..-2]` — nav path | **`Runtime error: range indices in nav path must be positive integers`** | **`[]`** | **`[]`** |
| `a[-2..-1]` — nav path | **same error** | `[40, 50]` | `[40, 50]` |
| `"Abcde"[-2..-1]` | **same error** | `[d, e]` | `[d, e]` |

Three answers to one expression, and the two that agree give the worst one: an
empty array is not an error and not the right result, so a program that slices
this way gets nothing and carries on. `a[-2..-1]` is more insidious still —
`zyvm` and `zyjs` return the *correct* elements there, so the form looks like it
works until the start index is positive and the end negative, which is the shape
`$[k..-k]` exists for.

**Which engine is right is a design question, not this log's.** What is certain
is that the tree-walker's message states a rule (*"must be positive integers"*)
that the other two engines do not enforce, and that GUIDE.md § 11c documents
ranges on nav steps with positive bounds only while § 11 documents negative
bounds only for `$[..]`. Neither section says the two notations differ, and the
corpus has no file that crosses them — `zyquality/corpus/strings/` uses `$[..]`
and `$-[1..6]`, never a bare `[k..-k]`.

**How it surfaced.** `μέτρηση/όλα.zy` parses a benchmark line by taking its last
two characters to test for `"ms"`. Written as `κ[-2..-1]` it worked under the
register VM and died under the tree-walker; the correct form is `κ$[-2..-1]`.
Three notations that look alike return three different types, and only two of
them are documented:

| Form | On `"Abcde"` | Type |
|---|---|---|
| `s[1]` | `A` | **Char** |
| `s$[1..2]` | `Ab` | **String** |
| `s[1..2]` | `[A, b]` | **Array** — undocumented |

---

## GAP

### GAP-GOL-003

**A program cannot construct an error value.**

The language has three operators for handling errors — `!?` catches, `$!` tests,
`$!!` propagates — and `GUIDE.md` § 16 documents a soft-error convention that
`std/io`, `std/net`, `std/db` and `std/time` all follow: *"Recoverable
environmental failures come back as a soft `Error` value that you test with `$!`
or catch with `!?`, rather than aborting."*

There is no way for user code to produce one. `##Parse("...")` is a catch
pattern, not a constructor:

```zymbol
f() { <~ ##Parse("bad input") }
// error: expected expression, found Hash
```

So a user module that validates outside data — which is the exact situation the
convention exists for — cannot follow it. This project's rule parser and pattern
lookup both return `(message, value...)` tuples instead:

```zymbol
(μήνυμα, κελιά) = σ::πάρε(όνομα)
? μήνυμα <> "" { ... }
```

That works, and every caller now carries a slot it must remember to check —
which is the failure mode the soft-error value exists to prevent, since `$!`
cannot be forgotten silently the way an unread tuple slot can.

**Decalogue point 4 applies:** *"if the program can only express the concept by
leaving the language, the language did not support it."* The concept here is
"this data is malformed, and the caller decides what to do", and the language
expresses it for its own standard library and not for a program written in it.

---

### GAP-GOL-004

**The range-direction warning fires on literal bounds it could decide
statically, and there is no way to silence it.**

```zymbol
@ i:1..3  { }    // no warning
@ i:-1..1 { }    // warning
@ i:-3..-1 { }   // warning
```

```
warning: range direction is decided at runtime: if the end turns out to be
lower than the start, this loop counts down instead of not running.
```

Both bounds are literals in every case, and `-1 < 1` is not a runtime question.
The warning appears to be gated on the bounds being *positive* literals rather
than on their being literals at all — a negative literal is a unary minus over
a literal, and the check does not fold it.

`-1..1` is the canonical way to walk a Moore neighbourhood, so this fires on
the most ordinary shape in the whole domain. It is emitted by `zymbol run` as
well as `zymbol check`, and there is no pragma, no `_`-prefix escape and no
comment marker that suppresses it, so a program that has *already* guarded the
empty case has no way to say so and prints the warning on every single run.

This project routes around it with a pair of offset tables (`πυρήνας/κόσμος.zy`,
`ΔΓ`/`ΔΣ`) — faster, as it happens, but chosen for the warning and not for the
speed.

**Not disputed:** the warning is *correct and useful* when a bound is dynamic
(`1..γραμμές` can be `1..0`, which counts down). Only the literal case is
wrong, and only the absence of any suppression makes the rest expensive.

---

### GAP-GOL-005

**`-h` and `--help` never reach a Zymbol program.**

```bash
zymbol run ζωή.zy --help      # prints zymbol's help, not the program's
zymbol run ζωή.zy -h          # same
zymbol run ζωή.zy --version   # reaches the program
zymbol run ζωή.zy -- --help   # reaches the program
```

`>< args` is documented in `GUIDE.md` § 3 with a plain example and no mention
that two flags are reserved, or that `--` exists as the way past them. They are
the two flags every command-line program is expected to answer, so every
program that grows a CLI hits this, and the workaround is invisible until
someone finds it.

**Not a bug in `><`** — the interception is `clap`'s and it is ordinary CLI
behaviour. The gap is that nothing says so where a user would look, and that a
packaged `.zyp` run as `zymbol run app.zyp --help` has the same problem with
no obvious place to put the `--`.

---

### GAP-GOL-006

**`web/tests/run_one.mjs` cannot pass CLI arguments, so no parameterised
program can be graded on three engines.**

The browser engine *implements* `>< args` — `runZymbol(..., cliArgs = [])`,
`web/src/zymbol/zymbol.js:8286`, and `CLI_ARGS` is a real token. The harness
that `zyquality` and every wrapper script use to reach that engine accepts only
`--input`:

```js
const args = process.argv.slice(2);
const file = args.find(a => !a.startsWith('--'));
const inputArg = args[args.indexOf('--input') + 1];
```

Consequence: any application whose behaviour is selected by a command line —
this one, ZethyCLI, anything with a `--mode` — can be compared across `zytw`
and `zyvm` and not across all three. `μέτρηση/όλα.zy` works around it by reading
its own benchmark with `std/io`, substituting the sizes into a copy, running that
and deleting it — which works, and is not a thing a harness should require of
every caller.

A `--args a b c` passthrough would close it; the engine side already exists.

---

### GAP-GOL-009

**An interactive Zymbol program cannot be tested from Zymbol.**

The TUI primitives are the only part of this project that no Zymbol code can
reach:

- `>>|` **errors** unless the process is attached to a TTY, so a test that opens
  a screen cannot run under a test runner, a pipe, or CI.
- `<<|` and `<<|?` read from that terminal. There is no way to hand them a
  scripted sequence of keys — no alternative source, no simulated input, no
  replay.
- Nothing in the language or in `std/*` starts another process at all, let alone
  one with a terminal attached.

So the 195 assertions in `δοκιμές/` cover the world, the rule, the stop
conditions, four locales, the geometry and the whole command line — and stop at
the editor, which is the part a user actually touches. Testing it requires
`δοκιμές/οθόνη.py`: 130 lines of Python that fork a pty, write keystrokes into
it, and read the escape sequences back. That file is not there because Python was
convenient. It is there because **the language cannot do it**, and neither can
any program written in it.

**Why this is more than a testing inconvenience.** The same incapacity means a
Zymbol program cannot drive another program at all — cannot wrap a CLI, cannot
script an interactive tool, cannot be the parent process of anything. A language
that ships TUI primitives (`>>|`, `<<|`, `>>~`, `>>?`) and cannot test what it
draws with them is asking every application author to leave the language to find
out whether their screen works. Six of this workspace's applications draw a
screen. **None of them tests it.**

*(The shape of a remedy — simulated input, a process module, a headless mode —
is a design question and not this log's to answer. What is recorded here is the
incapacity and what it costs.)*

---

### GAP-GOL-010

**A program cannot capture what its own code prints.**

`>>` writes to the process's output and nothing else. There is no sink, no
redirect, no `capture { … }`, and no return value that carries what a call
printed. So a test that calls anything which writes to the screen writes to the
screen too, mixed into its own report:

```
  ┌ έξοδος του δοκιμαζόμενου προγράμματος ──────────
Σχήματα:
  block           τετράγωνο              ακίνητο (4)
  …
  └────────────────────────────────────────────────
  ✔ εκκίνηση                 20 δοκιμές
```

`δοκιμές/εκκίνηση.zy` tests the entire command line by calling
`εκκίνηση::ξεκίνα(lang, args)` directly — which is the right way to test it, and
the reason it can be done without a shell at all. But every one of those 20 cases
can only assert the **exit code**. What the program actually *said* — that a bad
rule produces the right message in the right language, that `--list` names all
eighteen patterns — is printed where a human can see it and asserted by nothing.

The workaround used everywhere else in this workspace is a golden file, and a
golden needs a runner outside the language to capture the output and compare it.
That is the same dependency GAP-GOL-009 describes, arriving from the other
direction: **the language cannot observe itself running.**

---

### GAP-GOL-011

**`<\ … \>` discards the exit status of what it ran.**

```zymbol
a = <\ "echo hola" \>
>> "«" a "»" ¶          // → «hola»
b = <\ "exit 3" \>
>> "«" b "»" ¶          // → «»
```

A command that failed and a command that printed nothing are the same value. The
status is not returned, not available afterwards, and not exposed anywhere else,
so a Zymbol program that shells out **cannot tell whether the thing it ran
worked**. `stderr` is merged into the same string, so it cannot be separated
either.

This is what forced the shape of `δοκιμές/όλα.zy`. A runner built the obvious
way — one `<\ "zymbol run …" \>` per suite — could not have reported which
suite failed, because every suite would come back as a blob of text with no
status. The runner imports the suites as **modules** and calls them instead,
which turned out better (it needs no shell at all, and it breaks in the same run
if the modules break) — but it was not a free choice, and a program that needs to
run something that is *not* Zymbol has no equivalent escape.

`zymbol run` itself gets this right: `<~ 2` at the top level reaches the
operating system, and GUIDE.md § 3 documents it. So Zymbol can *report* an exit
status and cannot *read* one.

---

## ERROR

None. No diagnostic in this project was wrong about what it pointed at — the
one false positive is a warning, and it is GAP-GOL-004.

---

## IDEA

### IDEA-GOL-007

**A function call per cell costs ~39% under the register VM and ~0% under the
tree-walker. Building the next grid costs nothing at all under either.**

Measured by `μέτρηση/βάση.zy`, which runs the same generation three ways:

- **A** — `κόσμος::βήμα`: a neighbour-count *call* per cell, new grid per step
- **B** — the same count written inline: no call, new grid per step
- **C** — count only: no call, nothing built

| side | engine | A (ms) | B (ms) | C (ms) | ns/cell-step | A/B |
|------|--------|--------|--------|--------|--------------|-----|
| 64 | `zytw` | 1626 | 1625 | 1653 | 19 849 | 1.00 |
| 64 | `zyvm` | 252 | 181 | 183 | 3 076 | **1.39** |
| 100 | `zytw` | 3990 | 3963 | 4043 | 19 950 | 1.01 |
| 100 | `zyvm` | 618 | 451 | 448 | 3 090 | **1.37** |
| 64 | `zyjs` | 6050 | 5195 | 4831 | 147 705 | 1.16 |

Three readings, and each is worth stating separately:

1. **B ≈ C in every engine.** Building a fresh 100×100 grid every generation is
   free next to the arithmetic that fills it. That is HLZ-012/HLZ-014 working —
   `Value` sharing `Array` behind an `Rc` and copying on write — and it is the
   measurement that says the copy-on-write model paid for itself on a real
   aggregate workload rather than on a microbenchmark.

2. **A/B is 1.00 under the tree-walker and 1.39 under the VM.** The tree-walker
   is slow enough everywhere that a call per cell disappears into the noise. The
   VM made everything *else* fast, so the call is now 39% of the work — which
   is a statement about where the next VM optimisation belongs, and it is not
   visible from any benchmark that does not vary the call structure while
   holding the computation fixed.

3. **The register VM is 6.4× the tree-walker here**, stable to ±1.7% across
   repeated runs and flat across sizes (19 849 → 19 950 ns/cell for `zytw`,
   3 076 → 3 090 for `zyvm`). That is the top of the documented 1.4–6× range
   for microbenchmarks, on a workload that is neither a microbenchmark nor
   search-shaped. **The browser engine is 7.4× slower than the tree-walker and
   48× slower than the VM** on the same program — a figure this workspace did
   not have, because `zyquality/bench/` is deliberately outside the corpus and
   the browser parity runner never ran it.

**Not a defect.** Filed as IDEA because the actionable part is a VM
optimisation target, and because the three numbers together are a better
answer than "~4.4× on fib(35)" to the question of what `--vm` is worth.

---

### IDEA-GOL-008

**A digit written as a letter inside a translated string defeats the numeral
mode, and nothing says so.**

`USERAPPI18N.md` §14 names two traps for the digit-script mechanism: the mode
reaches `io::write` and shell commands, and `json::encode` stays ASCII. There is
a third, and it bites inside the locale files themselves — the one place the
document is telling you to put your text.

```zymbol
// ✗ the singular's digit is a letter, so it stays ASCII for ever
φράση_πληθυσμού(ν) {
    ? ν == 1 { <~ "1 कोशिका जीवित" }
    <~ "{ν} कोशिकाएँ जीवित"
}
```

Output in Hindi: `1 कोशिका जीवित` beside `३६१ कोशिकाएँ जीवित`. The plural follows
the language and the singular does not, because the mode governs the **printing
of a number** and not the letters of a literal — which is correct, documented
and completely invisible in every language whose digits are already ASCII.

```zymbol
// ✓ the digit goes through the number
? ν == 1 { <~ "{ν} कोशिका जीवित" }
```

It appeared three times while writing this project, always in the same shape: a
plural function's singular branch, a `gen 0` header, and a year typed into a
label. Each was invisible in Greek, Spanish and English, and each was obvious
the moment the Hindi locale was switched on. **The general rule is narrower than
§14 states:** the mode belongs to output the user reads, *and only a value can
carry it* — a digit typed as text is text, wherever it sits.

Worth a line in §14's trap list, and worth a row in the §12 audit checklist:
*"no visible digit is written as a literal inside a translated string."* It is
mechanically checkable — a locale file containing `0`–`9` between quotes is
either this bug or a version number.

### IDEA-GOL-012

**Not one application suite in this workspace reports its result as an exit
code. All 44 of them are read by something else.**

Swept on 2026-09-04, after the runner for this project was rewritten in Zymbol:

| Application | Suites | Exit with `<~` | Print `FAIL` | Runner |
|---|---|---|---|---|
| 囲碁 | 10 | **0** | 7 | `試験/全試験.sh` |
| चतुरङ्गम् | 7 | **0** | 6 | `परीक्षा/सर्वपरीक्षा.sh` |
| Serpiente | 2 | **0** | 0 | `pruebas/todas.sh` |
| Hov veS | 1 | **0** | 1 | `mIw/Hoch.sh` |
| Zofía | 11 | **0** | 0 | — |
| ZyAudit | 8 | **0** | 0 | — |
| ZyBank | 5 | **0** | 3 | `pruebas/todas.sh` |
| **total** | **44** | **0** | **17** | |

A suite that counts its own failures correctly and then exits 0 has to be graded
from outside. Seventeen of them print `FAIL` and are read by `grep`; the other
twenty-seven print `PASS`/`TODO BIEN` and are read by a person. `囲碁/試験/全試験.sh`
states the consequence in its own header, and it is right:

> *"This script is not the authority any more. It decides correctness by grepping
> the suite's output for FAIL, so a suite that crashes half way through prints no
> FAIL and passes — that is not hypothetical, it was measured."*

**This is not carelessness, and the date says so.** `<~` at the top level
becoming the process's exit status is **new in v0.0.9** — before it, the
tree-walker ignored the value and ran on, while the register VM and the browser
engine stopped and dropped it (GUIDE.md § "Exit Status"). Every one of these
applications was written against a version where a suite *could not* say "I
failed" in a way a shell would hear. ZyBank, the most recent, still ends with
`? fallos == 0 { >> "TODO BIEN" ¶ }` because that was the only thing available
when it was written.

`zyquality/project/` closes the hole from the other side, and correctly: it
compares each suite against a golden, and a truncated run does not match one. But
that makes the verdict depend on `zyq`, on a recorded golden, and on a runner
outside the language. **A suite still cannot say for itself that it failed** —
and now it could.

The cost of the change is one line per suite. What that line would let a runner
be — and whether the six older applications are worth touching for it — is the
author's call, not this log's. What is recorded here is the count, the cause,
and the fact that the capability now exists and is unused.

*(GoL's own runner, `δοκιμές/όλα.zy`, is Zymbol: it imports the five suites as
modules and calls them, so no shell is involved at any point and a suite that
throws takes the runner down with it. That shape is only possible because each
suite returns its failure count — which is the same fact this finding is about,
applied at the function level instead of the process level.)*

---

## What this cost, and what it says about escalating

The program is ~3,060 lines of Zymbol across 25 files — eleven modules, four
locales, five self-asserting test suites and two runners that are themselves
Zymbol — built in a day. The only file in it that is not Zymbol is the pty
harness, and GAP-GOL-009 is why. The findings above are what a domain the language
had not been asked to serve produced *on the way*, before the program did
anything interesting.

Three of them (BUG-GOL-001, BUG-GOL-002, BUG-GOL-013) are engine divergences on
ordinary code, each two engines against one, and none is reachable from the
corpus because the corpus tests each feature alone. Three more (GAP-GOL-009 to
011) are the same incapacity seen from three sides: **the language cannot observe
itself running** — it cannot drive an interactive program, cannot capture what
its own code prints, and cannot read the exit status of anything it starts. That
one is not about Life at all. It is about what a language needs before its own
applications can be tested in it, and it was found by trying. That is `LDV.md` § 4's argument about
intersections, reproduced without setting out to reproduce it.

That is the case for escalating. The case against is unchanged and is in the
retro that opened the project: this is the fifth terminal grid game, `LDV.md`
§ 6 says domain distance is what pays, and a ninth gated application is a
recurring maintenance bill. **The decision is the author's.** What is settled is
that the findings exist and are reproducible.
