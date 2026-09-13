import json
import subprocess
import sys
import unittest
from pathlib import Path

from analyzer import analyze, evidence


class AnalyzerTests(unittest.TestCase):
    def test_exact_evidence_and_coverage(self):
        result = analyze("Built Python services.\nUsed SQL.", "Python, SQL and Docker")
        self.assertEqual(result["coverage_percent"], 66.7)
        self.assertEqual(result["matched"][0]["resume_evidence"], "Built Python services.")
        self.assertEqual(result["not_found_in_resume"][0]["skill"], "Docker")

    def test_whole_terms_prevent_false_matches(self):
        self.assertEqual(evidence("digital reaction makes things happen"), {})
        self.assertNotIn("SQL", evidence("PostgreSQL"))
        self.assertNotIn("Make", evidence("make dinner"))

    def test_aliases_unicode_and_case(self):
        self.assertEqual(set(evidence("Ｐｙｔｈｏｎ REACT.JS postgres make.com")),
                         {"Python", "React", "PostgreSQL", "Make"})

    def test_repeated_keywords_do_not_inflate_score(self):
        self.assertEqual(analyze("Python " * 100, "Python Docker")["coverage_percent"], 50)

    def test_no_known_job_skills_is_unknown(self):
        self.assertIsNone(analyze("Python", "Excellent interpersonal skills")["coverage_percent"])

    def test_negation_preserves_evidence_for_human_review(self):
        result = analyze("No experience with Docker", "Docker required")
        self.assertEqual(result["matched"][0]["resume_evidence"], "No experience with Docker")
        self.assertIn("Negation", " ".join(result["limitations"]))

    def test_invalid_input(self):
        for value in ("", " ", None, [], "x" * 100_001):
            with self.subTest(value=str(value)[:20]), self.assertRaises(ValueError):
                analyze(value, "Python")

    def test_sample_cli(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "analyzer.py", "examples/resume.txt", "examples/job.txt"],
            cwd=root, text=True, capture_output=True, check=True,
        )
        self.assertEqual(json.loads(result.stdout)["coverage_percent"], 62.5)


if __name__ == "__main__":
    unittest.main()
