# Resume Evidence

**An explainable Python tool for comparing skill mentions in a resume and a job description.**

A working implementation of the original resume-analyzer idea. The current version is deterministic: it does not call an LLM and does not claim to simulate an employer's ATS.

## Try it in one minute

Requires Python 3.10 or newer. No third-party packages, API keys, account, or model downloads.

```bash
git clone https://github.com/engdareenbassamesleem/ai-resume-analyzer.git
cd ai-resume-analyzer
python app.py
```

Open http://127.0.0.1:8765 and select **Load synthetic example**, then **Compare skills**. The included example produces **62.5% mention coverage**: 5 of 8 recognized skills.

## What you can inspect

- Matched skills with the original resume line and job-description line.
- Job skills not found in the resume, plus other skills the resume mentions.
- A canonical dictionary of aliases such as PostgreSQL/postgres and React/react.js.
- Unicode normalization, whole-term matching and deduplication.
- An explicit unknown result when no job skills are recognized.
- A responsive browser interface and a JSON command-line output.

## CLI and API

```bash
python analyzer.py examples/resume.txt examples/job.txt
python -m unittest discover -s tests -v
```

POST /api/analyze accepts a JSON object with string fields **resume** and **job**. Each is limited to 100,000 characters. GET /health returns local service status.

## How the calculation works

1. Normalize each line with Unicode NFKC and case folding.
2. Recognize dictionary terms at word boundaries; do not count repeated keywords twice.
3. Intersect the recognized resume and job skill sets.
4. Calculate 100 × matched skills / recognized job skills. If the denominator is zero, return null.
5. Preserve the original evidence so a person can check context.

The UI treats all result text as text, not executable HTML. The local server binds to loopback, validates host/origin and bounds request size. Submitted texts are neither persisted nor sent to external services.

## Limits that matter

This is **mention coverage**, not an ATS score, suitability assessment or hiring probability. It does not infer experience level, proficiency, negation, required vs optional skills, or qualifications outside the dictionary. For example, “no Python experience” still contains a Python mention; the evidence is shown for review. English skill names are supported inside multilingual text; full Arabic skill translation is not implemented. Inputs are plain text; PDF/DOCX parsing is not implemented.

The standard-library HTTP server is for local demonstrations, not public deployment. Add a production server, authentication and resource controls before hosting for other users.

## Files and engineering focus

| File | Responsibility |
|---|---|
| analyzer.py | Normalization, skill evidence, coverage and CLI |
| app.py | HTTP adapter |
| webserver.py | Local HTTP transport and request validation |
| static/ | Accessible form, evidence cards and responsive styles |
| examples/ | Synthetic resume and vacancy |
| tests/ | Matching edge cases, CLI and HTTP behavior |

The old backend directory is retained as a historical scaffold; its previous dependency list has been replaced by an explanation of the dependency-free implementation.

## Development notes

This portfolio implementation was developed with AI coding assistance. Inspect the source and tests; no paid-client outcome or independent authorship claim is implied.

Possible extensions: a configurable dictionary, PDF extraction with page evidence, and a separately evaluated semantic matching layer.
