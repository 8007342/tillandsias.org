"""Hand-authored SVG figures for the tillandsias.org content matrix.

Every figure is theme-agnostic: it draws with `currentColor` and the CSS custom
properties the page already defines, so nothing here needs a second palette.
Figures are deliberately small and diagrammatic — they carry one idea each.
"""

_HEAD = ('<figure class="fig"><svg viewBox="0 0 {vb}" role="img" '
         'aria-label="{alt}" preserveAspectRatio="xMidYMid meet">')
_FOOT = '</svg><figcaption>{cap}</figcaption></figure>'


def _wrap(vb, alt, cap, body):
    return _HEAD.format(vb=vb, alt=alt) + body + _FOOT.format(cap=cap)


LAYERS = _wrap(
    "600 250", "Nested layers from host hardware out to apps",
    "A region is layers, not a machine. Each ring only trusts what is inside it.",
    """
    <rect x="8" y="8" width="584" height="234" rx="12" class="s-line" fill="none"/>
    <text x="22" y="30" class="s-lbl">your computer &#183; your disk &#183; your electricity</text>
    <rect x="28" y="44" width="544" height="186" rx="10" class="s-line s-fill1"/>
    <text x="42" y="66" class="s-lbl">a clean Linux machine (made for you on Mac/Windows)</text>
    <rect x="48" y="80" width="504" height="134" rx="9" class="s-line s-fill2"/>
    <text x="62" y="102" class="s-lbl s-accent">the enclave &#8212; a private network with no way out</text>
    <g class="s-box">
      <rect x="66" y="118" width="106" height="42" rx="7"/>
      <rect x="182" y="118" width="106" height="42" rx="7"/>
      <rect x="298" y="118" width="106" height="42" rx="7"/>
      <rect x="414" y="118" width="122" height="42" rx="7"/>
    </g>
    <g class="s-txt">
      <text x="119" y="144">app</text><text x="235" y="144">app</text>
      <text x="351" y="144">app</text><text x="475" y="144">agent</text>
    </g>
    <rect x="66" y="172" width="470" height="32" rx="7" class="s-line s-gate"/>
    <text x="301" y="192" class="s-txt s-amber">the one guarded door out &#8212; everything else is refused</text>
    """)

LOOP = _wrap(
    "600 250", "The closed loop from specs through evidence back to specs",
    "Nothing in the loop is allowed to be the only source of truth. Each arrow is checked by machine.",
    """
    <g class="s-box">
      <rect x="228" y="14" width="144" height="40" rx="8"/>
      <rect x="424" y="86" width="152" height="40" rx="8"/>
      <rect x="356" y="186" width="152" height="40" rx="8"/>
      <rect x="92" y="186" width="152" height="40" rx="8"/>
      <rect x="24" y="86" width="152" height="40" rx="8"/>
    </g>
    <g class="s-txt">
      <text x="300" y="39">specs &#8212; the intent</text>
      <text x="500" y="111">cheatsheets</text>
      <text x="432" y="211">code</text>
      <text x="168" y="211">traces &#8212; evidence</text>
      <text x="100" y="111">litmus &#8212; the line</text>
    </g>
    <g class="s-arrow" fill="none">
      <path d="M374 44 C 424 52 452 66 470 82" marker-end="url(#ah)"/>
      <path d="M508 128 C 500 158 480 176 456 184" marker-end="url(#ah)"/>
      <path d="M354 208 L 248 208" marker-end="url(#ah)"/>
      <path d="M132 184 C 108 174 92 156 88 130" marker-end="url(#ah)"/>
      <path d="M110 82 C 132 62 176 48 224 42" marker-end="url(#ah)"/>
    </g>
    <text x="300" y="130" class="s-lbl s-accent" text-anchor="middle">continuous integration</text>
    <text x="300" y="148" class="s-lbl" text-anchor="middle">refuses the merge if any arrow breaks</text>
    """)

