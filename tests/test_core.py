import unittest
from aidiff.core.prompt_manager import PromptManager
from aidiff.core.diff_parser import DiffParser
from aidiff.utils.issue_parser import IssueParser
import tempfile
import os

class TestPromptAssembly(unittest.TestCase):
    def setUp(self):
        # Create temporary directory with test prompt
        self.temp_dir = tempfile.mkdtemp()
        self.prompt_file = os.path.join(self.temp_dir, "security.md")
        with open(self.prompt_file, 'w') as f:
            f.write("Test security prompt")
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_prompt_assembly(self):
        prompt_manager = PromptManager(self.temp_dir)
        diff = '+print("hello")\n'
        prompt = prompt_manager.build_final_prompt(['security'], diff)
        self.assertIn('Git Diff', prompt)
        self.assertIn(diff.strip(), prompt)

class TestDiffParsing(unittest.TestCase):
    def setUp(self):
        self.parser = DiffParser()
        
    def test_clean_diff(self):
        raw = 'diff --git a/foo.py b/foo.py\n+print("hi")\n'
        cleaned = self.parser.clean_diff(raw)
        self.assertIn('+print("hi")', cleaned)

class TestLLMOutputParsing(unittest.TestCase):
    def setUp(self):
        self.parser = IssueParser()
        
    def test_parse_llm_output(self):
        llm_output = '''---\n**Issue:** Hardcoded secret\n**File:** foo.py\n**Severity:** High\n**Confidence:** 95%\n**Suggestion:** Remove secret\n---'''
        issues = self.parser.parse_llm_output(llm_output)
        # Only count non-empty issues
        issues = [i for i in issues if i.issue or i.suggestion]
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].file, 'foo.py')
        self.assertIn('Hardcoded secret', issues[0].issue)

if __name__ == '__main__':
    unittest.main()
