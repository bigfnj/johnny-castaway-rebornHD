"""Read-only source evidence collection; outputs stay in ignored build/."""
from pathlib import Path
import ast
import hashlib
import itertools
import json
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = "3af0242a74f234aab231d9203b48f78ca8e5c1b4"
MERGED = "9ea8293f8efbd45a25717b4f8dd3bc5139586259"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def without_comments(text):
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


head = git("rev-parse", "HEAD").decode().strip()
assert head == MERGED
paths = {
    "src/engine/jc_reborn.c": "Full CLI state machine, config modes, dispatch and shutdown",
    "src/engine/config.c": "Full config read/write and cached-path ownership",
    "src/engine/resource.c": "Full map, resource parsers, name borrowing and lookup",
    "src/engine/resource.h": "Resource ownership fields and public API",
    "src/engine/uncompress.c": "Full LZW/RLE boundary and allocation handling",
    "src/engine/utils.c": "Full file/byte helpers, string ownership, error and calendar paths",
    "src/engine/story.c": "Full scene selection, date updates, transition and island lifecycle",
    "src/engine/ads.c": "Full ADS parser, dispatch, scheduling, scene and island ownership",
    "src/engine/ttm.c": "Full TTM tag scan, VM, string decoding and slot lifecycle",
    "src/engine/ttm.h": "Public VM API",
    "src/engine/walk.c": "Full path, heading, arrival and palm ordering",
    "src/engine/calcpath.c": "Full recursive path enumeration and fallback",
    "src/engine/calcpath.h": "Public path API",
    "src/engine/dump.c": "Full BMP/SCR/ADS/TTM dump and file-close handling",
    "src/engine/bench.c": "Full benchmark slot and sprite calls",
    "src/engine/events.c": "Full event, bounded-run, delay and exit paths",
    "src/engine/art_style.c": "Full manifest validation, source fallback and PNG ownership",
    "src/engine/graphics.c": "Selected ownership/call paths: lines1-355,818-end; release, init, display, sprite load and fade; drawing middle not fully reread",
    "src/engine/island.c": "Selected ownership and live-wave setup: lines1-230; remaining animation handled by parallel platform audit",
    "src/engine/sound.c": "Full common audio lifecycle and buffer/callback ownership",
    "src/engine/mytypes.h": "Integer aliases",
    "src/data/story_data.h": "Full63-entry scene table and flags; static domain census",
    "src/data/calcpath_data.h": "Full fixed6-node directed transition table; independent simple-path census",
    "src/data/walk_data.h": "Initial travel data plus complete machine-read table identity; not all movement rows visually reread",
}
coverage = []
for path, scope in paths.items():
    raw = (ROOT / path).read_bytes()
    prior = git("show", f"{BASE}:{path}")
    text = raw.decode("utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").encode()
    coverage.append({"path": path, "sha256": sha(raw), "lf_utf8_sha256": sha(normalized),
                     "base_git_sha256": sha(prior), "same_as_base_after_lf_normalization": normalized == prior.replace(b"\r\n", b"\n").replace(b"\r", b"\n"),
                     "lines": len(text.splitlines()), "review_scope": scope})

inventory_path = "docs/knowledge-base/port-inventory.json"
inventory = json.loads((ROOT / inventory_path).read_text(encoding="utf-8"))
with zipfile.ZipFile(ROOT / "assets/scrantic_data.zip") as archive:
    member_facts = {name: sha(archive.read(name)) for name in ["data/RESOURCE.MAP", "data/RESOURCE.001"]}
    archive_info = {"sha256": sha((ROOT / "assets/scrantic_data.zip").read_bytes()), "members": len(archive.namelist()),
                    "resource_payload_sha256": member_facts,
                    "resource_payloads_match_historical_static_inventory": member_facts["data/RESOURCE.MAP"] == inventory["inputs"]["port_map_sha256"] and member_facts["data/RESOURCE.001"] == inventory["inputs"]["port_volume_sha256"]}

matrix_text = without_comments((ROOT / "src/data/calcpath_data.h").read_text())
literal = matrix_text.split("walkMatrix", 1)[1].split("=", 1)[1].split(";", 1)[0]
matrix = ast.literal_eval(literal.replace("{", "[").replace("}", "]").strip())
path_counts = []
for start in range(6):
    for end in range(6):
        allowed = []
        for length in range(1, 7):
            for path in itertools.permutations(range(6), length):
                if path[0] != start or path[-1] != end:
                    continue
                if all(matrix[6 if i == 0 else path[i - 1]][path[i]][path[i + 1]] for i in range(length - 1)):
                    allowed.append(path)
        path_counts.append({"from": start, "to": end, "count": len(allowed),
                            "maximum_nodes": max(map(len, allowed), default=0)})