STAIRCASE = _wrap(
    "600 270", "Residual distance falling release over release toward a floor above zero",
    "Schematic: if comparable residuals never rise, they approach a "
    "floor, and nobody has proven that floor is zero.",
    """
    <line x1="58" y1="20" x2="58" y2="212" class="s-axis"/>
    <line x1="58" y1="212" x2="576" y2="212" class="s-axis"/>
    <text x="16" y="26" class="s-lbl">far</text>
    <text x="8" y="200" class="s-lbl">close</text>
    <text x="300" y="248" class="s-lbl" text-anchor="middle">successive releases &#8212; each one re-raises the bar</text>
    <path d="M58 44 H128 V78 H198 V96 H268 V132 H338 V146 H408 V164 H478 V172 H548"
          class="s-step" fill="none"/>
    <g class="s-dot">
      <circle cx="128" cy="44" r="3.5"/><circle cx="198" cy="78" r="3.5"/>
      <circle cx="268" cy="96" r="3.5"/><circle cx="338" cy="132" r="3.5"/>
      <circle cx="408" cy="146" r="3.5"/><circle cx="478" cy="164" r="3.5"/>
      <circle cx="548" cy="172" r="3.5"/>
    </g>
    <line x1="58" y1="186" x2="576" y2="186" class="s-floor"/>
    <text x="570" y="180" class="s-lbl s-amber" text-anchor="end">the floor &#8212; possibly not zero</text>
    <line x1="58" y1="212" x2="576" y2="212" class="s-axis"/>
    <text x="570" y="228" class="s-lbl" text-anchor="end">zero would mean &#8220;finished&#8221;. No proof it is reachable.</text>
    """)

LLN = _wrap(
    "600 260", "An illustration of averaging, not a measured convergence result",
    "Schematic only: averaging can reduce variation under suitable hypotheses. "
    "Dependent iterations and persistent bias need a separate argument; this diagram is not evidence.",
    """
    <text x="150" y="24" class="s-lbl" text-anchor="middle">one big slow iteration</text>
    <text x="450" y="24" class="s-lbl s-accent" text-anchor="middle">many small fast iterations</text>
    <line x1="30" y1="150" x2="270" y2="150" class="s-axis"/>
    <line x1="330" y1="150" x2="570" y2="150" class="s-axis"/>
    <line x1="30" y1="96" x2="270" y2="96" class="s-target"/>
    <line x1="330" y1="96" x2="570" y2="96" class="s-target"/>
    <text x="34" y="88" class="s-lbl s-amber">truth</text>
    <text x="334" y="88" class="s-lbl s-amber">truth</text>
    <circle cx="196" cy="60" r="7" class="s-miss"/>
    <line x1="196" y1="67" x2="196" y2="92" class="s-skew"/>
    <text x="196" y="184" class="s-lbl" text-anchor="middle">lands off-target,</text>
    <text x="196" y="200" class="s-lbl" text-anchor="middle">and you cannot see by how much</text>
    <g class="s-dot2">
      <circle cx="352" cy="72" r="2.6"/><circle cx="370" cy="118" r="2.6"/>
      <circle cx="388" cy="66" r="2.6"/><circle cx="406" cy="124" r="2.6"/>
      <circle cx="424" cy="80" r="2.6"/><circle cx="442" cy="110" r="2.6"/>
      <circle cx="460" cy="84" r="2.6"/><circle cx="478" cy="106" r="2.6"/>
      <circle cx="496" cy="90" r="2.6"/><circle cx="514" cy="100" r="2.6"/>
      <circle cx="532" cy="93" r="2.6"/><circle cx="550" cy="98" r="2.6"/>
    </g>
    <path d="M352 108 C 420 104 480 98 566 96" class="s-mean" fill="none"/>
    <text x="450" y="184" class="s-lbl s-accent" text-anchor="middle">an illustrative running average</text>
    <text x="450" y="200" class="s-lbl" text-anchor="middle">no convergence theorem established here</text>
    <text x="300" y="234" class="s-lbl" text-anchor="middle">Bounded bias alone does not make the average reach the truth.</text>
    """)

