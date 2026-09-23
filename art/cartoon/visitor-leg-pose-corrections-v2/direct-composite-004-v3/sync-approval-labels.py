"""Keep viewer labels accurate after the scoped 004 approval."""
from pathlib import Path

path = Path(__file__).resolve().parent.parent / "color-sequence-template.html"
text = path.read_text(encoding="utf-8")
replacements = {
    "004 and 005 candidates: awaiting review.": "004 approved; 005 candidate awaiting review.",
    "NEW 004 / 005 candidates": "Current 004 / 005 review drawings",
    "Approved selections (imported 004 / 005)": "Approved selections",
    "Only 004 and 005 change between modes.": "004 is approved. Only 005 changes between modes.",
    "Approved imported selection": "Approved selection",
    "Showing approved imported selections for 004 and 005. Pending candidates are available in the comparison menu.": "Showing approved selections: direct composite v3 for 004 and the prior imported drawing for 005.",
    "New candidate comparison": "Review drawing comparison",
    "The yellow border marks 004 and 005.": "005 still awaits appearance review.",
}
for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
print("004 approval labels synchronized")
