# GoL — El Juego de la Vida

[English](README.md) · **Español**

El [Juego de la Vida](https://es.wikipedia.org/wiki/Juego_de_la_vida) de Conway como
editor y simulador de terminal a pantalla completa, en **cuatro idiomas** —
Ελληνικά, Español, English, हिन्दी — escrito en [Zymbol](https://zymbol-lang.org)
v0.0.9.

```bash
zymbol run vida.zy                    # español
zymbol run ζωή.zy                     # ελληνικά
zymbol run life.zy                    # english
zymbol run जीवन.zy                    # हिन्दी
```

Marca las casillas iniciales con el cursor, pulsa ENTER y mira. Pulsa `l` en
cualquier momento para cambiar de idioma, incluso a mitad de una simulación.

---

## Por qué existe

No es una demostración. Empezó como **banco de medición**: su trabajo era decir lo
que cuesta una generación de Vida en cada motor de Zymbol, y registrar qué le
resultó fácil y qué no al lenguaje. Los hallazgos están en [HALLAZGOS.md](HALLAZGOS.md);
los números en [`μέτρηση/`](μέτρηση/).

Desde el **2026-09-29** es proyecto de Validación Dirigida por el Lenguaje, el
noveno (`zymbol-design/LDV.md` § 5.1). Al principio se dejó fuera a propósito — el
§6 dice que el método *«escala con la distancia de dominio, no con el tamaño»*, y
éste es el quinto juego de rejilla en terminal después de 囲碁, चतुरङ्गम्,
Serpiente y Hov veS — y se escaló porque sus hallazgos lo justificaron: la
distancia que pagó no fue la rejilla sino una aplicación que se prueba a sí misma
desde dentro del lenguaje. La última sección de HALLAZGOS.md tiene el argumento. Su
suite está en el gate como `gol` (`zyquality/project/apps.toml`), y es la única
aplicación ahí que coincide en los tres motores.

---

## La pantalla

```
▸ CORRE     gen 6/24   41 células vivas   8×40 toro   B3/S23   150 ms   cañón de Gosper
────────────────────────────────────────────────────────────────────────────────
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
────────────────────────────────────────────────────────────────────────────────
↑↓←→ mover  SPACE marcar  ↵ correr/parar  n paso  p figura  c limpiar  q salir
```

| Tecla | Hace |
|-------|------|
| `↑ ↓ ← →` | mover el cursor (da la vuelta) |
| `SPACE` | marcar o desmarcar la casilla bajo el cursor |
| `↵` | correr / parar — y, al terminar, reiniciar |
| `n` | avanzar exactamente una generación |
| `p` | **abrir el catálogo de figuras** (las 18, por categoría) |
| `1`–`9` | poner una de las nueve figuras de atajo en el cursor |
| `c` `r` | limpiar / llenar al azar |
| `t` | siguiente tema — `emoji`, `bloques`, `letras` |
| `l` | **cambiar de idioma**, en cualquier momento |
| `+` `-` | duplicar / reducir a la mitad la velocidad |
| `q` | salir |

El mundo se puede editar **mientras corre**. La Vida no tiene fase de preparación,
y un cambio de modo se la habría inventado.

### Para solo

La Vida no termina nunca, así que el programa tiene que saber cuándo no tiene
sentido seguir. Guarda las últimas 16 generaciones y para cuando el mundo **se
extingue**, **se congela** o **repite un fotograma que ya mostró**, diciendo el
periodo:

```
■ el mundo oscila con periodo 15, desde la generación 15   ·   ↵ correr/parar   q salir
```

Dieciséis porque el pentadecatlón tiene periodo 15 y es el ciclo más largo con el
que uno se topa sin buscarlo. Un planeador **no** cuenta como parada: repite su
forma cada 4 generaciones pero en otro sitio, y una figura que viaja no se ha
detenido. `-n N` añade un límite de turnos por encima, para que una figura que
crece también acabe.

### El tablero nunca pasa de la pantalla

Se pida lo que se pida, el mundo se recorta a lo que cabe — y lo dice. Una rejilla
más ancha que la terminal se dibujaría a medias, y las casillas que no se ven
siguen contando vecinos: lo que estarías mirando no sería la Vida.

```bash
$ zymbol run vida.zy -r 200 -c 200 -p glider -b -n 3
21×40 toro  B3/S23  glider (planeador)
el mundo se ajustó a la pantalla
```

---

## Figuras

Las dieciocho están en el catálogo de `p`, agrupadas por lo que son:

| Categoría | Figuras |
|---|---|
| **vida quieta** | bloque · colmena · hogaza · barca · tina |
| **oscilador** | parpadeante · sapo · faro · púlsar (p3) · pentadecatlón (p15) |
| **nave** | planeador · nave ligera · nave media · nave pesada |
| **matusalén** | r-pentominó · hueso duro (muere en la gen. 130) · bellota |
| **cañón** | cañón de Gosper (primer planeador en la gen. 30) |

Cada uno de esos datos entre paréntesis lo comprueba
[`δοκιμές/κόσμος.zy`](δοκιμές/κόσμος.zy) contra la literatura, no contra una
ejecución anterior.

---

## Opciones

```bash
zymbol run vida.zy -- --help         # el `--` primero: -h/--help no llegan al programa
```

| Bandera | Significa |
|---|---|
| `-r, --rows N` / `-c, --cols N` | tamaño del mundo (recortado a la pantalla) |
| `-p, --pattern NOMBRE` | empezar por una figura conocida, centrada |
| `-R, --rule REGLA` | `B3/S23` (por defecto), `B36/S23`, `B2/S`, … |
| `-t, --theme NOMBRE` | `emoji` (por defecto), `block`, `ascii` |
| `-d, --delay MS` | milisegundos por generación |
| `-x, --random` / `-s, --seed N` | inicio al azar, reproducible desde su semilla |
| `-e, --edges` | el mundo tiene bordes (por defecto es un toro) |
| `-n, --turns N` | parar después de N generaciones |
| `--run` | arrancar corriendo en vez de editando |
| `-b, --batch` | correr sin pantalla y dar el informe |
| `--every K` / `--print` / `--time` | con `--batch`; `--time` añade los milisegundos transcurridos |
| `-L, --lang CÓDIGO` | `el` `es` `en` `hi` |
| `-l, --list` | figuras, temas e idiomas |

**Las banderas son ASCII e inglesas mientras todo lo de dentro del programa está en
griego.** Una línea de órdenes es la única superficie escrita para que la lea una
*máquina* — un shell, un Makefile, un trabajo de CI — que es la misma regla que
sigue `std/time::format` cuando se niega a usar el modo de cifras. (El shell está
de acuerdo, y no en abstracto: `μέτρηση/όλα.zy` construye líneas de orden con
`<\ … \>` para arrancar los otros motores, y todas son ASCII — un tamaño, un
número de generaciones, una ruta. El griego vale en un identificador de Zymbol y
es un error de sintaxis en un nombre de variable de shell.)

---

## Los cuatro idiomas

Construido contra `zymbol-design/USERAPPI18N.md`,
los catorce puntos de la lista:

- **El idioma es estado de módulo, nunca un parámetro.** Ni una función de este
  proyecto lleva argumento de idioma (§1, §2).
- **Las claves están en griego** —el idioma en que está escrito el programa— con
  prefijo de dominio en todas (`τέλος.ακίνητο`, nunca `ακίνητο`), que es lo que
  mantiene decidible el «traducción igual a clave significa que falta» también en
  griego (§3).
- **Las frases con números son funciones del idioma**, no concatenación en el punto
  de llamada: `φράση_πληθυσμού`, `φράση_τέλους`, `φράση_κόσμου`, `φράση_ρυθμού` (§4).
- **Todos los anchos pasan por `std/term::width`**, a través de una capa griega de
  re-exportación ([`πρότυπο/τερματικό.zy`](πρότυπο/τερματικό.zy)) para que el código
  de dibujo no lea nunca un identificador inglés (§5, §9).
- **Los marcos se construyen midiendo el contenido**
  ([`εμφάνιση/πλαίσιο.zy`](εμφάνιση/πλαίσιο.zy)), nunca tecleados como literales con
  el relleno dentro (§6).
- **El idioma se cambia dentro del juego**, con redibujado completo, y el nombre de
  cada idioma está escrito en sí mismo: `Español` es `Español` estés leyendo griego
  o hindi (§7).
- **Un punto de entrada por idioma** (§8), y **una puerta** que recorre 87 claves ×
  4 idiomas × cada rama compuesta, en los dos motores (§10).
- **El hindi manda sobre la escritura de las cifras.** Elegirlo activa `#०९#` una
  vez en el distribuidor, y todos los números que imprime el programa lo siguen
  —`पीढ़ी १३० में सब मर गए`— sin que ningún punto de llamada sepa nada (§14).

Añadir un quinto idioma son **tres cambios**: un `γλώσσα/<Nombre>.zy` que cumpla el
contrato de cinco funciones, una importación en el distribuidor y una rama en cada
reparto. La puerta lo comprueba después clave por clave.

> **Falta**, y se dice en vez de disimularlo: hay README en inglés y en español, no
> en griego ni en hindi. Es el punto 14 de la lista y el que más se salta, porque
> no falla nada cuando lo saltas.

---

## Pruebas

**Todas las comprobaciones están escritas en Zymbol y cada suite decide por sí
misma.** Cada una sale con 1 si algo se rompió, así que una suite que revienta a
mitad no se puede confundir con una que pasó — que es justo lo que siempre pudo
pasar con un `grep -q FAIL` sobre la salida de un programa.

```bash
zymbol run      δοκιμές/όλα.zy           # todas las suites
zymbol run --vm δοκιμές/όλα.zy           # en la VM de registros
zymbol run      δοκιμές/όλα.zy -v        # con todos los ✓
zymbol run      δοκιμές/όλα.zy κόσμος    # una sola suite
node ../web/tests/run_one.mjs δοκιμές/όλα.zy    # en el motor del navegador
```

**El runner también es Zymbol.** [`δοκιμές/όλα.zy`](δοκιμές/όλα.zy) importa las
cinco suites como módulos y las llama — no hay shell en ninguna parte, que importa
porque un runner en shell estaría diciendo que para ejecutar programas de Zymbol
hace falta algo que no es Zymbol. Y además el runner se rompe en la misma
ejecución en que se rompan los módulos.

Esa forma no fue una elección libre: `<\ … \>` devuelve la salida de un comando y
**tira su código de salida**, así que un runner hecho de la manera obvia no habría
podido decir qué suite falló ([GAP-GOL-011](HALLAZGOS.md#gap-gol-011)).

| Suite | Comprueba | Casos |
|---|---|---|
| [`κόσμος.zy`](δοκιμές/κόσμος.zy) | la regla, y cada figura contra la literatura | 42 |
| [`τέλος.zy`](δοκιμές/τέλος.zy) | cuándo para el mundo, y con qué periodo | 39 |
| [`γλώσσα.zy`](δοκιμές/γλώσσα.zy) | 87 claves × 4 idiomas, cada rama compuesta, la rotación | 34 |
| [`όψη.zy`](δοκιμές/όψη.zy) | dos columnas por signo, marcos cuadrados en todo idioma, el tope de pantalla | 60 |
| [`εκκίνηση.zy`](δοκιμές/εκκίνηση.zy) | la línea de órdenes entera, llamando al módulo | 20 |

La línea de órdenes se prueba llamando directamente a
`εκκίνηση::ξεκίνα(idioma, args)`, así que tampoco hace falta shell para conducir el
programa — aunque esos 20 casos solo pueden comprobar el **código de salida**,
porque un programa no puede capturar lo que imprime su propio código
([GAP-GOL-010](HALLAZGOS.md#gap-gol-010)). Lo que el programa *dijo* se imprime
donde un humano lo ve y no lo comprueba nadie.

**Una prueba no está en Zymbol, y no puede estarlo.**
[`δοκιμές/οθόνη.py`](δοκιμές/οθόνη.py) conduce el editor por un pty de verdad
—dieciséis casos, incluidos el catálogo de figuras, el cambio de idioma en vivo,
las condiciones de parada y las cifras en devanagari, y pilló tres defectos reales
en sus primeras ejecuciones. No está ahí porque Python fuera cómodo: `>>|` da
error si el proceso no tiene TTY, a `<<|` no se le puede dar una secuencia de
teclas escrita, y nada en el lenguaje lanza un proceso, así que **el editor es la
única parte de este programa a la que ningún código Zymbol llega**
([GAP-GOL-009](HALLAZGOS.md#gap-gol-009)). Seis aplicaciones de este taller
dibujan una pantalla; ninguna la prueba.

**Los valores esperados no salen de este programa.** Los periodos, el
desplazamiento del planeador, las poblaciones del r-pentominó en las generaciones
1/10/20/50, el hueso duro muriendo en la 130, el cañón de Gosper soltando su primer
planeador en la 30: todo calculado por una implementación de referencia
independiente y contrastado con la literatura. Un golden grabado de la propia cosa
que se examina solo demuestra que sigue haciendo lo que hacía.

---

## Qué mide

`μέτρηση/βάση.zy` corre la misma generación de tres maneras —con una llamada por
casilla, con la cuenta en línea, y sin construir la rejilla siguiente— para que el
número separe tres costes en vez de mezclarlos.

```bash
zymbol run μέτρηση/όλα.zy               # 32 48 64, diez generaciones
zymbol run μέτρηση/όλα.zy 100 -g 20     # un mundo mayor, más generaciones
zymbol run μέτρηση/όλα.zy 48 --sin-js   # sin el motor del navegador
```

Este runner **también** es Zymbol, y aquí sí lanza otros procesos de verdad: la
pregunta es cuánto cuestan tres *motores*, y un programa corre en uno. `<\ … \>`
basta porque lo único que hace falta de vuelta es la salida; el código de salida
que tira ([GAP-GOL-011](HALLAZGOS.md#gap-gol-011)) es la razón de que una
ejecución fallida salga como `—` y no como error.

| lado | motor | A llamada+construir | B construir | C contar | ns/casilla | A/B |
|------|--------|--------|--------|--------|--------------|-----|
| 64 | `zytw` | 1626 ms | 1625 | 1653 | 19 849 | 1,00 |
| 64 | `zyvm` | 252 ms | 181 | 183 | **3 076** | 1,39 |
| 64 | `zyjs` | 6050 ms | 5195 | 4831 | 147 705 | 1,16 |
| 100 | `zytw` | 3990 ms | 3963 | 4043 | 19 950 | 1,01 |
| 100 | `zyvm` | 618 ms | 451 | 448 | **3 090** | 1,37 |

- la VM de registros va **6,4×** el árbol aquí, estable al ±1,7% y plana en tamaño
- el motor del navegador va **7,4× más lento que el árbol**, 48× más lento que la VM
- **construir una rejilla nueva cada generación sale gratis** (B ≈ C en los tres) —
  el modelo `Rc` + copia al escribir de HLZ-012/HLZ-014, medido sobre carga real
- **una llamada por casilla cuesta el 39% en la VM y nada en el árbol** —
  [IDEA-GOL-007](HALLAZGOS.md#idea-gol-007)

Vuelve a medir antes de citar: estos son los del intérprete del 2026-09-04.

---

## Autoría

Escrito con [Claude Code](https://claude.ai/code) bajo la dirección del autor, igual
que el intérprete y las aplicaciones LDV (`interpreter/README.md` § Authorship & AI
Collaboration).