LATTICE = _wrap(
    "600 210", "The evidence ladder from absent to evidence-bundled",
    "Evidence only ever climbs. A claim may not descend a rung without an explicit, recorded "
    "scope change.",
    """
    <g class="s-box">
      <rect x="10" y="76" width="82" height="38" rx="7"/>
      <rect x="106" y="76" width="82" height="38" rx="7"/>
      <rect x="202" y="76" width="82" height="38" rx="7"/>
      <rect x="298" y="76" width="88" height="38" rx="7"/>
      <rect x="400" y="76" width="88" height="38" rx="7"/>
      <rect x="502" y="76" width="88" height="38" rx="7"/>
    </g>
    <g class="s-txt s-sm">
      <text x="51" y="100">absent</text><text x="147" y="100">declared</text>
      <text x="243" y="100">traced</text><text x="342" y="100">tested +</text>
      <text x="444" y="100">tested &#8722;</text><text x="546" y="100">observed</text>
    </g>
    <g class="s-arrow" fill="none">
      <path d="M92 95 L 102 95" marker-end="url(#ah)"/>
      <path d="M188 95 L 198 95" marker-end="url(#ah)"/>
      <path d="M284 95 L 294 95" marker-end="url(#ah)"/>
      <path d="M386 95 L 396 95" marker-end="url(#ah)"/>
      <path d="M488 95 L 498 95" marker-end="url(#ah)"/>
    </g>
    <text x="300" y="42" class="s-lbl" text-anchor="middle">less evidence &#8594; more evidence, one direction only</text>
    <path d="M540 130 C 400 168 200 168 60 130" class="s-forbid" fill="none"/>
    <text x="300" y="182" class="s-lbl s-red" text-anchor="middle">going backwards is not a bug report, it is a rejected merge</text>
    """)

CRDT = _wrap(
    "600 250", "Two agents appending independently and folding to the same result",
    "With the same delivered facts and valid merge rules, replicas agree regardless of arrival order. "
    "This illustration shows set union, not every field in the ledger.",
    """
    <text x="120" y="26" class="s-lbl">agent A &#8212; offline</text>
    <text x="400" y="26" class="s-lbl">agent B &#8212; offline</text>
    <g class="s-box">
      <rect x="60" y="42" width="150" height="30" rx="6"/>
      <rect x="60" y="80" width="150" height="30" rx="6"/>
      <rect x="340" y="42" width="150" height="30" rx="6"/>
      <rect x="340" y="80" width="150" height="30" rx="6"/>
    </g>
    <g class="s-txt s-sm">
      <text x="135" y="62">a new fact</text><text x="135" y="100">another fact</text>
      <text x="415" y="62">a third fact</text><text x="415" y="100">a fourth</text>
    </g>
    <g class="s-arrow" fill="none">
      <path d="M135 116 C 150 148 220 156 268 162" marker-end="url(#ah)"/>
      <path d="M415 116 C 400 148 330 156 288 162" marker-end="url(#ah)"/>
    </g>
    <rect x="176" y="172" width="248" height="40" rx="8" class="s-line s-gate"/>
    <text x="300" y="197" class="s-txt s-accent">fold &#8212; order does not matter</text>
    <text x="300" y="236" class="s-lbl" text-anchor="middle">set union preserves facts; registers choose a winning value</text>
    """)

GATE = _wrap(
    "600 230", "A litmus test as a decision boundary with negative controls",
    "A test that only ever passes proves nothing. Each boundary is pinned from both sides.",
    """
    <line x1="300" y1="30" x2="300" y2="176" class="s-boundary"/>
    <text x="300" y="204" class="s-lbl s-accent" text-anchor="middle">the boundary the specification draws</text>
    <text x="150" y="30" class="s-lbl" text-anchor="middle">must hold</text>
    <text x="450" y="30" class="s-lbl" text-anchor="middle">must NOT hold</text>
    <g class="s-dot">
      <circle cx="96" cy="70" r="5"/><circle cx="150" cy="98" r="5"/>
      <circle cx="120" cy="134" r="5"/><circle cx="196" cy="70" r="5"/>
      <circle cx="206" cy="140" r="5"/>
    </g>
    <g class="s-miss-g">
      <circle cx="400" cy="72" r="5"/><circle cx="452" cy="106" r="5"/>
      <circle cx="418" cy="142" r="5"/><circle cx="500" cy="82" r="5"/>
      <circle cx="508" cy="146" r="5"/>
    </g>
    <text x="150" y="168" class="s-lbl s-accent" text-anchor="middle">positive cases</text>
    <text x="450" y="168" class="s-lbl s-red" text-anchor="middle">negative controls</text>
    """)

