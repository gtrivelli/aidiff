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

if __name__ == '__main__':
    unittest.main()
