import unittest
import os
import tempfile
import shutil
import io
from gpt_repository_loader import process_repository, get_ignore_list, ContentFilter

class MockLLM:
    def __call__(self, prompt, max_tokens=None, temperature=None, stop=None):
        if "binary_file.bin" in prompt or "generated_code.js" in prompt:
            return {"choices": [{"text": "NO"}]}
        return {"choices": [{"text": "YES"}]}

class TestGPTRepositoryLoader(unittest.TestCase):
    def setUp(self):
        self.test_data_path = os.path.join(os.path.dirname(__file__), 'test_data')
        self.example_repo_path = os.path.join(self.test_data_path, 'example_repo')
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files for content filtering
        self.create_test_files()

    def create_test_files(self):
        # Create a source code file that should be kept
        with open(os.path.join(self.temp_dir, 'main.py'), 'w') as f:
            f.write('def main():\n    print("Hello, World!")\n')
        
        # Create a binary-like file that should be filtered
        with open(os.path.join(self.temp_dir, 'binary_file.bin'), 'wb') as f:
            f.write(b'\x00\x01\x02\x03')
        
        # Create a generated code file that should be filtered
        with open(os.path.join(self.temp_dir, 'generated_code.js'), 'w') as f:
            f.write('// GENERATED CODE - DO NOT EDIT\n')

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_end_to_end(self):
        # Set up the output file and the expected output file paths
        output_file_path = os.path.join(tempfile.mkdtemp(), 'output.txt')
        expected_output_file_path = os.path.join(self.test_data_path, 'expected_output.txt')

        # Get the ignore list using the repository path
        ignore_list = get_ignore_list(self.example_repo_path)

        # Run the gpt-repository-loader script on the example repository
        with open(output_file_path, 'w') as output_file:
            process_repository(self.example_repo_path, ignore_list, output_file)

        # Compare the output to the expected output
        with open(output_file_path, 'r') as output_file, open(expected_output_file_path, 'r') as expected_output_file:
            self.assertEqual(output_file.read(), expected_output_file.read())

        # Clean up the output file
        shutil.rmtree(os.path.dirname(output_file_path))

    def test_content_filter(self):
        # Create a content filter with mock LLM
        content_filter = ContentFilter()
        content_filter.llm = MockLLM()

        # Test with source code file
        with open(os.path.join(self.temp_dir, 'main.py'), 'r') as f:
            content = f.read()
            self.assertTrue(content_filter.is_relevant(content, 'main.py'))

        # Test with binary file
        with open(os.path.join(self.temp_dir, 'binary_file.bin'), 'rb') as f:
            content = f.read().decode('latin1')  # Use latin1 to handle binary data
            self.assertFalse(content_filter.is_relevant(content, 'binary_file.bin'))

        # Test with generated code
        with open(os.path.join(self.temp_dir, 'generated_code.js'), 'r') as f:
            content = f.read()
            self.assertFalse(content_filter.is_relevant(content, 'generated_code.js'))

    def test_process_with_filter(self):
        output_stream = io.StringIO()
        ignore_list = []
        content_filter = ContentFilter()
        content_filter.llm = MockLLM()

        total_tokens = process_repository(
            self.temp_dir,
            ignore_list,
            output_stream,
            content_filter=content_filter
        )

        output = output_stream.getvalue()
        
        # Check that main.py is included
        self.assertIn('main.py', output)
        # Check that binary and generated files are excluded
        self.assertNotIn('binary_file.bin', output)
        self.assertNotIn('generated_code.js', output)

if __name__ == '__main__':
    unittest.main()