EPHEMERAL = _wrap(
    "600 210", "Repairing in place versus destroying and recreating",
    "Nothing at runtime is repaired. It is thrown away and built again from the recipe — which "
    "is why it comes back identical.",
    """
    <text x="150" y="26" class="s-lbl s-red" text-anchor="middle">the usual way</text>
    <text x="450" y="26" class="s-lbl s-accent" text-anchor="middle">this way</text>
    <g class="s-box">
      <rect x="52" y="44" width="88" height="34" rx="6"/>
      <rect x="160" y="44" width="88" height="34" rx="6"/>
      <rect x="52" y="106" width="88" height="34" rx="6"/>
      <rect x="160" y="106" width="88" height="34" rx="6"/>
    </g>
    <g class="s-txt s-sm">
      <text x="96" y="65">it breaks</text><text x="204" y="65">poke at it</text>
      <text x="96" y="127">still odd</text><text x="204" y="127">poke again</text>
    </g>
    <g class="s-arrow" fill="none">
      <path d="M140 61 L 156 61" marker-end="url(#ah)"/>
      <path d="M204 82 L 204 100" marker-end="url(#ah)"/>
      <path d="M160 123 L 144 123" marker-end="url(#ah)"/>
    </g>
    <text x="150" y="176" class="s-lbl s-red" text-anchor="middle">drifts somewhere nobody can reproduce</text>
    <g class="s-box">
      <rect x="336" y="44" width="96" height="34" rx="6"/>
      <rect x="452" y="44" width="106" height="34" rx="6"/>
      <rect x="392" y="106" width="130" height="34" rx="6"/>
    </g>
    <g class="s-txt s-sm">
      <text x="384" y="65">it breaks</text><text x="505" y="65">throw it away</text>
      <text x="457" y="127">build from the recipe</text>
    </g>
    <g class="s-arrow" fill="none">
      <path d="M432 61 L 448 61" marker-end="url(#ah)"/>
      <path d="M505 82 C 505 96 500 100 486 104" marker-end="url(#ah)"/>
    </g>
    <text x="450" y="176" class="s-lbl s-accent" text-anchor="middle">identical every time, on every machine</text>
    """)


FIXPOINT = _wrap(
    "600 240", "An ascending chain stabilising at a least fixed point",
    "Monotone refinement over a finite lattice cannot ascend forever. It stabilises \u2014 and the "
    "step where it stops is what \u201cdone\u201d means. Provided refinement really is monotone.",
    """
    <line x1="56" y1="24" x2="56" y2="190" class="s-axis"/>
    <line x1="56" y1="190" x2="566" y2="190" class="s-axis"/>
    <text x="14" y="34" class="s-lbl">more</text>
    <text x="10" y="184" class="s-lbl">less</text>
    <text x="300" y="222" class="s-lbl" text-anchor="middle">applications of the refinement operator</text>
    <path d="M56 174 H116 V138 H176 V108 H236 V86 H296 V72 H356 V66 H416 V66 H476 V66 H546"
          class="s-step" fill="none"/>
    <g class="s-dot">
      <circle cx="116" cy="174" r="3.5"/><circle cx="176" cy="138" r="3.5"/>
      <circle cx="236" cy="108" r="3.5"/><circle cx="296" cy="86" r="3.5"/>
      <circle cx="356" cy="72" r="3.5"/><circle cx="416" cy="66" r="3.5"/>
      <circle cx="476" cy="66" r="3.5"/><circle cx="546" cy="66" r="3.5"/>
    </g>
    <line x1="56" y1="52" x2="566" y2="52" class="s-floor"/>
    <text x="562" y="46" class="s-lbl s-amber" text-anchor="end">lattice top &#8212; never reached, and need not be</text>
    <text x="470" y="94" class="s-lbl s-accent" text-anchor="middle">refine(refine(x)) = refine(x)</text>
    <text x="470" y="110" class="s-lbl" text-anchor="middle">the chain stops moving</text>
    """)

GALOIS = _wrap(
    "600 230", "The abstraction and concretisation pair that is not established",
    "Without the adjunction, a closed obligation does not transport back to a statement about the "
    "program. The arrows exist; the law relating them is not proven.",
    """
    <rect x="34" y="52" width="200" height="120" rx="10" class="s-line s-fill1"/>
    <rect x="366" y="52" width="200" height="120" rx="10" class="s-line s-fill1"/>
    <text x="134" y="40" class="s-lbl" text-anchor="middle">concrete: program behaviours</text>
    <text x="466" y="40" class="s-lbl" text-anchor="middle">abstract: obligation states</text>
    <g class="s-dot"><circle cx="104" cy="92" r="4"/><circle cx="150" cy="128" r="4"/>
      <circle cx="188" cy="100" r="4"/></g>
    <g class="s-dot2"><circle cx="436" cy="96" r="4"/><circle cx="486" cy="126" r="4"/></g>
    <path d="M240 92 C 290 78 320 78 360 88" class="s-arrow-a" fill="none" marker-end="url(#ah)"/>
    <path d="M360 140 C 320 150 290 150 240 136" class="s-arrow-a" fill="none" marker-end="url(#ah)"/>
    <text x="300" y="74" class="s-lbl s-accent" text-anchor="middle">&#945;</text>
    <text x="300" y="166" class="s-lbl s-accent" text-anchor="middle">&#947;</text>
    <text x="300" y="206" class="s-lbl s-red" text-anchor="middle">&#945;(c) &#8849; a &#8660; c &#8849; &#947;(a) &#8212; not established</text>
    """)

