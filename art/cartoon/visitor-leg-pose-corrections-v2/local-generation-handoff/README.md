# Exact prompts and references

[Open the handoff](index.html) | [Manifest](manifest.json) | [Copy verification](verification.json)

10 saved request versions: nine submitted, one not submitted. All submissions are stopped. No current drawing is appearance-approved.

Blocked: 003 v1, 004 v1, 009 v2, 010 v1. 004 used identical arguments twice; only its second exact error was retained. 006 v2 was never submitted.

| Attempt | Submission | Result | Files |
| --- | --- | --- | --- |
| 003-v1 | SUBMITTED | BLOCKED | [Prompt](003-v1/prompt.txt), [request](003-v1/request.json), [references](index.html#003-v1), [failure](003-v1/failure.json) |
| 004-v1 | SUBMITTED | BLOCKED | [Prompt](004-v1/prompt.txt), [request](004-v1/request.json), [references](index.html#004-v1), [failure](004-v1/failure.json) |
| 009-v2 | SUBMITTED | BLOCKED | [Prompt](009-v2/prompt.txt), [request](009-v2/request.json), [references](index.html#009-v2), [failure](009-v2/failure.json) |
| 010-v1 | SUBMITTED | BLOCKED | [Prompt](010-v1/prompt.txt), [request](010-v1/request.json), [references](index.html#010-v1), [failure](010-v1/failure.json) |
| 005-v1 | SUBMITTED | READY FOR REVIEW | [Prompt](005-v1/prompt.txt), [request](005-v1/request.json), [references](index.html#005-v1), [output](005-v1/returned-output.png) |
| 006-v1 | SUBMITTED | INSUFFICIENT | [Prompt](006-v1/prompt.txt), [request](006-v1/request.json), [references](index.html#006-v1), [output](006-v1/returned-output.png) |
| 008-v1 | SUBMITTED | INSUFFICIENT | [Prompt](008-v1/prompt.txt), [request](008-v1/request.json), [references](index.html#008-v1), [output](008-v1/returned-output.png) |
| 008-v2 | SUBMITTED | COMPARISON CANDIDATE | [Prompt](008-v2/prompt.txt), [request](008-v2/request.json), [references](index.html#008-v2), [output](008-v2/returned-output.png) |
| 009-v1 | SUBMITTED | INSUFFICIENT | [Prompt](009-v1/prompt.txt), [request](009-v1/request.json), [references](index.html#009-v1), [output](009-v1/returned-output.png) |
| 006-v2 | NOT SUBMITTED | PREPARED ONLY | [Prompt](006-v2/prompt.txt), [request](006-v2/request.json), [references](index.html#006-v2) |

Every prompt.txt contains the exact decoded arguments.prompt string encoded as UTF-8, with no added newline. Each request.json is an unchanged byte copy. Reference PNGs are numbered in their original argument order. Failure records and returned outputs/records are included where they exist.

Request JSON retains historical absolute paths. Use the numbered local reference files in the same order when supplying inputs elsewhere. There is no submission script.

Statuses come from copied [003 notes](notes/visitor-003-notes.md), [004–006 notes](notes/visitor-004-006-notes.md) and [008–010 notes](notes/visitor-008-010-notes.md).

[Official documentation](https://learn.chatgpt.com/docs/image-generation), checked on 2026-09-21, identifies the built-in backend as gpt-image-2. Retained tool responses supply no per-call model ID.
