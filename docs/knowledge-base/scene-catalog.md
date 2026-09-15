# Scene observation catalog

[scene-catalog.json](scene-catalog.json) contains 176 terse, individually identified
observations from 19 reviewed pages of the Johnny Castaway fan guide, retrieved
2026-09-14. Every record starts as `secondary_unverified`. The source site is
a fan reference, not an original program specification or evidence that this port
implements an event correctly.

Records include reported outcomes and context as well as actions. Some pages
describe the same event. Counts below are catalog records, not distinct animations,
and do not establish complete coverage of the original screensaver. The numbered
story, seasonal windows and reported glitches are observations to cross-check.

| Source category | Stable source ID | Records |
| --- | --- | ---: |
| [Source navigation](https://johnnycastawayscreensaver.com/list.html) | `fan:list` | 0 |
| [Daily activities](https://johnnycastawayscreensaver.com/common.html) | `fan:common` | 34 |
| [Catches and fishing](https://johnnycastawayscreensaver.com/fishing.html) | `fan:fishing` | 17 |
| [Water activities](https://johnnycastawayscreensaver.com/swimming.html) | `fan:swimming` | 16 |
| [Book activity](https://johnnycastawayscreensaver.com/reading.html) | `fan:reading` | 2 |
| [Bird interactions](https://johnnycastawayscreensaver.com/seagull.html) | `fan:seagull` | 7 |
| [Mermaid encounters](https://johnnycastawayscreensaver.com/mermaid.html) | `fan:mermaid` | 15 |
| [Pirate encounters](https://johnnycastawayscreensaver.com/pirates.html) | `fan:pirates` | 9 |
| [Numbered story sequence](https://johnnycastawayscreensaver.com/story.html) | `fan:story` | 15 |
| [Departure and mainland](https://johnnycastawayscreensaver.com/leaving.html) | `fan:leaving` | 11 |
| [Passing visitors](https://johnnycastawayscreensaver.com/visitors.html) | `fan:visitors` | 16 |
| [Unusual events](https://johnnycastawayscreensaver.com/unusual.html) | `fan:unusual` | 11 |
| [Calendar observations](https://johnnycastawayscreensaver.com/annivers.html) | `fan:annivers` | 5 |
| [Reported legacy faults](https://johnnycastawayscreensaver.com/bugs.html) | `fan:bugs` | 18 |
| [Source update digest](https://johnnycastawayscreensaver.com/johnew.html) | `fan:johnew` | 0 |
| [Dive detail page](https://johnnycastawayscreensaver.com/dive.html) | `fan:dive` | 0 |
| [Octopus detail page](https://johnnycastawayscreensaver.com/octoctch.html) | `fan:octoctch` | 0 |
| [Aircraft detail page](https://johnnycastawayscreensaver.com/crash-b.html) | `fan:crash-b` | 0 |
| [Water-gag detail page](https://johnnycastawayscreensaver.com/stillthere.html) | `fan:stillthere` | 0 |

Each JSON record carries a semantic ID and a source ID. The source table supplies
its direct page citation, retrieval date and hashes of the initial HTML response
and rendered article text. IDs should survive wording corrections; retire an ID
explicitly if later evidence splits or disproves its observation.

Use the source hashes to identify this research snapshot. Harvested prose and
media remain outside the tracked knowledge base. The JSON is the only fact
catalog; this page provides navigation instead of repeating its descriptions.
Short detail pages without a specific additional outcome are recorded with zero
new entries. Setup guidance, technical claims and external-reference provenance
belong in the source guide and [original extractor reference](original-extractor-reference.md).

Original-data and port mappings must be added as separate evidence. A filename
resemblance alone does not confirm a scene, its timing, its alternatives or its
visual result. Historical fault reports are not assertions of current port bugs.