REFINEMENT_MESH = _wrap(
    "600 300", "Three local refinement traces and one shared residual trace",
    "A schematic engineering model: each checked change can move one local residual, while the shared record is judged against aligned specifications. It is not a probability measurement or a convergence proof.",
    """
    <text x="300" y="20" class="s-lbl s-accent" text-anchor="middle">local tasks: source + prompt + checks → committed delta</text>
    <g class="s-axis" fill="none">
      <path d="M42 40 V128 H202"/><path d="M222 40 V128 H382"/><path d="M402 40 V128 H562"/>
    </g>
    <g class="s-lbl">
      <text x="45" y="48">accessibility</text><text x="225" y="48">product copy</text><text x="405" y="48">dashboard</text>
      <text x="46" y="145">local target</text><text x="226" y="145">local target</text><text x="406" y="145">local target</text>
    </g>
    <path d="M48 62 L76 76 L104 70 L132 96 L160 102 L192 112" class="s-step" fill="none"/>
    <path d="M228 58 L256 68 L284 90 L312 82 L340 106 L372 112" class="s-step" fill="none"/>
    <path d="M408 66 L436 82 L464 78 L492 94 L520 106 L552 112" class="s-step" fill="none"/>
    <g class="s-dot2"><circle cx="76" cy="76" r="3"/><circle cx="132" cy="96" r="3"/><circle cx="160" cy="102" r="3"/>
      <circle cx="256" cy="68" r="3"/><circle cx="312" cy="82" r="3"/><circle cx="340" cy="106" r="3"/>
      <circle cx="436" cy="82" r="3"/><circle cx="492" cy="94" r="3"/><circle cx="520" cy="106" r="3"/></g>
    <path d="M44 174 V258 H562" class="s-axis" fill="none"/>
    <text x="48" y="182" class="s-lbl">shared residual</text>
    <path d="M52 190 H126 V206 H200 V218 H274 V226 H348 V234 H422 V239 H496 V243 H554" class="s-step" fill="none"/>
    <line x1="44" y1="246" x2="562" y2="246" class="s-floor"/>
    <text x="556" y="276" class="s-lbl s-amber" text-anchor="end">shared target: specifications, aligned before comparison</text>
    <text x="300" y="294" class="s-lbl" text-anchor="middle">a checked commit preserves history; it does not prove every line improved</text>
    """)

