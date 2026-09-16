# Preserved source-only route investigation

These three files are exact copies from the executed scratch investigation in
`build/connecting-analysis/`: `analyze.py`, `route-analysis.json` and
`route-plan.md`. The Python program was executed from that scratch location;
its relative root calculation assumes two directory levels beneath the repository.
Do not run this preservation copy in place. To repeat the investigation, copy
`analyze.py` into a fresh directory immediately below `build/` and run that copy.
It writes its new report beside itself. Compare the predicted draw sequences;
the captured Git commit field changes when the repository advances.

The interpreter checks preserved actual-C trace rows, not a newly compiled
engine or the original executable. Actual native transition captures remain
required. All source identities, case predictions and static TTM sites are in
`route-analysis.json`; interpretation limits are in `route-plan.md`.
