import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "benchmark" / "documents"
CASES = ROOT / "benchmark" / "cases"

entries = [
    (
        "Aurora",
        [
            "Aurora uses reflective panels to redirect winter light.",
            "Aurora records observations in a public ledger.",
            "Aurora gardens require less water during summer.",
            "Aurora stores tools in numbered cabinets.",
            "Aurora meetings begin on the first Monday of each month.",
        ],
    ),
    (
        "Birch",
        [
            "Birch paper is made from processed wood pulp.",
            "Birch labels use blue ink for archive copies.",
            "Birch workshops open at nine in the morning.",
            "Birch routes are marked with square signs.",
            "Birch seeds are kept in dry envelopes.",
        ],
    ),
    (
        "Cedar",
        [
            "Cedar benches are treated with natural oil.",
            "Cedar maps show walking paths in green.",
            "Cedar volunteers sort materials by weight.",
            "Cedar lectures take place in the north hall.",
            "Cedar records are backed up every Friday.",
        ],
    ),
    (
        "Dahlia",
        [
            "Dahlia flowers grow best in well-drained soil.",
            "Dahlia guides include a monthly planting table.",
            "Dahlia tools are cleaned after every use.",
            "Dahlia plots receive morning sunlight.",
            "Dahlia seeds remain viable for two years.",
        ],
    ),
    (
        "Ember",
        [
            "Ember stoves use dry hardwood for fuel.",
            "Ember safety cards list three warning signs.",
            "Ember cabins have a metal water bucket.",
            "Ember inspections are logged by hand.",
            "Ember trails close during severe wind.",
        ],
    ),
    (
        "Fjord",
        [
            "Fjord boats carry emergency blankets.",
            "Fjord charts use a scale of one to ten thousand.",
            "Fjord crossings are shortest in September.",
            "Fjord stations keep radios on channel four.",
            "Fjord permits are issued at the visitor center.",
        ],
    ),
    (
        "Grove",
        [
            "Grove soil retains moisture under leaf cover.",
            "Grove paths are inspected after heavy rain.",
            "Grove surveys use a six-point checklist.",
            "Grove signs are placed at every junction.",
            "Grove seedlings are protected by woven guards.",
        ],
    ),
    (
        "Harbor",
        [
            "Harbor lanterns are powered by rechargeable cells.",
            "Harbor notices are posted beside the main gate.",
            "Harbor crews inspect ropes before departure.",
            "Harbor water samples are stored in glass bottles.",
            "Harbor gates close during high waves.",
        ],
    ),
    (
        "Iris",
        [
            "Iris leaves are narrow and sword-shaped.",
            "Iris beds need regular weeding in spring.",
            "Iris labels include the year of planting.",
            "Iris bulbs are lifted before deep frost.",
            "Iris displays are arranged by color.",
        ],
    ),
    (
        "Juniper",
        [
            "Juniper berries are collected in small baskets.",
            "Juniper fences reduce wind across the field.",
            "Juniper notes are written on recycled cards.",
            "Juniper paths have wooden handrails.",
            "Juniper saplings are watered twice a week.",
        ],
    ),
    (
        "Kite",
        [
            "Kite strings are stored on labeled reels.",
            "Kite flights require a clear field.",
            "Kite clubs meet beside the old mill.",
            "Kite frames are made from light bamboo.",
            "Kite repairs are recorded in a logbook.",
        ],
    ),
    (
        "Lichen",
        [
            "Lichen grows slowly on undisturbed stone.",
            "Lichen surveys record color and texture.",
            "Lichen samples are not removed from protected rocks.",
            "Lichen walks follow a marked loop.",
            "Lichen photographs include a scale card.",
        ],
    ),
    (
        "Maple",
        [
            "Maple syrup is collected during the thaw.",
            "Maple taps are cleaned before storage.",
            "Maple barrels are kept in a cool room.",
            "Maple signs use a red leaf symbol.",
            "Maple demonstrations last about forty minutes.",
        ],
    ),
    (
        "Nettle",
        [
            "Nettle fibers can be spun into coarse thread.",
            "Nettle gloves are kept near the workbench.",
            "Nettle lessons begin with a safety briefing.",
            "Nettle bundles dry under a covered roof.",
            "Nettle recipes identify leaves by shape.",
        ],
    ),
    (
        "Orchid",
        [
            "Orchid roots need air around their growing medium.",
            "Orchid notes compare flowers by structure.",
            "Orchid benches are shaded at midday.",
            "Orchid pots have drainage holes.",
            "Orchid collections are checked for pests weekly.",
        ],
    ),
    (
        "Pine",
        [
            "Pine cones open in dry conditions.",
            "Pine shelters use locally milled boards.",
            "Pine trails are cleared in early June.",
            "Pine signs include distance markers.",
            "Pine seedlings tolerate sandy ground.",
        ],
    ),
    (
        "Quartz",
        [
            "Quartz fragments are sorted by surface color.",
            "Quartz displays include a magnifying lens.",
            "Quartz samples are labeled with collection dates.",
            "Quartz tables are covered after closing.",
            "Quartz lessons distinguish crystal shape from color.",
        ],
    ),
    (
        "Reed",
        [
            "Reed beds provide cover for small birds.",
            "Reed baskets are woven while the stalks are fresh.",
            "Reed cutters wear waterproof boots.",
            "Reed channels are measured each autumn.",
            "Reed workshops reuse clean offcuts.",
        ],
    ),
    (
        "Spruce",
        [
            "Spruce needles are arranged around each twig.",
            "Spruce cabins use thick wool curtains.",
            "Spruce records include tree height measurements.",
            "Spruce paths are quiet in winter.",
            "Spruce seedlings grow in shaded trays.",
        ],
    ),
    (
        "Willow",
        [
            "Willow branches bend easily when soaked.",
            "Willow fences are renewed each spring.",
            "Willow baskets are dried on open shelves.",
            "Willow lessons demonstrate three weaving patterns.",
            "Willow cuttings root in damp soil.",
        ],
    ),
]