AGGREGATE_TRACES = _wrap(
    "600 330", "Several local refinement traces with different targets combined on one timeline",
    "A schematic aggregation: small iterations wobble around and then nearer each local target. The lower view normalises distance to each target before combining workstreams; it is not a probability estimate or proof of shared convergence.",
    """
    <text x="300" y="18" class="s-lbl s-accent" text-anchor="middle">many small refinements; each workstream starts when its work begins</text>
    <path d="M46 38 V210 H566" class="s-axis" fill="none"/>
    <text x="12" y="47" class="s-lbl">distance</text>
    <text x="566" y="226" class="s-lbl" text-anchor="end">accepted refinements →</text>
    <g fill="none" stroke-width="1.2" stroke-dasharray="4 4">
      <path d="M90 68 H554" style="stroke:var(--leaf)"/>
      <path d="M170 104 H554" style="stroke:var(--violet)"/>
      <path d="M250 140 H554" style="stroke:var(--amber)"/>
      <path d="M330 176 H554" style="stroke:var(--rose)"/>
    </g>
    <g class="s-lbl s-sm">
      <text x="94" y="61" style="fill:var(--leaf)">accessibility &amp; language</text>
      <text x="174" y="97" style="fill:var(--violet)">marketing</text>
      <text x="254" y="133" style="fill:var(--amber)">dashboard</text>
      <text x="334" y="169" style="fill:var(--rose)">customer support</text>
    </g>
    <g fill="none" stroke-width="1.8" stroke-linejoin="round">
      <path d="M90 42 L118 90 L146 55 L174 78 L202 62 L230 72 L258 66 L286 70" style="stroke:var(--leaf)"/>
      <path d="M170 58 L198 130 L226 82 L254 116 L282 92 L310 110 L338 98 L366 106" style="stroke:var(--violet)"/>
      <path d="M250 76 L278 168 L306 116 L334 154 L362 128 L390 148 L418 134 L446 144 L474 138" style="stroke:var(--amber)"/>
      <path d="M330 96 L358 202 L386 146 L414 190 L442 158 L470 183 L498 164 L526 178 L554 169" style="stroke:var(--rose)"/>
    </g>
    <g>
      <g fill="var(--leaf)"><circle cx="118" cy="90" r="3"/><circle cx="174" cy="78" r="3"/><circle cx="230" cy="72" r="3"/><circle cx="286" cy="70" r="3"/></g>
      <g fill="var(--violet)"><circle cx="198" cy="130" r="3"/><circle cx="254" cy="116" r="3"/><circle cx="310" cy="110" r="3"/><circle cx="366" cy="106" r="3"/></g>
      <g fill="var(--amber)"><circle cx="278" cy="168" r="3"/><circle cx="334" cy="154" r="3"/><circle cx="390" cy="148" r="3"/><circle cx="474" cy="138" r="3"/></g>
      <g fill="var(--rose)"><circle cx="358" cy="202" r="3"/><circle cx="414" cy="190" r="3"/><circle cx="470" cy="183" r="3"/><circle cx="554" cy="169" r="3"/></g>
    </g>
    <path d="M46 246 V306 H566" class="s-axis" fill="none"/>
    <line x1="46" y1="278" x2="566" y2="278" class="s-floor"/>
    <text x="50" y="254" class="s-lbl">normalised combined view</text>
    <text x="562" y="272" class="s-lbl s-amber" text-anchor="end">0 = each local target</text>
    <g fill="none" stroke-width="1.7" stroke-dasharray="5 4">
      <path d="M90 258 L146 294 L202 266 L258 284 L314 272 L370 280" style="stroke:var(--leaf)"/>
      <path d="M170 248 L226 302 L282 262 L338 288 L394 270 L450 280" style="stroke:var(--violet)"/>
      <path d="M250 242 L306 306 L362 260 L418 290 L474 269 L530 281" style="stroke:var(--amber)"/>
      <path d="M330 238 L386 309 L442 258 L498 292 L554 270" style="stroke:var(--rose)"/>
    </g>
    <text x="300" y="325" class="s-lbl" text-anchor="middle">combine only aligned identities, scope and weights — this is a picture, not a proof</text>
    """)

HASSE = _wrap(
    "600 250", "A product lattice as a Hasse diagram",
    "Two obligations, each a chain of three states, give a nine-element product lattice ordered "
    "componentwise. Real specs multiply many more chains than two.",
    """
    <g class="s-hasse" fill="none">
      <path d="M300 42 L 210 92 M300 42 L 390 92"/>
      <path d="M210 92 L 120 142 M210 92 L 300 142 M390 92 L 300 142 M390 92 L 480 142"/>
      <path d="M120 142 L 210 192 M300 142 L 210 192 M300 142 L 390 192 M480 142 L 390 192"/>
      <path d="M210 192 L 300 226 M390 192 L 300 226"/>
    </g>
    <g class="s-node">
      <circle cx="300" cy="42" r="7"/><circle cx="210" cy="92" r="6"/><circle cx="390" cy="92" r="6"/>
      <circle cx="120" cy="142" r="6"/><circle cx="300" cy="142" r="6"/><circle cx="480" cy="142" r="6"/>
      <circle cx="210" cy="192" r="6"/><circle cx="390" cy="192" r="6"/><circle cx="300" cy="226" r="7"/>
    </g>
    <text x="322" y="34" class="s-lbl s-accent">&#8868; both fully evidenced</text>
    <text x="300" y="246" class="s-lbl s-amber" text-anchor="middle">&#8869; nothing evidenced</text>
    <text x="524" y="146" class="s-lbl" text-anchor="start">joins</text>
    """)

