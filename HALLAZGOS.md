# GoL — findings

> **What this is.** The gap log for the Game of Life project, in the canonical
> form `zymbol-design/LDV.md` § 5.2 asks for: one file named `HALLAZGOS.md`, four
> sections (`BUG` / `GAP` / `ERROR` / `IDEA`), a summary table, and identifiers
> scoped by project from the first entry.
>
> **What this project is.** An LDV project since **2026-09-29** — the ninth, and
> the first to be *escalated* rather than started as one. It was built as its
> own measuring bench: the retro that opened it said a fifth terminal grid game
> would validate almost nothing, and `LDV.md` § 6 agrees in writing. The rule
> agreed with the author was to escalate **only if the findings turned out to
> be worth it**. They did, and not because of the grid — see the closing
> section. From that date the suite is in the gate (`zyquality/project/apps.toml`,
> id `gol`), indexed in `LDV.md` § 5.1, and part of ZyFmtCheck's body.
>
> **Status.** Each entry says its own, and a resolved one says how at its foot.
> Nothing is closed on the strength of this document alone — the author decides
> per finding whether to implement, defer or reject it (the standing rule in
> this workspace, and `LDV.md` § 3 point 5 says the same). A GAP that asks a
> design question stays OPEN until that question has an answer.

---

## Summary

