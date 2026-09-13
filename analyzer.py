"""Explainable skill evidence matching. No external services or hiring predictions."""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

SKILLS = {
    "Python": ("python",),
    "SQL": ("sql",),
    "JavaScript": ("javascript", "js"),
    "TypeScript": ("typescript",),
    "React": ("react", "react.js", "reactjs"),
    "Next.js": ("next.js", "nextjs"),
    "HTML": ("html", "html5"),
    "CSS": ("css", "css3"),
    "FastAPI": ("fastapi",),
    "Flask": ("flask",),
    "Django": ("django",),
    "pandas": ("pandas",),
    "NumPy": ("numpy",),
    "scikit-learn": ("scikit-learn", "sklearn"),
    "Excel": ("excel",),
    "Google Sheets": ("google sheets", "google spreadsheets"),
    "Power BI": ("power bi", "powerbi"),
    "n8n": ("n8n",),
    "Zapier": ("zapier",),
    "Make": ("make.com", "integromat"),
    "REST APIs": ("rest api", "rest apis", "restful", "restful api"),
    "Webhooks": ("webhook", "webhooks"),
    "Git": ("git",),
    "GitHub Actions": ("github actions",),
    "Docker": ("docker",),
    "PostgreSQL": ("postgresql", "postgres"),
    "SQLite": ("sqlite",),
    "Firebase": ("firebase", "firestore"),
    "Testing": ("pytest", "unittest", "unit tests", "unit testing"),
    "Statistics": ("statistics", "statistical", "probability"),
    "Linear Algebra": ("linear algebra",),
    "RAG": ("rag", "retrieval augmented generation", "retrieval-augmented generation"),
    "LLMs": ("llm", "llms", "large language models"),
}
MAX_TEXT = 100_000


def normalize(text):
    return unicodedata.normalize("NFKC", text).casefold()


def evidence(text):
    """Return one original line per canonical skill, using whole-term matches."""
    result = {}
    for line in text.splitlines():
        normalized = normalize(line)
        for skill, aliases in SKILLS.items():
            for alias in aliases:
                if re.search(r"(?<![\w.])" + re.escape(alias) + r"(?!\w)", normalized):
                    result.setdefault(skill, line.strip()[:350])
                    break
    return result


def analyze(resume, job):
    for name, value in (("resume", resume), ("job", job)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must contain text.")
        if len(value) > MAX_TEXT:
            raise ValueError(f"{name} exceeds {MAX_TEXT:,} characters.")
    resume_skills, job_skills = evidence(resume), evidence(job)
    matched = sorted(job_skills.keys() & resume_skills.keys())
    missing = sorted(job_skills.keys() - resume_skills.keys())
    extra = sorted(resume_skills.keys() - job_skills.keys())
    return {
        "method": "Explicit skill mentions using a versioned alias dictionary",
        "coverage_percent": round(100 * len(matched) / len(job_skills), 1) if job_skills else None,
        "matched": [
            {"skill": skill, "resume_evidence": resume_skills[skill],
             "job_evidence": job_skills[skill]} for skill in matched
        ],
        "not_found_in_resume": [
            {"skill": skill, "job_evidence": job_skills[skill]} for skill in missing
        ],
        "other_resume_skills": extra,
        "recognized_job_skills": len(job_skills),
        "limitations": [
            "Mention coverage is not an ATS score or a probability of being hired.",
            "Text mentions do not prove proficiency. Negation and required vs optional are not inferred.",
            "Only dictionary skills are recognized; other qualifications are not assessed.",
            "Add a missing skill only when supported by your actual experience.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resume", type=Path, help="UTF-8 plain text resume")
    parser.add_argument("job", type=Path, help="UTF-8 plain text job description")
    args = parser.parse_args()
    try:
        result = analyze(args.resume.read_text(encoding="utf-8-sig"),
                         args.job.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
