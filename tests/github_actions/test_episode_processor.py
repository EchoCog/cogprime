"""
Tests for GitHub Actions episode processor.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

# We need to add the path to import the episode processor
import sys
sys.path.append('/home/runner/work/cogprime/cogprime/.github/scripts')

from generate_episode_issues import EpisodeProcessor

class TestEpisodeProcessor(unittest.TestCase):
    """Test cases for EpisodeProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'GITHUB_TOKEN': 'test_token',
            'REPO_OWNER': 'test_owner',
            'REPO_NAME': 'test_repo',
            'EPISODE_RANGE': 'all'
        })
        self.env_patcher.start()
        
        self.processor = EpisodeProcessor()
    
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
    
    def test_parse_episode_range_all(self):
        """Test parsing 'all' episode range."""
        self.processor.episode_range = 'all'
        result = self.processor.parse_episode_range()
        expected = list(range(0, 51))  # Episodes 0-50
        self.assertEqual(result, expected)
    
    def test_parse_episode_range_single(self):
        """Test parsing single episode number."""
        self.processor.episode_range = '5'
        result = self.processor.parse_episode_range()
        self.assertEqual(result, [5])
    
    def test_parse_episode_range_range(self):
        """Test parsing episode range."""
        self.processor.episode_range = '10-15'
        result = self.processor.parse_episode_range()
        expected = list(range(10, 16))  # 10, 11, 12, 13, 14, 15
        self.assertEqual(result, expected)
    
    def test_extract_episode_content(self):
        """Test extracting content from episode file."""
        # Create a temporary episode file
        episode_content = """# Episode 5: The Sacred and the Meaning Crisis

## Introduction
This episode explores the relationship between the sacred and meaning.

## What is the Sacred?
The sacred refers to something set apart, beyond the ordinary.

## Key Concepts
Here we discuss **relevance realization** and `cognitive frameworks`.

## Conclusion
Understanding the sacred helps address the meaning crisis.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(episode_content)
            temp_path = Path(f.name)
        
        try:
            result = self.processor.extract_episode_content(temp_path)
            
            self.assertEqual(result['title'], 'Episode 5: The Sacred and the Meaning Crisis')
            self.assertIn('Introduction', result['sections'])
            self.assertIn('What is the Sacred?', result['sections'])
            self.assertIn('Key Concepts', result['sections'])
            self.assertIn('Conclusion', result['sections'])
            
            # Check that key concepts were extracted
            self.assertTrue(len(result['concepts']) > 0)
            
            # Check that summary was created
            self.assertTrue(len(result['summary']) > 0)
            self.assertIn('sacred', result['summary'].lower())
            
        finally:
            # Clean up temporary file
            temp_path.unlink()
    
    def test_extract_key_concepts(self):
        """Test extracting key concepts from content."""
        content = """
        This episode discusses **Relevance Realization** and the importance of
        `cognitive science` in understanding `meaning-making`. We also explore
        **Wisdom Traditions** and their role in addressing existential concerns.
        """
        
        concepts = self.processor.extract_key_concepts(content)
        
        # Should extract bold and code-formatted terms
        self.assertIn('Relevance Realization', concepts)
        self.assertIn('cognitive science', concepts)
        self.assertIn('meaning-making', concepts)
        self.assertIn('Wisdom Traditions', concepts)
    
    def test_extract_summary(self):
        """Test extracting summary from content."""
        content = """# Episode Title

This is the first paragraph of the episode. It introduces the main topic.

This is the second paragraph. It provides more context and detail.

This is the third paragraph that should not be included in the summary.

