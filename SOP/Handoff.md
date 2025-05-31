# Handoff Template

> **IMPORTANT:** When starting a new hand-off, **create a brand-new Markdown file in the _same folder_ as `Handoff.md` with a clear, descriptive name** (example: `Handoff-LoginBug.md`).  
> _Never overwrite or rename existing hand-off documents, and **don't include dates or times in the filename**._

---

## 1 · Affected Files

List every file another developer must read or touch. _(Add more rows as needed for other affected files)_

| Path                               | Purpose                     |
| ---------------------------------- | --------------------------- |
| [Name of this new handoff file.md] | This handoff document       |
| `file_in_root1.ext`                | Brief role / responsibility |
| `file_in_root2.ext`                | Brief role / responsibility |
| `file_in_root3.ext`                | Brief role / responsibility |
| `file_in_root4.ext`                | Brief role / responsibility |
| `path/to/other_file1.ext`          | Brief role / responsibility |
| `path/to/other_file2.ext`          | Brief role / responsibility |
| `path/to/as many paths as needed`  | Brief role / responsibility |
| ...                                | ...                         |

---

## 2 · Problem Statement

Describe **what's wrong** and **why it matters**. Include:

- **Symptoms / error messages**
- **Expected vs. actual behaviour**
- **Business or user impact (severity & priority)**

---

## 3 · Reproduction Steps

Step-by-step guide to make the issue appear:

1. …
2. …
3. …

---

## 4 · Attempted Solutions & Findings

| Attempt | Key Changes Made | Outcome / Remaining Issue |
| ------- | ---------------- | ------------------------- |
| #1      | …                | …                         |
| #2      | …                | …                         |

> **Current blockers / unknowns:**
>
> - Technical constraints
> - Knowledge gaps
> - Resource limitations

---

## 5 · Developer Instructions

**Goal:** Identify the root cause and implement a sustainable fix.

1. Review the _Affected Files_ above.
2. Trace the execution path leading to the failure.
3. Propose and implement a solution (attach code snippets or PR link).
4. Document rationale, trade-offs, and potential side-effects.
5. Update tests / add new tests as needed.
6. Once complete, ensure the filled-out handoff document is made available as a downloadable file.

---

_End of template – duplicate and fill in for each new hand-off._

**Upon completion:**

Ask the 2nd-opinion expert:

            "Please read all attached files and then provide me with necessary information.

            it would be great if you can create a downloadable markdown file .md

    		Provide me  with a download link.

            Example:     Download the analysis (markdown)"