story_text = without_comments((ROOT / "src/data/story_data.h").read_text())
defs = {key: int(value, 0) for key, value in re.findall(r"#define\s+(\w+)\s+(0x[0-9A-Fa-f]+|\d+)", story_text)}
scenes = []
for name, values in re.findall(r'\{\s*"([^"\n]+)"\s*,([^}]+)\}', story_text):
    row = []
    for value in values.split(","):
        result = 0
        for term in value.strip().split("|"):
            term = term.strip()
            result |= defs[term] if term in defs else int(term, 0)
        row.append(result)
    scenes.append({"resource": name, "tag": row[0], "start_spot": row[1], "start_heading": row[2],
                   "end_spot": row[3], "end_heading": row[4], "day": row[5], "flags": row[6]})
eligibility = []
for day in range(1, 12):
    for wanted in [0, defs["VARPOS_OK"], defs["LOWTIDE_OK"], defs["VARPOS_OK"] | defs["LOWTIDE_OK"]]:
        for unwanted in [defs["FINAL"], defs["FINAL"] | defs["FIRST"]]:
            eligible = [s for s in scenes if (s["day"] in (0, day)) and s["flags"] & wanted == wanted and not s["flags"] & unwanted]
            eligibility.append({"day": day, "wanted": wanted, "unwanted": unwanted, "count": len(eligible)})
facts = {
    "schema_version": 1, "head": head, "baseline": BASE,
    "source_diff_names": git("diff", "--name-only", BASE, head, "--", "src").decode().splitlines(),
    "archive": archive_info,
    "static_inventory": {"path": inventory_path, "sha256": sha((ROOT / inventory_path).read_bytes()),
                         "scope": "Historical static facts reused only after checking current MAP/001 payload identity; historical executable proofs not rerun.",
                         "summary": inventory["summary"],
                         "command_support_overview": [{k: v for k, v in row.items() if k not in ("sites", "occurrences", "resources")} for row in inventory["command_support"]]},
    "path_domain_census": {"method": "Independent exhaustive simple-node permutations filtered by current transition table; static analysis, not native engine execution.",
                           "pairs": path_counts, "max_paths": max(x["count"] for x in path_counts),
                           "max_nodes": max(x["maximum_nodes"] for x in path_counts),
                           "unconnected_pairs": [x for x in path_counts if not x["count"]]},
    "story_domain_census": {"entries": len(scenes), "invalid_endpoint_rows": [s for s in scenes if not (0 <= s["start_spot"] < 6 and 0 <= s["end_spot"] < 6 and 0 <= s["start_heading"] < 8 and 0 <= s["end_heading"] < 8)],
                            "final_candidates_by_day": {str(day): sum(s["day"] in (0, day) and bool(s["flags"] & defs["FINAL"]) for s in scenes) for day in range(1, 12)},
                            "nonfinal_min_candidates": min(x["count"] for x in eligibility), "nonfinal_eligibility_cases": len(eligibility)},
    "limits": ["No full native run, sanitizer, leak detector or performance benchmark was executed for this read-only audit.",
               "No unsupported-opcode effect or random-story parity was inferred from static command counts.",
               "File hashes identify inspected bytes; they do not prove every path is correct."]}