## Section Header
More content here.
"""
        
        summary = self.processor.extract_summary(content)
        
        # Should contain first two paragraphs
        self.assertIn('first paragraph', summary)
        self.assertIn('second paragraph', summary)
        self.assertNotIn('third paragraph', summary)
        self.assertNotIn('Section Header', summary)
    
    def test_create_issue_body(self):
        """Test creating issue body content."""
        episode_data = {
            'title': 'Episode 1: Introduction',
            'summary': 'This episode introduces the meaning crisis.',
            'file_path': '50 Episodes in Relevance Realization/Episode_01.md',
            'sections': ['Introduction', 'The Problem', 'Next Steps'],
            'concepts': ['meaning crisis', 'relevance realization', 'cognitive science']
        }
        
        body = self.processor.create_issue_body(episode_data)
        
        # Check that all elements are included
        self.assertIn('This episode introduces the meaning crisis', body)
        self.assertIn('50 Episodes in Relevance Realization/Episode_01.md', body)
        self.assertIn('Introduction', body)
        self.assertIn('The Problem', body)
        self.assertIn('meaning crisis', body)
        self.assertIn('relevance realization', body)
        self.assertIn('Discussion Points', body)
        self.assertIn('automatically generated', body)
    
    @patch('generate_episode_issues.requests.get')
    def test_check_issue_exists_true(self, mock_get):
        """Test checking if issue exists (returns True)."""
        # Mock API response with existing issue
        mock_response = Mock()
        mock_response.json.return_value = [
            {'title': 'Episode Discussion: Episode 1: Introduction'}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.processor.check_issue_exists('Episode Discussion: Episode 1: Introduction')
        self.assertTrue(result)
    
    @patch('generate_episode_issues.requests.get')
    def test_check_issue_exists_false(self, mock_get):
        """Test checking if issue exists (returns False)."""
        # Mock API response with no matching issues
        mock_response = Mock()
        mock_response.json.return_value = [
            {'title': 'Episode Discussion: Episode 2: Different Title'}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.processor.check_issue_exists('Episode Discussion: Episode 1: Introduction')
        self.assertFalse(result)
    
    @patch('generate_episode_issues.requests.post')
    @patch('generate_episode_issues.requests.get')
    def test_create_github_issue_success(self, mock_get, mock_post):
        """Test successful GitHub issue creation."""
        # Mock check_issue_exists to return False (issue doesn't exist)
        mock_get_response = Mock()
        mock_get_response.json.return_value = []
        mock_get_response.raise_for_status.return_value = None
        mock_get.return_value = mock_get_response
        
        # Mock successful issue creation
        mock_post_response = Mock()
        mock_post_response.json.return_value = {'number': 123, 'title': 'Test Issue'}
        mock_post_response.raise_for_status.return_value = None
        mock_post.return_value = mock_post_response
        
        episode_data = {
            'title': 'Episode 1: Introduction',
            'summary': 'Test summary',
            'file_path': 'test/path.md',
            'sections': ['Section 1'],
            'concepts': ['concept 1']
        }
        
        result = self.processor.create_github_issue(episode_data)
        self.assertTrue(result)
        
        # Verify the API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('title', call_args[1]['json'])
        self.assertIn('body', call_args[1]['json'])
        self.assertIn('labels', call_args[1]['json'])
    
    @patch('generate_episode_issues.requests.get')
    def test_create_github_issue_already_exists(self, mock_get):
        """Test GitHub issue creation when issue already exists."""
        # Mock check_issue_exists to return True (issue exists)
        mock_response = Mock()
        mock_response.json.return_value = [
            {'title': 'Episode Discussion: Episode 1: Introduction'}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        episode_data = {
            'title': 'Episode 1: Introduction',
            'summary': 'Test summary',
            'file_path': 'test/path.md',
            'sections': [],
            'concepts': []
        }
        
        result = self.processor.create_github_issue(episode_data)
        self.assertFalse(result)  # Should return False when issue already exists

class TestEpisodeProcessorIntegration(unittest.TestCase):
    """Integration tests for EpisodeProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'GITHUB_TOKEN': 'test_token',
            'REPO_OWNER': 'test_owner', 
            'REPO_NAME': 'test_repo',
            'EPISODE_RANGE': '1-3'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
    
    def test_initialization_with_missing_env(self):
        """Test initialization fails with missing environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                EpisodeProcessor()
    
    def test_initialization_success(self):
        """Test successful initialization."""
        processor = EpisodeProcessor()
        self.assertEqual(processor.repo_owner, 'test_owner')
        self.assertEqual(processor.repo_name, 'test_repo')
        self.assertEqual(processor.episode_range, '1-3')

if __name__ == '__main__':
    unittest.main()