for index, (topic, facts) in enumerate(entries, start=1):
    name = f"document-{index:02d}.md"
    (DOCS / name).write_text(
        f"# {topic}\n\n" + "\n\n".join(facts) + "\n",
        encoding="utf-8",
    )
    source = name
    cases = [
        ("supported", facts, ["SUPPORTED"] * 5),
        (
            "partial",
            [fact.rstrip(".") + " and it is guaranteed forever." for fact in facts],
            ["PARTIALLY_SUPPORTED"] * 5,
        ),
        ("unsupported", [f"{topic} is made of glass." for _ in facts], ["UNSUPPORTED"] * 5),
        (
            "insufficient",
            ["The moon is made of cheese." for _ in facts],
            ["INSUFFICIENT_EVIDENCE"] * 5,
        ),
        (
            "mixed",
            [
                facts[0],
                facts[1].rstrip(".") + " and it is guaranteed forever.",
                f"{topic} is made of glass.",
                "The moon is made of cheese.",
            ],
            ["SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED", "INSUFFICIENT_EVIDENCE"],
        ),
    ]
    for kind, answer_lines, statuses in cases:
        case_id = f"{index:02d}-{kind}"
        (CASES / f"{case_id}.json").write_text(
            json.dumps(
                {
                    "id": case_id,
                    "question": f"What does the original {topic} note say?",
                    "answer": "\n".join(f"- {line}" for line in answer_lines),
                    "sources": [source],
                    "expected_statuses": statuses,
                    "ground_truth": [
                        {"claim": line, "label": status, "evidence": [{"document": source}]}
                        for line, status in zip(answer_lines, statuses, strict=False)
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

(ROOT / "benchmark" / "README.md").write_text(
    """# EvidenceBench benchmark dataset\n\nThis is a small, original, synthetic dataset generated for EvidenceBench 0.1.0. It contains 20 Markdown documents and 100 labeled question/answer cases (480 labeled claims). The documents and claims were authored for this repository; they are not copied from a third-party work. They are released under the repository MIT license.\n\nEach case restricts retrieval to its listed source document and contains `ground_truth` labels for the four supported statuses. Run `evidencebench validate benchmark` before using it and `evidencebench benchmark benchmark` to measure the current implementation. Benchmark values are generated at runtime and are intentionally not hard-coded here.\n""",
    encoding="utf-8",
)
