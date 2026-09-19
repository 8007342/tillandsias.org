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

NESTING = _wrap(
    "600 268", "Containers inside a virtual machine inside a host, on two platforms",
    "Containerization is not one layer. Every layer between your hardware and the app is a box, "
    "and Mac and Windows carry one box more than Linux does.",
    """
    <text x="8" y="14" class="s-lbl">Linux</text>
    <rect x="8" y="20" width="282" height="240" rx="12" class="s-line" fill="none"/>
    <text x="22" y="40" class="s-lbl">your computer</text>
    <rect x="22" y="52" width="254" height="196" rx="10" class="s-line s-fill1"/>
    <text x="36" y="72" class="s-lbl s-accent">the enclave &#8212; one private network</text>
    <rect x="34" y="84" width="230" height="152" rx="9" class="s-line s-fill2"/>
    <text x="48" y="104" class="s-lbl">rootless containers, sharing the host kernel</text>
    <g class="s-box">
      <rect x="44" y="116" width="102" height="52" rx="7"/>
      <rect x="154" y="116" width="100" height="52" rx="7"/>
      <rect x="44" y="178" width="210" height="48" rx="7"/>
    </g>
    <g class="s-txt">
      <text x="95" y="146">app</text><text x="204" y="146">app</text>
      <text x="149" y="207">shared services &#183; proxy &#183; mirror</text>
    </g>
    <text x="306" y="14" class="s-lbl">macOS and Windows</text>
    <rect x="306" y="20" width="286" height="240" rx="12" class="s-line" fill="none"/>
    <text x="320" y="40" class="s-lbl">your computer</text>
    <rect x="320" y="52" width="258" height="196" rx="10" class="s-line s-gate"/>
    <text x="334" y="72" class="s-lbl s-amber">a Linux machine, made for you</text>
    <rect x="332" y="84" width="234" height="152" rx="10" class="s-line s-fill1"/>
    <text x="346" y="104" class="s-lbl s-accent">the enclave &#8212; one private network</text>
    <rect x="344" y="116" width="210" height="108" rx="9" class="s-line s-fill2"/>
    <text x="358" y="136" class="s-lbl">rootless containers</text>
    <g class="s-box">
      <rect x="354" y="148" width="94" height="30" rx="6"/>
      <rect x="456" y="148" width="90" height="30" rx="6"/>
      <rect x="354" y="186" width="192" height="28" rx="6"/>
    </g>
    <g class="s-txt">
      <text x="401" y="168">app</text><text x="501" y="168">app</text>
      <text x="450" y="205">shared services</text>
    </g>
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

# Presentation illustrations keep the detailed figures on the level pages intact.
LOCAL_REGION = _wrap(
    "720 230", "A laptop contains workspaces and shared services; pushed work lives upstream",
    "Your tools live together locally. Commit and push the work you want to keep.",
    """
    <ellipse cx="260" cy="206" rx="230" ry="16" fill="var(--leaf)" opacity=".06"/>
    <rect x="46" y="18" width="408" height="176" rx="16" class="s-line s-fill2"/>
    <text x="70" y="45" class="s-lbl s-accent">YOUR COMPUTER</text>
    <g class="s-box"><rect x="70" y="63" width="166" height="64" rx="12"/>
      <rect x="250" y="63" width="180" height="64" rx="12"/>
      <rect x="70" y="139" width="360" height="34" rx="9"/></g>
    <g class="s-txt"><text x="153" y="91">AI assistants</text>
      <text x="153" y="112" class="s-lbl">disposable workspaces</text>
      <text x="340" y="100">Apps + tools</text>
      <text x="250" y="161">Shared services · one local region</text></g>
    <path d="M28 196 H472 L452 209 H48 Z" class="s-line s-fill1"/>
    <path d="M465 108 H526" class="s-arrow" marker-end="url(#ah)"/>
    <text x="496" y="91" class="s-lbl" text-anchor="middle">push</text>
    <rect x="542" y="57" width="154" height="103" rx="18" class="s-line s-gate"/>
    <path d="M600 85 L614 72 H636 V104 H600 Z M614 72 V85 H600" class="s-line" style="stroke:var(--amber)"/>
    <text x="619" y="128" class="s-txt">Durable work</text>
    <text x="619" y="146" class="s-lbl" text-anchor="middle">upstream repository</text>
    """)

PUSH_JOURNEY = _wrap(
    "720 215", "Workspace pushes to the credential-holding mirror, which relays upstream before reporting success",
    "With an upstream: push → relay → acceptance → success.",
    """
    <rect x="14" y="16" width="450" height="127" rx="18" class="s-line s-fill2"/>
    <text x="34" y="39" class="s-lbl s-accent">INSIDE YOUR REGION</text>
    <g class="s-box"><rect x="34" y="57" width="164" height="65" rx="12"/>
      <rect x="278" y="57" width="164" height="65" rx="12"/>
      <rect x="526" y="57" width="178" height="65" rx="12"/></g>
    <g class="s-txt"><text x="116" y="84">Workspace</text><text x="360" y="84">Git mirror</text>
      <text x="615" y="84">Upstream</text></g>
    <g class="s-lbl" text-anchor="middle"><text x="116" y="105">your commits</text>
      <text x="360" y="105" class="s-amber">credential stays here</text>
      <text x="615" y="105">copy outside</text></g>
    <g class="s-arrow" fill="none"><path d="M202 84 H270" marker-end="url(#ah)"/>
      <path d="M446 84 H518" marker-end="url(#ah)"/></g>
    <path d="M615 132 V173 H116 V132" fill="none" stroke="var(--leaf)" stroke-width="2"/>
    <circle cx="116" cy="173" r="12" fill="var(--leaf)"/>
    <path d="M110 173 l4 4 8 -9" fill="none" stroke="var(--bg)" stroke-width="2"/>
    <text x="365" y="198" class="s-txt s-accent">Success comes back after upstream accepts</text>
    """)


def _progress_figure(combined=False):
    """The same illustrative gap counts, first by workstream, then as a sum."""
    rows = [("Accessibility", "leaf", (6, 3, 1)),
            ("Product copy", "violet", (6, 4, 2)),
            ("Dashboards", "amber", (6, 5, 3))]
    body = '<g class="s-lbl" text-anchor="middle">'
    for x, title in zip((265, 435, 605), ("Start", "Check again", "Check again")):
        body += f'<text x="{x}" y="24">{title}</text>'
    body += '</g>'
    if not combined:
        for row, (name, color, counts) in enumerate(rows):
            y = 65 + row * 59
            body += f'<text x="18" y="{y + 5}" class="s-txt" style="text-anchor:start">{name}</text>'
            body += f'<path d="M230 {y} H636" stroke="var(--{color})" opacity=".25" stroke-width="3"/>'
            for x, count in zip((265, 435, 605), counts):
                body += (f'<circle cx="{x}" cy="{y}" r="22" fill="var(--{color})" fill-opacity=".12" '
                         f'stroke="var(--{color})"/><text x="{x}" y="{y + 5}" class="s-txt">{count}</text>')
        body += '<text x="435" y="229" class="s-lbl" text-anchor="middle">gaps remaining in each part →</text>'
        alt = 'Illustrative remaining gaps: accessibility 6 to 3 to 1; copy 6 to 4 to 2; dashboards 6 to 5 to 3'
    else:
        for row, (name, color, _) in enumerate(rows):
            y = 70 + row * 30
            body += f'<circle cx="24" cy="{y}" r="5" fill="var(--{color})"/>'
            body += f'<text x="39" y="{y + 5}" class="s-txt" style="text-anchor:start">{name}</text>'
        for col, x in enumerate((265, 435, 605)):
            y = 191
            for _, color, counts in rows:
                height = counts[col] * 7
                y -= height
                body += f'<rect x="{x - 37}" y="{y}" width="74" height="{height - 2}" rx="3" fill="var(--{color})" opacity=".8"/>'
            total = sum(counts[col] for _, _, counts in rows)
            body += f'<text x="{x}" y="{y - 10}" class="s-txt">{total} gaps</text>'
        body += '<path d="M215 198 H663" class="s-axis"/>'
        body += '<text x="435" y="229" class="s-lbl" text-anchor="middle">same parts · same weights · fewer gaps →</text>'
        alt = 'The same three workstreams stack into totals of 18, 12, then 6 remaining gaps; none has reached zero'
    return _wrap("720 246", alt,
                 "Illustrative counts, not project measurements. Same requirements; each gap has equal weight.", body)


SMALL_STEPS = _progress_figure()
SHARED_PROGRESS = _progress_figure(combined=True)

EVIDENCE_RECORD = _wrap(
    "720 225", "A passing check and a counterexample both join the shared evidence record",
    "Keep distinct events, including corrections. Re-delivering the same event does not add it twice.",
    """
    <g class="s-box"><rect x="18" y="24" width="206" height="69" rx="13"/>
      <rect x="18" y="127" width="206" height="69" rx="13"/>
      <rect x="318" y="24" width="384" height="172" rx="16"/></g>
    <g class="s-txt"><text x="121" y="52" class="s-accent">Contributor A</text>
      <text x="121" y="76">Adds a passing check</text>
      <text x="121" y="155" class="s-amber">Contributor B</text>
      <text x="121" y="179">Adds a counterexample</text>
      <text x="510" y="53">One shared record</text></g>
    <g class="s-arrow" fill="none"><path d="M231 59 C270 59 270 87 305 87" marker-end="url(#ah)"/>
      <path d="M231 160 C270 160 270 135 305 135" marker-end="url(#ah)"/></g>
    <rect x="342" y="72" width="336" height="38" rx="8" fill="var(--leaf)" opacity=".1"/>
    <rect x="342" y="118" width="336" height="38" rx="8" fill="var(--amber)" opacity=".1"/>
    <g class="s-txt"><text x="510" y="96">Check retained</text>
      <text x="510" y="142">Counterexample retained</text></g>
    <text x="510" y="178" class="s-lbl" text-anchor="middle">review the claim with both in view</text>
    """)

GIT_RECORD = _wrap(
    "720 235", "Two Git branches add distinct ledger events, merge and fold into a tagged shared record",
    "A collaboration pattern: Git exchanges versioned files; the ledger fold applies the data’s merge rules.",
    """
    <path d="M48 103 C108 103 108 55 158 55 H290 C341 55 341 103 385 103 H468" fill="none" stroke="var(--leaf)" stroke-width="3"/>
    <path d="M48 103 C108 103 108 151 158 151 H290 C341 151 341 103 385 103" fill="none" stroke="var(--violet)" stroke-width="3"/>
    <g fill="var(--panel)" stroke-width="3"><circle cx="48" cy="103" r="8" stroke="var(--ink-dim)"/>
      <circle cx="175" cy="55" r="8" stroke="var(--leaf)"/><circle cx="175" cy="151" r="8" stroke="var(--violet)"/>
      <circle cx="385" cy="103" r="8" stroke="var(--leaf)"/></g>
    <g class="s-txt"><text x="206" y="29">Branch A · event A</text>
      <text x="206" y="184">Branch B · event B</text>
      <text x="392" y="81">Merge</text></g>
    <rect x="490" y="54" width="210" height="99" rx="15" class="s-line s-fill2"/>
    <g class="s-txt"><text x="595" y="83">Fold the events</text>
      <text x="595" y="108" class="s-accent">A + B</text></g>
    <text x="595" y="134" class="s-lbl" text-anchor="middle">same inputs, same view</text>
    <path d="M475 103 H486" class="s-arrow" marker-end="url(#ah)"/>
    <text x="385" y="220" class="s-lbl" text-anchor="middle">commit + release tag → a state you can revisit</text>
    """)

ARTIFACT_VECTORS = _wrap(
    "720 365", "Files, specifications, artifacts and documentation contribute identified evidence to a shared record",
    "A modeling pattern: event sets can merge by union; artifact contents retain their own validation rules.",
    """
    <g class="s-lbl"><text x="28" y="27">VERSIONED ARTIFACT</text>
      <text x="292" y="27">EVIDENCE TO PRESERVE</text></g>
    <g class="s-box"><rect x="18" y="45" width="226" height="59" rx="12"/>
      <rect x="18" y="119" width="226" height="59" rx="12"/>
      <rect x="18" y="193" width="226" height="59" rx="12"/>
      <rect x="18" y="267" width="226" height="59" rx="12"/></g>
    <g class="s-txt"><text x="131" y="80" class="s-accent">Files / code</text>
      <text x="131" y="154" style="fill:var(--violet)">Specifications</text>
      <text x="131" y="228" class="s-amber">Build artifacts</text>
      <text x="131" y="302" style="fill:var(--rose)">Documentation</text></g>
    <g class="s-txt" style="text-anchor:start"><text x="292" y="80">Test results + commit IDs</text>
      <text x="292" y="154">Requirement IDs + checks</text>
      <text x="292" y="228">Digests + build provenance</text>
      <text x="292" y="302">Claims + supporting sources</text></g>
    <g class="s-arrow" fill="none"><path d="M250 75 H280" marker-end="url(#ah)"/>
      <path d="M250 149 H280" marker-end="url(#ah)"/>
      <path d="M250 223 H280" marker-end="url(#ah)"/>
      <path d="M250 297 H280" marker-end="url(#ah)"/>
      <path d="M590 75 H618 V297 H590 M618 186 H661" marker-end="url(#ah)"/></g>
    <circle cx="683" cy="186" r="20" fill="var(--leaf)" fill-opacity=".12" stroke="var(--leaf)"/>
    <text x="683" y="191" class="s-txt">∪</text>
    <text x="360" y="353" class="s-lbl" text-anchor="middle">stable event IDs · set union · deterministic field rules</text>
    """)

ITERATION_HISTORY = _wrap(
    "720 325", "Three iterations retain previous evidence while adding tests and a later correction",
    "Illustration: A and B remain in the record when correction C changes how a claim is interpreted.",
    """
    <path d="M106 81 H615" class="s-arrow" fill="none" marker-end="url(#ah)"/>
    <path d="M120 81 C150 81 150 38 199 38 H243 C290 38 290 81 340 81
             M350 81 C390 81 390 38 437 38 H475 C520 38 520 81 570 81"
          fill="none" stroke="var(--violet)" stroke-width="2"/>
    <g fill="var(--panel)" stroke="var(--leaf)" stroke-width="3">
      <circle cx="110" cy="81" r="9"/><circle cx="355" cy="81" r="9"/><circle cx="610" cy="81" r="9"/></g>
    <g class="s-lbl" text-anchor="middle"><text x="224" y="25">change + check</text>
      <text x="456" y="25">challenge + check</text>
      <text x="110" y="116">commit 1</text><text x="355" y="116">commit 2</text>
      <text x="610" y="116">commit 3</text></g>
    <g class="s-box"><rect x="20" y="140" width="182" height="118" rx="14"/>
      <rect x="264" y="140" width="182" height="118" rx="14"/>
      <rect x="518" y="140" width="182" height="118" rx="14"/></g>
    <g class="s-txt"><text x="111" y="174">Evidence A</text>
      <text x="355" y="174">Evidence A + B</text>
      <text x="609" y="174">Evidence A + B + C</text></g>
    <g fill="var(--leaf)"><rect x="50" y="196" width="122" height="8" rx="4"/>
      <rect x="294" y="196" width="122" height="8" rx="4"/>
      <rect x="548" y="196" width="122" height="8" rx="4"/></g>
    <g fill="var(--violet)"><rect x="294" y="211" width="122" height="8" rx="4"/>
      <rect x="548" y="211" width="122" height="8" rx="4"/></g>
    <rect x="548" y="226" width="122" height="8" rx="4" fill="var(--amber)"/>
    <text x="360" y="297" class="s-txt">History accumulates. The current interpretation can change.</text>
    """)

FINITE_BOUNDARY = _wrap(
    "720 330", "A bounded staircase within fixed requirements climbs to a stable state below the maximum evidence rank",
    "Finite-height model: at most 6N strict increases for N fixed requirements with seven ranks each.",
    """
    <rect x="24" y="22" width="672" height="251" rx="18" fill="var(--leaf)" fill-opacity=".025"
          stroke="var(--leaf)" stroke-dasharray="6 6" opacity=".8"/>
    <text x="48" y="50" class="s-lbl s-accent">FIXED REQUIREMENTS · FIXED VALIDATION RULE</text>
    <path d="M56 81 H665" class="s-floor"/>
    <text x="664" y="73" class="s-lbl s-amber" text-anchor="end">highest modeled evidence</text>
    <path d="M64 233 H161 V206 H255 V171 H349 V142 H443 V124 H628"
          fill="none" stroke="var(--leaf)" stroke-width="4" stroke-linejoin="round"/>
    <g fill="var(--leaf)"><circle cx="161" cy="206" r="5"/><circle cx="255" cy="171" r="5"/>
      <circle cx="349" cy="142" r="5"/><circle cx="443" cy="124" r="5"/>
      <circle cx="530" cy="124" r="5"/><circle cx="628" cy="124" r="5"/></g>
    <text x="540" y="155" class="s-txt">stable under this rule</text>
    <text x="540" y="175" class="s-lbl" text-anchor="middle">a gap may remain</text>
    <text x="71" y="256" class="s-lbl">keep or raise each evidence rank →</text>
    <text x="360" y="310" class="s-txt">Scope change or falsification → explicitly reconsider the boundary</text>
    """)


def _refinement_tree():
    # Four small branch-and-merge histories become roots of one checked record.
    body = '''
    <ellipse cx="430" cy="180" rx="285" ry="150" fill="var(--leaf)" opacity=".035"/>
    <rect x="58" y="30" width="756" height="342" rx="24" fill="none"
          stroke="var(--leaf)" stroke-opacity=".35" stroke-dasharray="7 7"/>
    <text x="436" y="54" class="s-lbl s-accent" text-anchor="middle">ONE FIXED SCOPE · FINITE EVIDENCE RANKS</text>
    <path d="M28 372 V83" class="s-arrow" marker-end="url(#ah)"/>
    <text x="23" y="240" class="s-lbl" transform="rotate(-90 23 240)" text-anchor="middle">iterations over time</text>
    <path d="M436 285 V229 C436 184 336 188 304 139 M436 229 C436 184 537 188 569 139
             M436 229 V116 M304 139 C279 106 229 126 204 90
             M304 139 C326 104 354 114 366 82
             M569 139 C542 106 518 114 507 82 M569 139 C597 106 646 126 669 90"
          fill="none" stroke="var(--leaf)" stroke-width="5" stroke-linecap="round"/>
    <g fill="var(--panel)" stroke="var(--leaf)" stroke-width="2.5">
      <circle cx="436" cy="229" r="9"/><circle cx="304" cy="139" r="7"/>
      <circle cx="569" cy="139" r="7"/><circle cx="436" cy="116" r="7"/></g>
    <g fill="var(--leaf)"><ellipse cx="204" cy="90" rx="13" ry="6" transform="rotate(35 204 90)"/>
      <ellipse cx="366" cy="82" rx="13" ry="6" transform="rotate(-48 366 82)"/>
      <ellipse cx="507" cy="82" rx="13" ry="6" transform="rotate(48 507 82)"/>
      <ellipse cx="669" cy="90" rx="13" ry="6" transform="rotate(-35 669 90)"/></g>
    <text x="436" y="201" class="s-lbl" text-anchor="middle">checked joins</text>
    '''.strip()
    for x, color, name in [(139, "leaf", "Files"), (337, "leaf", "Specs"),
                           (535, "leaf", "Artifacts"), (733, "leaf", "Docs")]:
        body += f'''
        <g fill="none" stroke="var(--{color})" stroke-width="2.5" stroke-linecap="round">
          <path d="M{x} 423 V397 C{x} 379 {x-33} 384 {x-33} 357 V341
                   M{x} 397 C{x} 379 {x+33} 384 {x+33} 357 V341
                   M{x-33} 341 Q{x-33} 319 {x} 310 Q{x+33} 319 {x+33} 341
                   M{x} 310 C{x} 273 436 330 436 285"/>
        </g>
        <g fill="var(--panel)" stroke="var(--{color})" stroke-width="2">
          <circle cx="{x}" cy="410" r="5"/><circle cx="{x-33}" cy="351" r="5"/>
          <circle cx="{x+33}" cy="351" r="5"/><circle cx="{x}" cy="310" r="6"/></g>
        '''.strip()
    body += '<circle cx="436" cy="285" r="10" fill="var(--leaf)"/>'
    return _wrap("870 470",
                 "Four colored Git branch histories for files, specs, artifacts and docs join into a growing refinement tree; a dashed boundary marks fixed scope and finite evidence ranks",
                 "The tree is a methodology metaphor. Git histories with merges are directed acyclic graphs; the finite bound applies to evidence states.", body)


REFINEMENT_TREE = _refinement_tree()

METHODOLOGY_BRIDGE = _wrap(
    "900 260", "A fixed constraint is refined through small checked changes and retained evidence",
    "A prompt ends when its residual is close enough for the current specification; the next prompt inherits the record.",
    """
    <g class="s-box"><rect x="20" y="82" width="170" height="70" rx="12"/>
      <rect x="260" y="82" width="170" height="70" rx="12"/>
      <rect x="500" y="82" width="170" height="70" rx="12"/>
      <rect x="740" y="82" width="140" height="70" rx="12"/></g>
    <g class="s-txt"><text x="105" y="112">constraint</text><text x="105" y="134">fixed scope</text>
      <text x="345" y="112">small prompt</text><text x="345" y="134">propose a delta</text>
      <text x="585" y="112">check</text><text x="585" y="134">test + counterexample</text>
      <text x="810" y="112" class="s-accent">record</text><text x="810" y="134">keep evidence</text></g>
    <g class="s-arrow" fill="none"><path d="M194 117 H252" marker-end="url(#ah)"/>
      <path d="M434 117 H492" marker-end="url(#ah)"/><path d="M674 117 H732" marker-end="url(#ah)"/>
      <path d="M810 160 V205 H105 V160" marker-end="url(#ah)"/></g>
    <text x="450" y="238" class="s-lbl" text-anchor="middle">each accepted event adds refinement; each correction remains visible</text>
    """)


def _refinement_cloud():
    paths = []
    for i in range(34):
        dx = ((i * 37) % 120) - 60
        dy = ((i * 53) % 90) - 45
        scale = 0.82 + ((i * 11) % 20) / 100
        opacity = 0.07 + (i % 5) * 0.012
        paths.append(
            f'<g transform="translate({dx} {dy}) scale({scale})" opacity="{opacity:.3f}">'
            '<path d="M450 390 V300 C450 250 350 255 320 205 M450 300 C450 250 550 255 580 205 '
            'M450 300 V150 M320 205 C285 160 245 180 210 135 M320 205 C350 160 380 170 405 125 '
            'M580 205 C545 160 520 170 495 125 M580 205 C615 160 655 180 690 135" '
            'fill="none" stroke="var(--sky)" stroke-width="7" stroke-linecap="round"/>'
            '</g>')
    body = ''.join(paths) + '''
    <rect x="106" y="30" width="688" height="402" rx="24" fill="none" stroke="var(--sky)" stroke-opacity=".38" stroke-dasharray="7 7"/>
    <text x="450" y="59" class="s-lbl" style="fill:var(--sky)" text-anchor="middle">MANY SPECIFICATIONS · MANY SMALL REFINEMENTS</text>
    <circle cx="450" cy="300" r="13" fill="var(--sky)"/>
    '''
    return _wrap("900 490", "Dozens of translucent refinement trees for different specifications overlap into a bright convergence region", "Each translucent tree is one illustrative specification path. Similar paths overlap; the glow is a metaphor for accumulated effort.", body)


REFINEMENT_CLOUD = _refinement_cloud()

PROJECT_ORCHESTRATION = _wrap(
    "1440 778",
    "Intended my-project.com development topology: a forge agent debugs containerized Chromium against an httpd container. "
    "The forge clones and pushes through a Git mirror, which reads its GitHub credential from Vault and relays through the proxy. "
    "The host keychain holds the unseal key; the host orchestrator manages the runtime. Personal browser, Office and other apps "
    "sit outside the container workspace. macOS uses a Linux VM, Windows uses WSL2, and Linux containers share the host kernel.",
    "Intended container-browser workflow, not a full-isolation guarantee: current tooling also uses host Chrome, "
    "egress has gaps, and the unseal key has guest/cache copies. Enclave membership is not authentication.",
    """
    <g font-family="var(--sans)">
      <!-- Shared topology, with the three actual runtime boundaries below. -->
      <g font-size="16" fill="var(--ink-dim)">
        <path d="M28 36 H64" stroke="var(--ink-dim)" stroke-width="2"/>
        <text x="74" y="42">host</text>
        <path d="M158 36 H194" stroke="var(--amber)" stroke-width="3"/>
        <text x="204" y="42">runtime boundary</text>
        <path d="M388 36 H424" stroke="var(--leaf)" stroke-width="2"/>
        <text x="434" y="42">shared enclave</text>
        <rect x="607" y="25" width="29" height="23" rx="5" fill="var(--panel)" stroke="var(--violet)"/>
        <text x="648" y="42">container boundary</text>
      </g>
      <rect x="1050" y="8" width="366" height="66" rx="13" class="s-line s-fill1"/>
      <text x="1233" y="33" text-anchor="middle" fill="var(--ink)" font-size="19" font-weight="600">GitHub · example upstream</text>
      <text x="1233" y="58" text-anchor="middle" fill="var(--ink-dim)" font-size="17">github.com/you/my-project.com</text>

      <rect x="12" y="96" width="1416" height="548" rx="22" fill="none" stroke="var(--ink-dim)" stroke-opacity=".55" stroke-width="2"/>
      <text x="33" y="127" fill="var(--ink-dim)" font-size="17" font-weight="600">YOUR HOST COMPUTER</text>
      <rect x="32" y="164" width="258" height="144" rx="14" class="s-line s-fill1"/>
      <g fill="var(--ink)" font-size="18" font-weight="600">
        <text x="84" y="199">BROWSER</text><text x="84" y="238">OFFICE</text><text x="84" y="277">OTHER APPS</text>
      </g>
      <g stroke="var(--ink-dim)" stroke-width="1.5" fill="none">
        <rect x="50" y="181" width="22" height="18" rx="3"/><path d="M50 186 H72"/>
        <path d="M52 219 H66 L72 225 V242 H52 Z M66 219 V225 H72 M57 231 H66 M57 236 H66"/>
        <rect x="51" y="259" width="8" height="8" rx="2"/><rect x="64" y="259" width="8" height="8" rx="2"/>
        <rect x="51" y="272" width="8" height="8" rx="2"/><rect x="64" y="272" width="8" height="8" rx="2"/>
      </g>
      <text x="161" y="331" text-anchor="middle" fill="var(--ink-dim)" font-size="15">outside the container workspace</text>

      <rect x="32" y="353" width="258" height="87" rx="14" fill="var(--amber)" fill-opacity=".07" stroke="var(--amber)"/>
      <g stroke="var(--amber)" stroke-width="2" fill="none"><circle cx="59" cy="379" r="7"/>
        <path d="M66 379 H84 M77 379 V386 M83 379 V384"/></g>
      <text x="100" y="386" fill="var(--amber)" font-size="20" font-weight="600">HOST KEYCHAIN</text>
      <text x="161" y="416" text-anchor="middle" fill="var(--ink)" font-size="18">Vault unlock / unseal key</text>
      <rect x="32" y="487" width="258" height="94" rx="14" class="s-line s-fill1"/>
      <text x="161" y="520" text-anchor="middle" fill="var(--ink)" font-size="19" font-weight="600">Tillandsias orchestrator</text>
      <text x="161" y="550" text-anchor="middle" fill="var(--ink-dim)" font-size="17">launch · stop · publish · route</text>

      <rect x="320" y="142" width="1088" height="484" rx="18" fill="var(--amber)" fill-opacity=".025" stroke="var(--amber)" stroke-width="2.5"/>
      <text x="344" y="172" fill="var(--amber)" font-size="18" font-weight="600">LINUX RUNTIME</text>
      <text x="555" y="172" fill="var(--ink-dim)" font-size="17">VM on macOS / Windows · shared host kernel on Linux</text>
      <rect x="344" y="194" width="1042" height="410" rx="17" fill="var(--leaf)" fill-opacity=".03" stroke="var(--leaf)" stroke-width="2"/>
      <text x="368" y="224" fill="var(--leaf)" font-size="18" font-weight="600">ENCLAVE</text>
      <text x="496" y="224" fill="var(--ink-dim)" font-size="17">shared private network · peers can communicate</text>

      <!-- Each rounded purple box is a separate rootless container. -->
      <g fill="var(--panel)" stroke="var(--violet)" stroke-opacity=".65" stroke-width="1.5">
        <rect x="378" y="259" width="274" height="113" rx="13"/>
        <rect x="728" y="259" width="240" height="113" rx="13"/>
        <rect x="1060" y="259" width="270" height="113" rx="13"/>
        <rect x="378" y="462" width="244" height="94" rx="13"/>
        <rect x="726" y="462" width="242" height="94" rx="13"/>
        <rect x="1070" y="462" width="260" height="94" rx="13"/>
      </g>
      <g text-anchor="middle" fill="var(--ink)" font-size="22" font-weight="600">
        <text x="515" y="289">FORGE</text><text x="848" y="289">DEV CHROMIUM</text>
        <text x="1195" y="289">HTTPD</text><text x="500" y="497">GIT MIRROR</text>
        <text x="847" y="497" fill="var(--amber)">VAULT</text><text x="1200" y="497">EGRESS PROXY</text>
      </g>
      <g text-anchor="middle" fill="var(--ink-dim)" font-size="17">
        <text x="515" y="317">agent + tools</text><text x="515" y="346" fill="var(--leaf)">my-project.com checkout</text>
        <text x="848" y="317">Playwright / debugging</text><text x="848" y="346">separate browser profile</text>
        <text x="1195" y="317">my-project.com website</text><text x="1195" y="346">read-only published files</text>
        <text x="500" y="530">clone · push · relay</text>
        <text x="847" y="530" fill="var(--amber)">GitHub credential</text><text x="1200" y="530">controlled upstream route</text>
      </g>

      <!-- Development traffic and artifact publication. -->
      <g class="s-arrow" fill="none" stroke-width="2">
        <path d="M657 316 H722" marker-end="url(#ah)"/>
        <path d="M973 316 H1054" marker-end="url(#ah)"/>
        <path d="M420 377 V455" marker-start="url(#ah)" marker-end="url(#ah)"/>
        <path d="M515 373 V402 H1195 V378" marker-end="url(#ah)"/>
        <path d="M500 558 V582 H1200 V561" marker-end="url(#ah)"/>
        <path d="M1332 509 H1364 V85 H1233 V78" marker-end="url(#ah)"/>
      </g>
      <g fill="var(--ink-dim)" font-size="15" text-anchor="middle">
        <text x="690" y="302">debug</text><text x="1014" y="302">HTTP</text>
        <text x="859" y="393">publish site via orchestrator</text>
        <text x="445" y="445" text-anchor="start">clone / push</text>
        <text x="862" y="599">upstream relay → proxy → GitHub</text>
      </g>
      <!-- Secrets remain on their authorized paths. -->
      <path d="M290 397 H305 V432 H408 Q420 418 432 432 H847 V456" fill="none" stroke="var(--amber)" stroke-width="2"/>
      <path d="M841 449 L847 458 L853 449" fill="none" stroke="var(--amber)" stroke-width="2"/>
      <text x="639" y="425" fill="var(--amber)" font-size="15" text-anchor="middle">host-managed unseal</text>
      <path d="M722 508 H630 M637 502 L627 508 L637 514" fill="none" stroke="var(--amber)" stroke-width="2"/>
      <text x="674" y="491" text-anchor="middle" fill="var(--amber)" font-size="15">token</text>
      <text x="674" y="535" text-anchor="middle" fill="var(--amber)" font-size="14">not in forge</text>
      <!-- Host control is an explicit integration across the runtime boundary. -->
      <path d="M290 539 H331 V616 H1358" fill="none" stroke="var(--ink-dim)" stroke-width="1.5" stroke-dasharray="5 5"/>
      <text x="161" y="609" text-anchor="middle" fill="var(--ink-dim)" font-size="14">dashed line = lifecycle control</text>

      <g fill="var(--panel)" stroke="var(--line-2)">
        <rect x="12" y="660" width="452" height="104" rx="13"/>
        <rect x="486" y="660" width="452" height="104" rx="13"/>
        <rect x="960" y="660" width="468" height="104" rx="13"/>
      </g>
      <g fill="var(--ink)" font-size="20" font-weight="600">
        <text x="32" y="688">macOS</text><text x="506" y="688">WINDOWS</text><text x="980" y="688">LINUX</text>
      </g>
      <g font-size="18" fill="var(--amber)">
        <text x="32" y="719">Host → hypervisor → Linux VM</text>
        <text x="506" y="719">Host → hypervisor → WSL2</text>
      </g>
      <text x="980" y="719" font-size="18" fill="var(--leaf)">Host kernel → rootless containers</text>
      <g fill="var(--ink-dim)" font-size="16">
        <text x="32" y="746">Separate guest kernel → enclave</text>
        <text x="506" y="746">Linux guest kernel → enclave</text>
        <text x="980" y="746">Namespace boundary · no hypervisor</text>
      </g>
    </g>
    """)

FIGURES = {
    "project-orchestration": PROJECT_ORCHESTRATION,
    "methodology-bridge": METHODOLOGY_BRIDGE, "refinement-cloud": REFINEMENT_CLOUD,
    "artifact-vectors": ARTIFACT_VECTORS, "iteration-history": ITERATION_HISTORY,
    "finite-boundary": FINITE_BOUNDARY, "refinement-tree": REFINEMENT_TREE,
    "local-region": LOCAL_REGION, "push-journey": PUSH_JOURNEY,
    "small-steps": SMALL_STEPS, "shared-progress": SHARED_PROGRESS,
    "evidence-record": EVIDENCE_RECORD, "git-record": GIT_RECORD,
    "layers": LAYERS, "loop": LOOP, "staircase": STAIRCASE, "lln": LLN,
    "refinement-mesh": REFINEMENT_MESH,
    "aggregate-traces": AGGREGATE_TRACES,
    "lattice": LATTICE, "crdt": CRDT, "gate": GATE, "ephemeral": EPHEMERAL,
    "fixpoint": FIXPOINT, "galois": GALOIS, "hasse": HASSE,
    "nesting": NESTING,
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
