import unittest
from reviewer import build_final_prompt
from diff_parser import clean_diff
from utils import parse_llm_output

class TestPromptAssembly(unittest.TestCase):
    def test_prompt_assembly(self):
        diff = '+print("hello")\n'
        prompt = build_final_prompt(['security'], diff)
        self.assertIn('Git Diff', prompt)
        self.assertIn(diff.strip(), prompt)

class TestDiffParsing(unittest.TestCase):
    def test_clean_diff(self):
        raw = 'diff --git a/foo.py b/foo.py\n+print("hi")\n'
        cleaned = clean_diff(raw)
        self.assertIn('+print("hi")', cleaned)

class TestLLMOutputParsing(unittest.TestCase):
    def test_parse_llm_output(self):
        llm_output = '''---\n**Issue:** Hardcoded secret\n**File:** foo.py\n**Severity:** High\n**Confidence:** 95%\n**Suggestion:** Remove secret\n---'''
        issues = parse_llm_output(llm_output)
        # Only count non-empty issues
        issues = [i for i in issues if i.get('issue') or i.get('suggestion')]
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]['file'], 'foo.py')
        self.assertIn('Hardcoded secret', issues[0]['issue'])

if __name__ == '__main__':
    unittest.main()
