# Remaining Johnny artwork

Complete supplied-original BMP/SCR inventory, visually classified per runtime slot; no new art approval.

Reviewed 2,402 source slots across 127 resources: 2,401 app slots and 1 original-only reference.

**1,002 confirmed Johnny slots remain**, across 76 resources. 28 character slots already have accepted Cartoon art; 84 additional app slots need visual confirmation.

The remaining slots contain 968 distinct native RGBA/canvas images. Duplicates remain separate runtime targets; no approval is inherited.

| Drawing type | Outstanding slots |
|---|---:|
| johnny_composite | 382 |
| johnny_full | 431 |
| johnny_partial | 189 |

These are drawings and compositing parts, not distinct animation sequences. Extraction is complete; Cartoon generation and scene acceptance are not.

Some Johnny drawings contain props or other characters in the same bitmap. Those scene groups need coordinated character and prop work. The title screen and thought bubbles also contain Johnny.

## Review and reproduce

Run `python -B art/cartoon/character-inventory-v1/build_inventory.py --check --review-directory build/character-inventory/review` from the repository root. Open the resulting `index.html`, or serve that directory on localhost.

The browser starts with confirmed outstanding drawings. It can also show accepted Cartoon comparisons, ambiguous pieces, excluded props and the original-only reference. Its JSON and ZIP downloads preserve exact resource/frame identities.

Originals use a diagnostic palette. Their geometry is authoritative for this extraction; the bright colors are not a proposed new style. Review the full native PNG when a contact-sheet thumbnail is too small.

See [character playbook](../../../docs/cartoon-character-playbook.md), [source provenance](source/README.md), [static scene mapping](scene-map/README.md) and [classification records](classification/).

## Resource worklist

