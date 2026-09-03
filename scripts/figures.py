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
    "Distance-to-target falls at every release and is never allowed to rise — but it settles on a "
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
    "600 260", "One slow sample versus many fast samples converging",
    "Left: one long run, one sample, one skew you cannot see. Right: many short runs whose "
    "average lands — provided each run's bias is bounded.",
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
    <text x="450" y="184" class="s-lbl s-accent" text-anchor="middle">the running average converges</text>
    <text x="450" y="200" class="s-lbl" text-anchor="middle">&#8212; only if each sample's bias is bounded</text>
    <text x="300" y="234" class="s-lbl" text-anchor="middle">Unbounded per-iteration skew: infinitely many iterations still miss.</text>
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
    "Two machines that never spoke, folded in either order, produce byte-identical state. "
    "That is the whole trick.",
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
    <text x="300" y="236" class="s-lbl" text-anchor="middle">no lock, no coordinator, no merge conflict, no lost write</text>
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
    "lattice": LATTICE, "crdt": CRDT, "gate": GATE, "ephemeral": EPHEMERAL,
    "fixpoint": FIXPOINT, "galois": GALOIS, "hasse": HASSE,
}

DEFS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6"
        orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="currentColor"/></marker>
</defs></svg>"""