FIGURES = {
    "layers": LAYERS, "loop": LOOP, "staircase": STAIRCASE, "lln": LLN,
    "refinement-mesh": REFINEMENT_MESH,
    "aggregate-traces": AGGREGATE_TRACES,
    "lattice": LATTICE, "crdt": CRDT, "gate": GATE, "ephemeral": EPHEMERAL,
    "fixpoint": FIXPOINT, "galois": GALOIS, "hasse": HASSE,
}

DEFS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6"
        orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="currentColor"/></marker>
</defs></svg>"""


# --- The plant itself -------------------------------------------------------
#
# Tillandsias are air plants: a rosette of narrow recurved leaves, no soil, and
# roots that grip rather than feed. Each level's aside carries one species drawn
# as a glyph — stroke-only, `currentColor`, legible at 15px, no second palette
# and nothing fetched. There is no Tillandsia in Unicode and none in the
# free emoji sets, so these are hand-drawn.

_PLANT = ('<svg viewBox="0 0 16 16" role="img" aria-label="{alt}" fill="none" '
          'stroke="currentColor" stroke-width="1.1" stroke-linecap="round" '
          'stroke-linejoin="round">{body}</svg>')


def _plant(alt, body):
    return _PLANT.format(alt=alt, body=body)


PLANTS = {
    # T. ionantha — a tight upright rosette.
    "ionantha": _plant("a small upright air plant", """
    <path d="M8 15 Q8 9 8 2.6"/>
    <path d="M8 15 Q6.1 9.4 4.6 4.9"/>
    <path d="M8 15 Q9.9 9.4 11.4 4.9"/>
    <path d="M8 15 Q4.4 11 2.4 7.6"/>
    <path d="M8 15 Q11.6 11 13.6 7.6"/>"""),

    # T. bulbosa — a bulbed base with a few snaking leaves.
    "bulbosa": _plant("an air plant with a bulbed base", """
    <path d="M6.4 15 Q5.8 12.2 8 11.4 Q10.2 12.2 9.6 15"/>
    <path d="M8 11.4 C7.4 8.4 5.9 6.8 6.9 3.2"/>
    <path d="M8 11.4 C9.6 8.8 11.6 7.9 10.9 4.6"/>
    <path d="M8 11.4 C6.1 9.6 3.7 9.2 4.1 6.2"/>"""),

    # T. xerographica — a broad rosette whose outer leaves curl back.
    "xerographica": _plant("a broad air plant with curling leaves", """
    <path d="M8 15 L8 4.4"/>
    <path d="M8 15 C7.6 10.2 6.6 6.8 4.8 4.8"/>
    <path d="M8 15 C8.4 10.2 9.4 6.8 11.2 4.8"/>
    <path d="M8 15 C7 11.2 5 9.2 2.7 9.7 C1.8 9.9 1.7 10.8 2.4 11.3"/>
    <path d="M8 15 C9 11.2 11 9.2 13.3 9.7 C14.2 9.9 14.3 10.8 13.6 11.3"/>"""),

    # T. usneoides — Spanish moss, which hangs rather than sits.
    "usneoides": _plant("hanging strands of Spanish moss", """
    <path d="M3.4 1.8 C4.4 4.6 3.3 6.6 4.3 9.2 C4.9 10.8 4.2 12 4.9 14.4"/>
    <path d="M8 1.8 C9 5 7.9 7.4 8.9 10.2 C9.5 11.8 8.9 12.9 9.3 15.2"/>
    <path d="M12.4 2.6 C13 5.4 11.9 7.2 12.7 10 C13.1 11.4 12.6 12.2 12.9 13.8"/>"""),

    # T. caput-medusae — leaves that twist away from a swollen base.
    "caput-medusae": _plant("an air plant with twisting leaves", """
    <path d="M5.9 14.8 Q5.4 11.6 8 10.9 Q10.6 11.6 10.1 14.8"/>
    <path d="M7.2 10.9 C6.1 8.2 4.1 7.2 4.7 4.3 C5 2.9 6.2 2.8 6.7 3.7"/>
    <path d="M8.4 10.9 C8.9 8 10.7 6.7 10.2 4.1"/>
    <path d="M9.4 11.3 C11.2 9.5 13.1 9.5 13.5 7.1"/>"""),
}