| Resource | Remaining Johnny | Needs review | Accepted Johnny | Static story associations |
|---|---:|---:|---:|---|
| COCOHEAD.BMP | 10 | 0 | 0 | COCONUT 360, COCONUT CHASE, COCONUT DROP L & R |
| DRUNKJON.BMP | 19 | 0 | 0 | WOULDBEAS |
| FIRE.BMP | 25 | 0 | 0 | EAT, JOHN BUILDS FIRE |
| FIRE3.BMP | 3 | 0 | 0 | EAT, JOHN BUILDS FIRE |
| FIRE4.BMP | 24 | 0 | 0 | EAT, JOHN BUILDS FIRE |
| FISHMAN.BMP | 2 | 0 | 0 | EIGHT ARM MENACE |
| GJANGRY.BMP | 10 | 0 | 0 |  |
| GJBIPLAN.BMP | 0 | 14 | 0 | LILIPUT 1, LILIPUT 2, LILIPUT 3 NIGHT, MJSAND, MUNDANE SLEEP |
| GJCASTLE.BMP | 8 | 0 | 0 | LILIPUT 2, MJSAND |
| GJCATCH1.BMP | 13 | 0 | 0 | CATCH 1, FISH AT C FOR JUNK, FISH AT KEEPERS |
| GJCATCH2.BMP | 17 | 0 | 0 | EIGHT ARM MENACE |
| GJCATCH3.BMP | 5 | 0 | 0 | CATCH 3, EIGHT ARM MENACE, FISH AT A (JUNK), FISH AT A KEEPERS |
| GJDIVE.BMP | 13 | 0 | 0 | GAG DIVES |
| GJFFFOOD.BMP | 5 | 0 | 0 | FISH EATS FOUL FOOD |
| GJGULL1A.BMP | 10 | 0 | 0 | GAG JOHN READ, GULL 1 READING, GULL 3 STILL READING, MUNDANE JOHN READ |
| GJGULL2A.BMP | 13 | 0 | 0 | GULL 2 BATHING, JOHN BATH |
| GJGULL3.BMP | 17 | 0 | 0 | GAG JOHN READ, GULL 1 READING, GULL 3 STILL READING, MUNDANE JOHN READ |
| GJGULL3A.BMP | 24 | 0 | 0 | GAG JOHN READ, GULL 1 READING, GULL 3 STILL READING, MUNDANE JOHN READ |
| GJHOT.BMP | 23 | 0 | 0 | HOT SUMMER DAYS, NATIVE 1, NATIVE 3 |
| GJKINGKO.BMP | 21 | 0 | 0 | LILIPUT 2, MJSAND |
| GJRUNAWA.BMP | 12 | 0 | 0 | LILIPUT 2, MJSAND |
| GJVIS3.BMP | 1 | 2 | 0 | VISITOR 3 |
| GJVIS5.BMP | 27 | 0 | 0 | COCONUT VISITOR 5 , VISITOR 6 |
| GJVIS52.BMP | 0 | 7 | 0 | COCONUT VISITOR 5  |
| GJVIS6.BMP | 18 | 0 | 0 | VISITOR 6 |
| INTRO.SCR | 1 | 0 | 0 |  |
| JATA.BMP | 1 | 0 | 0 |  |
| JCHANGE.BMP | 6 | 0 | 0 | GULL 2 BATHING, JOG, JOHN BATH, JOHNNY LEAVES, NATIVE 1, NATIVE 3, THE DATE |
| JOHNWALK.BMP | 7 | 0 | 28 | BOTTLE (FIND), BOTTLE (THROW), CATCH 1, CATCH 3, COCONUT 360, COCONUT CHASE, COCONUT DROP L & R, COCONUT VISITOR 5 , EAT, EIGHT ARM MENACE, FISH AT A (JUNK), FISH AT A KEEPERS, FISH AT C FOR JUNK, FISH AT KEEPERS, FISH EATS FOUL FOOD, GAG DIVES, GAG JOHN READ, GULL 1 READING, GULL 3 STILL READING, HOT SUMMER DAYS, JOG, JOHN & MARY BREAK UP, JOHN BUILDS FIRE, JOHN FINAL MESSAGE, JOHN'S 1ST MESSAGE, JOHNNY GLIMPLSE MARY, JOHNNY LEAVES, LILIPUT 1, LILIPUT 2, LILIPUT 3 NIGHT, MJ RAFT, MJSAND, MUNDANE DIVE, MUNDANE JOHN READ, MUNDANE SLEEP, SHARK1, THE DATE, VISITOR 6, WOULDBEAS |
| JOHNWOUL.BMP | 13 | 0 | 0 | WOULDBEAS |
| LITEBULB.BMP | 2 | 0 | 0 | BOTTLE (FIND), BOTTLE (THROW), GAG JOHN READ, GULL 1 READING, GULL 3 STILL READING, JOHN & MARY BREAK UP, JOHN FINAL MESSAGE, JOHN'S 1ST MESSAGE, JOHNNY ASKS FOR DATE, MUNDANE JOHN READ, NATIVE 1, NATIVE 3, SUZY CITY DWELLER, THE DATE, WOULDBEAS |
| MEXCWALK.BMP | 8 | 0 | 0 | JOHN & MARY BREAK UP, JOHNNY GLIMPLSE MARY, NATIVE 1, NATIVE 3 |
| MJBATH.BMP | 31 | 1 | 0 | GULL 2 BATHING, JOHN BATH |
| MJBOTTLE.BMP | 27 | 0 | 0 | BOTTLE (FIND), BOTTLE (THROW), JOHN FINAL MESSAGE, JOHN'S 1ST MESSAGE |
| MJBTL2.BMP | 13 | 0 | 0 | BOTTLE (FIND), BOTTLE (THROW), JOHN FINAL MESSAGE, JOHN'S 1ST MESSAGE |
| MJCOCO.BMP | 41 | 0 | 0 | COCONUT 360, COCONUT CHASE, COCONUT DROP L & R, COCONUT VISITOR 5  |
| MJDIVE.BMP | 15 | 4 | 0 | EIGHT ARM MENACE, GAG DIVES, MUNDANE DIVE |
| MJFISH1.BMP | 25 | 0 | 0 | CATCH 1, CATCH 3, EIGHT ARM MENACE, FISH AT A (JUNK), FISH AT A KEEPERS, FISH AT C FOR JUNK, FISH AT KEEPERS, FISH EATS FOUL FOOD, JOHNNY GLIMPLSE MARY |
| MJFISH2.BMP | 21 | 5 | 0 | CATCH 1, CATCH 3, EIGHT ARM MENACE, FISH AT A (JUNK), FISH AT A KEEPERS, FISH AT C FOR JUNK, FISH AT KEEPERS, JOHNNY GLIMPLSE MARY |
| MJFISH3.BMP | 7 | 4 | 0 | BOTTLE (FIND), BOTTLE (THROW), CATCH 1, CATCH 3, EIGHT ARM MENACE, FISH AT A (JUNK), FISH AT A KEEPERS, FISH AT C FOR JUNK, FISH AT KEEPERS, JOHN FINAL MESSAGE, JOHN'S 1ST MESSAGE, JOHNNY GLIMPLSE MARY |
| MJJOG1.BMP | 14 | 0 | 0 | JOG |
| MJJOG2.BMP | 24 | 0 | 0 | JOG |
| MJRAFT2.BMP | 10 | 0 | 0 | JOHN & MARY BREAK UP, MJ RAFT |
| MJREAD.BMP | 29 | 0 | 0 | COCONUT 360, COCONUT CHASE, COCONUT DROP L & R, GAG JOHN READ, GULL 1 READING, GULL 3 STILL READING, JOHNNY ASKS FOR DATE, MUNDANE JOHN READ |
| MJSANDC.BMP | 11 | 0 | 0 | LILIPUT 2, MJSAND |
| MJTELE.BMP | 20 | 0 | 0 | TELESCOPE POS C, TELESCOPE POS. A, VISITOR 3 |
| MJTELE2.BMP | 4 | 0 | 0 | TELESCOPE POS C, TELESCOPE POS. A, VISITOR 3 |
| MJ_AMB.BMP | 35 | 0 | 0 | MUN AMB POS.A NW, MUN AMB POS.A W, MUN AMB POS.B S, MUN AMB POS.B SE, MUN AMB POS.B SW, MUN AMB POS.C E, MUN AMB POS.C NE, MUN AMB POS.D  NW, MUN AMB POS.D NE, MUN AMB POS.E NW, MUN AMB POS.F NE, MUN. AMB. POS.A  SW |
| SBREAKUP.BMP | 13 | 0 | 0 | JOHN & MARY BREAK UP |
| SHARK.BMP | 21 | 0 | 0 | SHARK1 |
| SHARKWLK.BMP | 6 | 0 | 0 | SHARK1 |
| SHKNFIST.BMP | 4 | 0 | 0 | EIGHT ARM MENACE |
| SJBRAKUP.BMP | 2 | 0 | 0 | JOHN & MARY BREAK UP |
| SJGFTASK.BMP | 12 | 2 | 0 | JOHNNY ASKS FOR DATE |
| SJGFTJMP.BMP | 6 | 0 | 0 | JOHNNY ASKS FOR DATE |
| SJGFTSHY.BMP | 8 | 0 | 0 | JOHN & MARY BREAK UP, JOHNNY ASKS FOR DATE |
| SJGFTXCH.BMP | 14 | 0 | 0 | JOHNNY ASKS FOR DATE |
| SJMSUZY1.BMP | 9 | 0 | 0 | JOHN MEETS SUZY |
| SJMSUZY2.BMP | 9 | 2 | 0 | JOHN MEETS SUZY |
| SJMSUZY3.BMP | 14 | 2 | 0 | JOHN MEETS SUZY |
| SJRAFT1.BMP | 10 | 0 | 0 | JOHN & MARY BREAK UP, MJ RAFT |
| SJWORK.BMP | 12 | 0 | 0 | JOHN AT WORK |
| SLEEP.BMP | 17 | 0 | 0 | LILIPUT 1, LILIPUT 3 NIGHT, MUNDANE SLEEP |
| SLEVEJC1.BMP | 9 | 0 | 0 | JOHNNY LEAVES |
| SLEVEJC2.BMP | 14 | 0 | 0 | JOHNNY LEAVES |
| SLEVEJC3.BMP | 12 | 0 | 0 | JOHNNY LEAVES |
| SMDATE10.BMP | 4 | 0 | 0 | THE DATE |
| SMDATE11.BMP | 15 | 0 | 0 | THE DATE |
| SMDATE12.BMP | 0 | 2 | 0 | THE DATE |
| SMDATE2.BMP | 10 | 0 | 0 | THE DATE |
| SMDATE3.BMP | 16 | 0 | 0 | THE DATE |
| SMDATE4.BMP | 8 | 0 | 0 | THE DATE |
| SMDATE5.BMP | 11 | 0 | 0 | THE DATE |
| SMDATE6.BMP | 18 | 0 | 0 | THE DATE |
| SMDATE8.BMP | 3 | 1 | 0 | THE DATE |
| SMDATE9.BMP | 15 | 0 | 0 | THE DATE |
| SSUZY3.BMP | 0 | 7 | 0 | JOHN MEETS SUZY, SUZY CITY DWELLER |
| STNDLAY.BMP | 10 | 0 | 0 | LILIPUT 1, LILIPUT 3 NIGHT, MUNDANE SLEEP |
| THEEND1.BMP | 0 | 16 | 0 | THE END |
| THNKBUBL.BMP | 2 | 0 | 0 | BOTTLE (FIND), BOTTLE (THROW), JOHN AT WORK, JOHN FINAL MESSAGE, JOHN'S 1ST MESSAGE |
| WOULDBE.BMP | 13 | 15 | 0 | WOULDBEAS |

Resource-to-story associations identify where to investigate. They do not prove that every frame runs in every listed story. Ambiguous script slots remain explicit in the detailed scene map.