write("coverage.json", {"schema_version": 1, "head": head, "files": coverage})
write("facts.json", facts)
known = [
    {"id": "standing-wait-timer", "source": ["src/engine/ads.c:1110", "src/engine/ads.c:1114", "src/engine/story.c:285", "src/engine/story.c:304"],
     "finding": "Initial walk timer remains 6 even when the first walkAnimate returns 80. Both ordinary-story transition call sites remain present.",
     "reachability": "Valid public call and statically reachable story transitions; previously captured timing witnesses were not rerun.",
     "disposition": "Already in BACKLOG; original-runtime comparison before changing timing."},
    {"id": "config-integer-boundaries", "source": ["src/engine/config.c:136", "src/engine/config.c:139", "src/engine/story.c:102", "src/engine/jc_reborn.c:423"],
     "finding": "Config still uses atoi; day increments before range normalization; seed parsing still lacks errno/range enforcement.",
     "reachability": "Malformed saved values or out-of-range CLI input, not normal valid story state.",
     "disposition": "Already in BACKLOG; no new fault injection this audit."},
    {"id": "ttm-malformed-metadata", "source": ["src/engine/ttm.c:59", "src/engine/ttm.c:169", "src/engine/ttm.c:246", "src/engine/dump.c:381"],
     "finding": "Incomplete tag-table sentinel offsets remain unset; zero-offset matching lookup can fail to advance. The 255-character string limit still consumes the next byte as though it were a terminator.",
     "reachability": "Malformed metadata/overlong script strings. Existing exact-resource inventory remains applicable because MAP/001 bytes are unchanged.",
     "disposition": "Both already in BACKLOG; prior compiled witnesses are historical, not claimed as rerun."},
    {"id": "lzw-malformed-codes", "source": ["src/engine/uncompress.c:94", "src/engine/uncompress.c:151"],
     "finding": "Existing first-code and undefined-code permissiveness remains. Full-output-buffer early return is also still present and must not be removed without distinguishing valid packed resources.",
     "reachability": "Known malformed compressed-stream cases; no new bundled-resource decoder failure found.",
     "disposition": "Already in BACKLOG and LZW assessment; retain valid controls when addressing it."},
    {"id": "dump-close-errors", "source": ["src/engine/dump.c:169", "src/engine/dump.c:235", "src/engine/dump.c:321", "src/engine/dump.c:570"],
     "finding": "All four dump writers still discard fclose results. Frame capture has a distinct checked close path at graphics.c:241.",
     "reachability": "Real output-device/write failure in CLI dump; earlier executed BMP /dev/full proof remains historical.",
     "disposition": "Already in BACKLOG; do not imply all four writers were fault-injected."},
    {"id": "unfinished-scene-commands", "source": ["src/engine/ttm.c:290", "src/engine/ttm.c:382", "src/engine/ads.c:583", "src/engine/ads.c:701", "src/engine/ads.c:706"],
     "finding": "DRAW_BACKGROUND and SAVE_IMAGE1 incomplete behavior and other documented ignored command semantics persist. These are live VM cases rather than removable dead code.",
     "reachability": "Static inventory confirms shipped commands. Current MAP/001 identity was freshly checked; visible original parity was not re-established.",
     "disposition": "Already in BACKLOG/knowledge base; compare original scene effects before implementation."},
    {"id": "resource-lifetime", "source": ["src/engine/resource.c:40", "src/engine/resource.c:378", "src/engine/resource.c:495", "src/engine/jc_reborn.c:688", "src/engine/ttm.c:188", "src/engine/ads.c:505", "src/engine/ads.c:959", "src/engine/ads.c:1074"],
     "finding": "Resources retain process-lifetime ownership, names borrow map records and TTM data borrows decompressed resources. Normal ADS teardown frees layers, owned tags and loaded BMPs; the two production island-init callers retain matching release paths.",
     "reachability": "One resource load per process. A future reload/restart API would require explicit resource teardown; no current cumulative-leak claim.",
     "disposition": "Process-owned data limitation already in BACKLOG. Existing ownership repairs remain in place."},
    {"id": "common-audio-initialization", "source": ["src/engine/sound.c:79", "src/engine/sound.c:158", "src/engine/sound.c:165", "src/engine/sound.c:170"],
     "finding": "currentRemaining is initialized after opening audio, outside the callback lock; initial zero-length copy may receive NULL. Close-before-free and per-buffer teardown remain intact.",
     "reachability": "Real audio startup concurrency boundary; no race detector or physical-audio run performed here.",
     "disposition": "Already in BACKLOG; not a newly observed race or leak."},
]
audit = {
    "schema_version": 1, "status": "completed_read_only_review", "head": head, "baseline": BASE,
    "scope": "Fresh core engine/resource/scene/config/CLI and ownership review on merged main; platform/backend and authoring audits are separate.",
    "result": {"introduced_engine_regressions_found": 0, "new_actionable_core_findings": 0, "known_backlog_groups_reconfirmed": len(known),
               "covered_files": len(coverage), "all_src_git_diff_empty": not facts["source_diff_names"], "new_dead_code_removal_proposed": False,
               "new_performance_saving_claimed": False},
    "evidence": [{"path": (OUT / name).relative_to(ROOT).as_posix(), "sha256": sha((OUT / name).read_bytes())}
                 for name in ["coverage.json", "facts.json"]],
    "collector": {"path": Path(__file__).relative_to(ROOT).as_posix(), "sha256": sha(Path(__file__).read_bytes()),
                  "command": "python -B build/connecting-poses/post-merge-core/collect_audit.py"},
    "known_findings": known,
    "fresh_observations": [
        "Current production archive has 2594 members; MAP/001 match the historical static-inventory payload identities. Updated art did not replace original scripts or walk/story tables.",
        "All 36 valid endpoint pairs have paths in the current directed transition table, with at most 5 paths and 6 nodes. The 50-row path-capacity concern is not reachable with this fixed table; no general malformed-API safety proof is implied.",
        "All 63 story entries use spots 0..5 and headings 0..7; every day 1..11 has 19 or 20 final choices. All 88 checked nonfinal day/flag combinations have at least 28 choices. The empty-final tight-loop branch is not reached by the current table.",
        "Current style PNG path remains original geometry times 2, with Cartoon dimension/format refusal and compatible HD/original fallback. New palette/pose assets do not require engine dispatch changes.",
        "The remaining ignored or approximate script commands should not be deleted as dead code. No new orphaned public engine function was established in the inspected call paths."
    ],
    "optimization": {"recommendation": "Keep existing performance work in BACKLOG; measure cold interleaved variants before changing sprite mirroring, decoded resource retention or layer composition.",
                     "benchmarks_run": 0},
    "tests_executed": {"native": 0, "full_gates": 0, "sanitizers": 0, "static_collector_executed": True,
                       "note": "Parent owns the completed merged Windows/platform gates. This report does not duplicate or claim those results."},
    "audit_limits": facts["limits"] + ["Graphics and island coverage is explicitly partial in coverage.json; backend ownership is a parallel audit.",
                                       "Malformed input, asynchronous audio, original story outcomes and all random routes were not exhaustively executed."],
    "suggested_backlog_additions": [],
    "tracked_changes_by_this_audit": []
}
write("audit.json", audit)
markdown = f"""Fresh core audit completed on `{head}`. No introduced engine regression or new actionable core item was found in this review. Existing backlog issues remain open. `src/` is unchanged from `{BASE}`.

| Area | Result | Follow-up |
| --- | --- | --- |
| Current script identity | The 2594-member production archive retains exact original MAP/001 payloads. Static inventory facts still apply. | Keep original-runtime parity distinct from art approval. |
| Story and path domain | All 63 endpoint/heading rows are in range; all 36 path pairs connect, maximum 5 paths. All 11 days have final choices; 88 nonfinal flag/day cases remain nonempty. | No fixed-table path-capacity or empty-final-loop failure found. |
| Ownership | ADS tags, scene layers, BMP slots and island owners retain their current matched teardown. Global resources remain process-owned. | Existing reload/lifetime backlog applies; this is not a leak-free proof. |
| Config, CLI and malformed resources | Known seed overflow, config day overflow, TTM tag/string and LZW gaps remain. | Retain existing BACKLOG items. |
| Scene commands and dump output | Known incomplete VM semantics and ignored dump-close failures remain. | Original scene comparison and focused write-failure repairs remain separate work. |
| Common audio | Known startup locking and initial zero-length-copy concerns remain. | Existing backlog; no concurrency instrumentation was run. |
| Dead code and optimization | No new removal candidate or measured performance saving was established. | Profile before pursuing existing optimization ideas. |

Coverage is recorded for 24 source/data files in `coverage.json`, with exact local and LF-normalized hashes plus baseline Git identities. Full files were reread except the explicitly bounded graphics/island sections and the walk-data rows, whose scopes are recorded individually. `facts.json` preserves the independent static-table census and current resource fingerprints. `audit.json` contains source lines and backlog classifications.

No native launch, full gate, sanitizer, leak detector, fault injection or performance benchmark was run by this audit. Parent owns platform gates and the other audit scopes. No tracked files were changed. There are no suggested new BACKLOG entries from this bounded review.
"""
(OUT / "audit.md").write_text(markdown, encoding="utf-8", newline="\n")
print(json.dumps({"coverage_files": len(coverage), "source_diff_names": facts["source_diff_names"], "archive": archive_info,
                  "path_max": facts["path_domain_census"]["max_paths"], "story": facts["story_domain_census"],
                  "command_support_keys": list(inventory["command_support"][0]), "output_files": ["coverage.json", "facts.json"]}, indent=2))