| ID | Type | Module | What | Engines | Status |
|----|------|--------|------|---------|--------|
| [BUG-GOL-001](#bug-gol-001) | BUG | `zymbol-compiler` | a name bound by destructuring is invisible inside a named function | **zyvm only** (zytw, zyjs correct) | **SUPERSEDED** by MEM-2 |
| [BUG-GOL-002](#bug-gol-002) | BUG | `zymbol.js` (analyzer + runtime) | a file-level `_name()` function cannot be called from inside any block | **zyjs only** (zytw, zyvm correct) | **FIXED** 2026-09-29 |
| [GAP-GOL-003](#gap-gol-003) | GAP | language | a program cannot construct an error value | all three | **FIXED** 2026-09-29 — `##Kind("…")` |
| [GAP-GOL-004](#gap-gol-004) | GAP | `zymbol-semantic` | the range-direction warning is a false positive on literal bounds, and cannot be silenced | all three | **FIXED** by GLB-060; the rest **REJECTED** |
| [GAP-GOL-005](#gap-gol-005) | GAP | `zymbol-cli` | `-h` / `--help` never reach the program | CLI | **CLOSED** — documented 2026-09-29 |
| [GAP-GOL-006](#gap-gol-006) | GAP | `web/tests/run_one.mjs` | the browser-engine harness cannot pass CLI arguments | harness | **FIXED** 2026-09-29 |
| [IDEA-GOL-007](#idea-gol-007) | IDEA | `zymbol-vm` | a call per cell costs ~39% under the VM and ~0% under the tree-walker | measurement | OPEN |
| [IDEA-GOL-008](#idea-gol-008) | IDEA | `USERAPPI18N.md` | a written `"1"` inside a plural string defeats the numeral mode, silently | doctrine | **DONE** — § 14 trap 3, checklist item 15 |
| [GAP-GOL-009](#gap-gol-009) | GAP | language | an interactive Zymbol program cannot be tested from Zymbol | all three | **FIXED** 2026-09-30 — `zymbol run --keys` |
| [GAP-GOL-010](#gap-gol-010) | GAP | language | a program cannot capture what its own code prints | all three | **FIXED** 2026-09-30 — `</ app.zy args… />` |
| [GAP-GOL-011](#gap-gol-011) | GAP | language | `<\ … \>` discards the exit status of what it ran | all three | **FIXED** 2026-09-30 — soft `##IO` |
| [IDEA-GOL-012](#idea-gol-012) | IDEA | the LDV applications | 0 of 44 application suites report their result as an exit code | workshop | **DONE** for the 22 that count failures |
| [BUG-GOL-013](#bug-gol-013) | BUG | nav-path ranges | a negative index in a nav-path range raises in `zytw` and returns `[]` in silence under `zyvm`/`zyjs` | **all three disagree** | **FIXED** by GLB-012 |
| [BUG-GOL-015](#bug-gol-015) | BUG | `#?` count | the tree-walker counted a String's `#?` in bytes, and both Rust engines an error's message | **zytw** strings; **zytw, zyvm** errors | **FIXED** 2026-09-29 |
| [GAP-GOL-016](#gap-gol-016) | GAP | language | an error value's message cannot be read back without taking its display apart | all three | **FIXED** 2026-09-29 — `##Kind(m) =>` |
| [BUG-GOL-014](#bug-gol-014) | BUG | `zymbol.js` (`<\ … \>`) | in the browser, an unrecognised shell command returns a random nine-digit number instead of failing | **zyjs only** | **FIXED** 2026-09-29 |

Every reproduction below is a complete program. Run it as written. The tables
of engine answers record what was measured **when the finding was filed**; a
resolved entry says at its foot what the engines answer now.

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

**Resolution — SUPERSEDED by MEM-2 (verified 2026-09-29).** The function-capture
rule this finding lived under was reversed: `PREMISES.md` MEM-2 makes a named
function a self-contained space, and since 2026-09-13 all three engines refuse
the read *before running*, with the same message whatever created the name:

```
error: 'H' is read from outside this function
  = help: a function is a self-contained space: a value crosses into it as a parameter, never by being in view — pass 'H' as one
```

So the divergence cannot come back by this road, and the forms that remain
legal — a lambda reading `H`, `V`, `R`, or `g(H, V)` passing them as parameters —
agree in all three (`40`, `13`). The loop in `zymbol-compiler/src/lib.rs` still
visits only `Statement::Assignment`; it is no longer reachable for a read,
because the analyser stops the program first.

What the finding taught is kept as a refusal of the crossing itself:
`zyquality/corpus/errors/semantic/funcion_lee_lo_desestructurado.zy` — tuple,
array and rest patterns, each read from a function, each refused by all three.
It is the sibling of `funcion_lee_el_archivo.zy`, which only ever bound with
`x = …`, and that is the whole lesson: the rule held, and the file that tested it
did not cross the one feature where it broke.

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

**Resolution — FIXED in `zyjs`, 2026-09-29.** The rule was applied twice, and
both places had to change: the analyser's `lookup` in `web/src/zymbol/zymbol.js`
refused the name before anything ran, and `Env.get` refused it again at run time
once the analyser let it through. Both now skip a name bound to a function
declaration; both still refuse a variable. Measured after the change:

| | `zytw` | `zyvm` | `zyjs` |
|---|---|---|---|
| `_f()` from a loop, an `if`, a nested loop, a function | runs | runs | runs |
| `_v = 5` read from `@ 1 { }` | refused | refused | refused |
| `_K := 7` read from `@ 1 { }` | refused | refused | refused |

Held by `zyquality/corpus/functions/funcion_guion_bajo_en_bloque.zy`, which
agrees on all three engines.

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

**Resolution — FIXED by ZyDDT `GLB-012` (decided 2026-09-15, built 2026-09-22).**
The author decided both halves in D1 and D3: a start or end that is not a
positive position in a nav-path range is an **error** of family `##Index`, and an
inverted range selects in descending order. All three engines now raise on
`a[2..-2]`, `a[-2..-1]` and `"Abcde"[-2..-1]` with the tree-walker's message, and
the slice `a$[2..-2]` keeps answering `[20, 30, 40]`. Held by the ZyDDT cell
`runtime-index-nav/range-indices-in-nav-path-must-be` (`expect = "error"`).
What this log added was the silent `[]` in two engines, which is gone.

---

### BUG-GOL-014

**In the browser engine, a shell command it does not recognise returns a random
nine-digit number — in silence, as if the command had printed it.**

Found on 2026-09-29, re-measuring GAP-GOL-011 on three engines:

```zymbol
b = <\ "exit 3" \>
>> "«" b "»" ¶
```

| Engine | Result |
|--------|--------|
| `zytw` | `«»` |
| `zyvm` | `«»` |
| `zyjs` | `«691156425»` — a different number on every run |

**Cause.** The browser has no shell, and `web/src/zymbol/zymbol.js`, `case
'BashExec'`, is a set of stand-ins: `date +%Y` and friends answer from the
clock, `echo literal` answers with its text, and the entropy commands a seed is
built from (`date +%N`, `echo $$`, `/dev/urandom`) answer with a number of the
same order of magnitude — a deliberate and documented choice, since v0.0.9's
integer is fail-closed and a seed is multiplied on the next line. The last line
generalises it:

```js
// Anything else: entropy in the same nine-digit range …
return mkStr(String(_rand(1e9)));
```

So *every* other command is treated as a request for entropy. The corpus and
the example pool use `<\ \>` with `whoami`, `pwd`, `ls`, `cat file`, `test -f …
&& echo si || echo no` and eight `sqlite3 … 'SELECT …'` — each of which, in the
playground, returns a random number that the program then prints or parses as
if it were the answer.

**Why it is a BUG and not an environment exclusion.** An exclusion says *this
engine cannot run this*. This engine runs it and answers wrongly, and `LDV.md`
§ 2 names the silent wrong answer as red on the same footing as the incapacity.
The sibling construct already does the right thing: `</ file.zy />` in the same
function throws *"a subscript runs another file as a process, and the browser
has none"*.

**Resolution — FIXED, 2026-09-29 (author's decision D1).** Refuse any command
with no stand-in, keep the stand-ins by name. `case 'BashExec'` now answers:

| command | answer |
|---|---|
| `date +FORMAT` with `%Y %m %d %H %M %S %s %F %T %N %6N %%` | the whole format, from the clock — it used to answer `date +%Y-%m-%d` with the year alone |
| `date +%N`, `echo $$`, `od -An -N2 -tu2 /dev/urandom [\| tr -d …]` | entropy of the same range as the command, which the games seed from |
| `echo` of literal words, with nothing the shell would read as syntax | the words — `echo x \| bc` used to answer with the text of the pipeline |
| anything else, including a command built from variables | `cannot run 'exit 3': a shell command runs as a process, and the browser has none` |

The sweep before changing it: the four published games seed only from `date
+%N`, `echo $$` and `od … /dev/urandom | tr -d ' \n'`, all kept. GO's `printenv`,
`ps` and `date +%s%6N` are in `棋戦.zy`, which is not in the package. One corpus
file, `bugs/bug03_bashexec_void_statement.zy`, had agreed only because the
browser pretended to run `true`, `mkdir` and `rmdir`; it now carries the
`BASH_EXEC` exclusion every other shell file carries, with that history as its
reason. Held by `web/tests/test_shell.mjs` (16 checks, in CI): against the old
engine 11 of them fail.

---

### BUG-GOL-015

**`#?` counted in bytes where the language counts code points.**

Found by comparing the three engines on the constructor above:

```zymbol
s = "vacía"
>> s#? ¶
e = ##Parse("vacía")
>> e#? ¶
```

| | `zytw` | `zyvm` | `zyjs` |
|---|---|---|---|
| `s#?` | `(##", 6, vacía)` | `(##", 5, vacía)` | `(##", 5, vacía)` |
| `e#?` | `(##Parse, 6, …)` | `(##Parse, 6, …)` | `(##Parse, 5, …)` |

`$#` gives 5 in all three. So the tree-walker's `#?` on a String disagreed with
the other two engines, and both Rust engines counted an error's message in
bytes. Nobody saw either: no corpus file asked `#?` of a non-ASCII string, and
every error message the standard library produces is ASCII.

**Resolution — FIXED, 2026-09-29.** Code points in both places, both Rust
engines (`data_ops.rs`, and `error_message_len` in the VM). Held by
`corpus/strings/tipo_cuenta_puntos_de_codigo.zy` — Spanish, Greek and Chinese.

---

### GAP-GOL-016

**An error value's message cannot be read back — only printed.**

Found applying GAP-GOL-003 to this program. `κ::κανόνας` and `σ::πάρε` return a
catalogue key when the input is wrong (the core never writes text a person will
read), and the caller translates it. With the constructor they would return
`##Κανόνας("σφάλμα.κανόνας_κενό")` — and then the caller needs the key back:

```zymbol
κανόνας(κείμενο) {
    ? κείμενο$# == 0 { <~ ##Κανόνας("σφάλμα.κανόνας_κενό") }
    <~ κείμενο
}
r = κανόνας("")
? r$! {
    (είδος, _ν, _τ) = r#?
    κείμενο = "" r
    κλειδί = κείμενο$[είδος$# + 2..-2]
    >> "κλειδί: " κλειδί ¶
}
```

That runs, on all three engines, and it is the finding: the only way to the
message is to turn the error into its display and cut the `##Κανόνας(` and `)`
off by hand. The kind is readable — `#?` hands it over as text — and the message
is not. Inside `:!` there is `_err`; a built error never reaches a `:!`, which
is the point of it being a value.

It reaches past this program. D2 (GAP-GOL-011) will return a failed command as
`##IO(…)` carrying its exit status: the status will be in the message, where
nothing can read it either.

**Resolution — FIXED, 2026-09-29 (author's decision D7).** The spelling that
builds an error takes it apart, as a pattern of `??`:

```zymbol
κανόνας = κ::κανόνας(όνομα_κανόνα)
?? κανόνας {
    ##Κανόνας(κλειδί) => { σφάλμα = κλειδί }
    _                 => { (γέννηση, επιβίωση) = κανόνας }
}
```

That is `εκκίνηση.zy` now. `##Kind(m)` matches an error of that kind and puts
its message in `m`; `##Kind(_)` and `##Kind` match the kind alone, as `:!` does.
Three rules came with it, each decided rather than left to the engines:

- the binding is a **birth like `m = …`**: a visible `m` is assigned, never
  shadowed — `PREMISES.md` MEM-7 settled that without a new decision, and the
  first version, which shadowed, was wrong against it;
- it **stands alone** in its arm: refused inside `||` (the name would not exist
  when the other alternative matched) and inside a list pattern;
- the message is **bound, never compared**: `##A("x") =>` is refused.

It is the first pattern in the language that creates a name, so GUIDE § 7 now
lists seven kinds and LLM.md no longer says there are no binding patterns.
Held by `corpus/errors/catchable/leer_mensaje_de_error.zy`, three forms in
`reject/errors/`, and two ZyDDT cells in `error-flow`.

Found on the way, and not this finding's: `@ m:[1, 2]` after `m = "fuera"`
warns `unused variable 'm'` although the program reads it afterwards — the
analyser retires the outer declaration when a loop re-declares the name. The
pattern binding avoided it by assigning a visible name instead of declaring it;
the loop still has it.


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

**Resolution — FIXED, 2026-09-29 (author's decision D3).** `##Kind("message")`
in an expression builds the error, in all three engines: the spelling an error
prints as, and the kind a `:!` matches. It is a value — `$!` is `#1`, `$!!`
propagates it, no `:!` sees it — the kind is any name in any script, and the
message is a String (refused before running when the analyser knows it is not,
`##Type` at run time otherwise). Written together, like every operator since
GLB-031. Held by `corpus/errors/catchable/construir_error.zy`,
`mensaje_de_error_en_ejecucion.zy`, `errors/semantic/mensaje_de_error_no_es_texto.zy`,
two forms in `reject/errors/`, five ZyDDT cells in `error-flow`, and GUIDE § 16.

Applying it here, which is what LDV asks before a finding closes, **did not
work at first**: this program's two functions return a catalogue key, and a
caller could not read the key back out of the error — GAP-GOL-016. With that
closed the same day, `κ::κανόνας` returns `(γεννήσεις, επιβιώσεις)` or
`##Κανόνας(κλειδί)`, `σ::πάρε` the cells or `##Σχήμα(κλειδί)`, and the tuples
with an empty-string slot for "no error" are gone from all seven callers. The
suite's golden did not move, and the command line's errors read the same in all
four locales on all three engines.

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

**Resolution — FIXED by ZyDDT `GLB-060` (2026-09-25).** Found again,
independently, by the author in `zyV.zy`: the warning now stays quiet when both
bounds are integer literals — `-1` included — or constants, in all three engines,
and still fires when either bound is computed. `@ i:-1..1 { }` prints no warning.
The second half — a way to silence the warning on a *dynamic* bound the
program has already guarded — is **REJECTED** (author's decision D6,
2026-09-29). The descending range was kept *with* its warning by an earlier
decision of the author's; a switch that silences it would undo that decision
one call site at a time.

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

**Resolution — DOCUMENTED, 2026-09-29.** Measured before writing it: the
interception is narrower than the title says. `run`'s own options (`--vm`,
`--tw`, `--script`, `--keep-temp`, `-h`/`--help`) are recognised after the file
name only **until the first argument that is not one of them** — `zymbol run
x.zy a --help` hands the program `["a", "--help"]`, and `--version` always
reaches it. A bare `--` ends them, and it works for a `.zyp` as well
(`zymbol run app.zyp -- --help`). `GUIDE.md` § 3 "CLI Arguments" now says so with
five examples. Changing the rule itself — every argument after the file goes to
the program — would make `zymbol run x.zy --vm` stop meaning the VM. The author
kept the rule and closed the finding with the documentation (decision D6,
2026-09-29).

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

**Resolution — FIXED, 2026-09-29.** `node tests/run_one.mjs FILE.zy [--input FILE]
[-- ARG...]`: everything after a bare `--` is the program's command line, spelled
the way `zymbol run FILE.zy -- ARG...` spells it, so one argument vector reaches
all three engines. Measured on this program:
`ζωή.zy -- -p glider -r 10 -c 10 -b -n 3 --print -L hi` gives byte-identical
output under `zytw`, `zyvm` and `zyjs`.

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

**Resolution — FIXED, 2026-09-30 (author's decisions D5 and D11).** A headless
mode in the CLI, asked for and never guessed: `zymbol run app.zy --keys app.keys`
draws `>>|` on a virtual 24×80 screen, feeds `<<|` and `<<|?` from the file, and
writes each block's last frame to the output as text. Both Rust engines share one
implementation (`zymbol_common::vscreen`), so a frame cannot mean two things.
Without `--keys`, `>>|` with no terminal still fails — GLB-018 C stands.

Two things were measured before building it, and both changed the plan:

- **D5 had assumed the screen could be reached from a subscript.** It cannot: a
  subscript receives the program's arguments (D10), never `zymbol run`'s options.
  The in-process road was the one that worked — the suites already call
  `εκκίνηση::ξεκίνα(lang, args)`, which enters `>>|` like the program does.
- **"The last frame" was not enough.** Two of the sixteen cases check a picker
  that is closed by the time the program ends. The key script gained `SHOW`,
  which writes the frame of that moment; `WAIT n` makes a polling loop advance by
  polls rather than by a clock, so no case depends on timing.

`δοκιμές/οθόνη/` holds the sixteen cases of the old `οθόνη.py`, each a two-line
program, a `.keys` file and a golden, graded on both Rust engines by the same
gate as every other golden; `zyq` passes `--keys` when a `.keys` file sits beside
the program. `οθόνη.py` is deleted, and with it the last file of GoL that was not
Zymbol. `zyquality/tui/`'s pty driver stays: it tests the real terminal path —
how crossterm decodes an arrow — which a virtual screen by design does not touch.
Held by `corpus/output/pantalla_virtual.zy` with its key script.

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

**Resolution — FIXED, 2026-09-30 (author's decisions D4 and D10), by composition
and without a new mark.** D4 asked for a measurement before any capture block
was designed: could `</ … />`, now that it returns a status (GAP-GOL-011), test
what a program says? It could not, for one reason — a subscript inherited its
caller's arguments and could not be given its own; `</ ./x.zy uno />` was
`file not found: ./x.zy uno`. D10 supplied that piece and nothing else: the words
after the path are the subscript's command line, literal like the path, so
`zymbol package` and AGT-3 still read the reachable program without running it.

`δοκιμές/έξοδος.zy` is the suite this finding said could not be written. It runs
`ζωή.zy` as a subscript, one literal command line per check, and asserts what it
says against the program's own catalogue: the pattern list in all four
languages, four malformed rules each refused in the right language with status
2, an unknown pattern and an unknown option, and a batch run. 20 checks, both
Rust engines, its own golden in the gate. It is a script of its own and not a
module of `όλα.zy`, because the browser engine has no process to run a
subscript in, and `όλα.zy` is the suite that agrees on all three.

It caught one wrong expectation on its first run — `B/S23` is a valid rule, not
an empty half — which is the other half of the point: a check that can fail.
The in-process half of the finding — capturing what a function *in this
process* prints — remains without a mechanism, and nothing here needed one.

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

**Resolution — FIXED, 2026-09-30 (author's decisions D2 and D8).** A status
other than 0 is a soft `##IO` error that carries it, in both Rust engines, and
`##IO(m) =>` (GAP-GOL-016) reads it back:

| | before | now |
|---|---|---|
| `<\ "exit 3" \>` | `""` | `##IO(exit 3)` |
| `<\ "echo err >&2; exit 2" \>` | `"err"` | `##IO(exit 2: err)` — stderr, else stdout |
| `</ sub.zy />` where sub gives `<~ 3` | its output, the 3 lost | `##IO(exit 3: <its output>)` |
| `</ sub.zy />` where sub fails | raised | raised, unchanged (GLB-017 I) |

The subscript half met an earlier decision: GLB-017 I (2026-09-26) raises a
subscript that fails. D8 kept it — only a status the subscript *gives* becomes a
value; a crash is not a status it gave. `<\ \>` turns every status other than 0
into a value, because a shell cannot tell a failure from a crash.

**What the change broke, measured before and after.** The corpus: nothing. Seven
of eight applications: nothing. ZyAudit: six of eight suites — and not because
of D2. Its suites read `源文件/计算器.zy` and `i18n.json` relative to where they
run, and `zyq` runs every program in an empty scratch directory. So in the gate
the auditor **had never audited anything**: six goldens recorded the shell's
`sh: 1: cannot open 源文件/计算器.zy: No such file`, `函数=0` and blank labels as
the result, and matched them every run. D2 turned that text into `##IO` errors,
the goldens stopped matching, and the suite's long run of passing on a
missing file became visible. Fixed by the author's decision D9: an application
declares `fixtures` in `zyquality/project/apps.toml`, `zyq --fixture` copies them
into each scratch directory, and the six goldens were re-recorded from a real
run — `总计=60`, nine functions with their lines and arities, the report in
three languages. The re-recording was reviewed line by line; nothing in the new
goldens is a failure message.

Four places depended on `""` for a failure that is part of their normal flow,
and now test `$!`: ZyAudit's `printenv GEMINI_API_KEY`, its `grep … | grep -v`
that finds no function, its `jq` lookup (whose documented fallback is the empty
string), and 囲碁's `printenv ZYGO_KIFU` in `棋戦.zy`. Held by
`corpus/errors/catchable/estado_de_salida.zy` (with two subscripts beside it) and
two ZyDDT cells in `environment`.

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

**Resolution — DONE, 2026-09-29.** `USERAPPI18N.md` § 14 now has three traps
(the third with the program above, checked on all three engines) and § 12 an
item 15. The last sentence of this entry turned out to be wrong, and the
document says so instead: a sweep of every application's locale files found 76
candidates and three real cases — the rest were keys, syntax the user types in
ASCII, and titles. Searchable, not decidable: a checklist item read by a person,
not a gate.

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

**Resolution — DONE for every suite that counts its own failures, 2026-09-29.**
The 44 split into two kinds, and only one of them has a result to return:

| kind | suites | what changed |
|---|---|---|
| self-asserting, with a failure counter | 22 — 囲碁 8, चतुरङ्गम् 6, Serpiente 2, Hov veS 1, ZyBank 5 | the failure branch ends with `<~ 1` |
| print values, judged by a golden | 22 — Zofía 12, ZyAudit 8, 囲碁's `性能試験` and `自戦試験` | nothing: they count nothing, so there is nothing to return. Making them self-asserting is separate work |

The goldens did not move (a passing run prints what it printed). Checked the
other way too: forcing one failure into `文字試験.zy` exits 1, restored it
exits 0. The four runners that decided by text — `全試験.sh`, `todas.sh` of
Serpiente, `Hoch.sh` (grep for `FAIL`/`FALLA`) and ZyBank's `todas.sh` (grep for
`TODO BIEN`) — now read the exit status; `全試験.sh` also gained `棋譜試験`, a
self-asserting suite it had never run. चतुरङ्गम्'s runner already compared
goldens and was left alone.

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
recurring maintenance bill. The decision was the author's, and it was taken on
**2026-09-29**: escalate.

What decided it is in the paragraph above, restated as `LDV.md` now records it:
the grid found little, and the distance that paid was a domain the project moved
into without setting out to — **an application testing itself from inside the
language**. No earlier project had been asked to do that in Zymbol. The
maintenance bill turned out lower than feared: the program crossed MEM-2 and
HLZ-015 without a change, and its suite is the only one in the gate that agrees
under all three engines, so it is also the only application the browser engine
can be graded on.

Escalating cost one change to the program: the batch mode printed `elapsed Nms`,
a number that differs on every run and so cannot sit in a golden. It now prints
it only with `--time`. The help text named a `--gens` option that does not exist
(the option is `--batch`), in all four locales; that was corrected in the same
change.
