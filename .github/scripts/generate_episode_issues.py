#!/usr/bin/env python3
"""
GitHub Actions script to generate issues from episode files.

This script processes the "50 Episodes in Relevance Realization" markdown files
and creates GitHub issues for each episode, extracting key concepts and discussion points.
"""

import os
import re
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class EpisodeProcessor:
    """Processes episode markdown files and generates GitHub issues."""
    
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.repo_owner = os.environ.get('REPO_OWNER')
        self.repo_name = os.environ.get('REPO_NAME')
        self.episode_range = os.environ.get('EPISODE_RANGE', 'all')
        
        if not all([self.github_token, self.repo_owner, self.repo_name]):
            raise ValueError("Missing required environment variables")
            
        self.github_api_base = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def parse_episode_range(self) -> List[int]:
        """Parse the episode range input."""
        if self.episode_range.lower() == 'all':
            return list(range(0, 51))  # Episodes 0-50
        
        if '-' in self.episode_range:
            start, end = map(int, self.episode_range.split('-'))
            return list(range(start, end + 1))
        
        return [int(self.episode_range)]
    
    def extract_episode_content(self, file_path: Path) -> Dict[str, str]:
        """Extract structured content from an episode file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else f"Episode {file_path.stem.split('_')[1]}"
        
        # Extract sections
        sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        
        # Extract key concepts (items that appear to be important topics)
        concepts = self.extract_key_concepts(content)
        
        # Extract a summary (first few paragraphs)
        summary = self.extract_summary(content)
        
        return {
            'title': title,
            'sections': sections,
            'concepts': concepts,
            'summary': summary,
            'file_path': str(file_path)
        }
    
    def extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts from episode content."""
        concepts = []
        
        # Look for capitalized terms that might be concepts
        concept_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized phrases
            r'\*\*([^*]+)\*\*',  # Bold text
            r'`([^`]+)`',  # Code/emphasis text
        ]
        
        for pattern in concept_patterns:
            matches = re.findall(pattern, content)
            concepts.extend(matches)
        
        # Filter and deduplicate
        filtered_concepts = []
        for concept in concepts:
            if (len(concept) > 3 and 
                concept not in filtered_concepts and
                concept not in ['The', 'And', 'But', 'What', 'How', 'Why', 'This', 'That']):
                filtered_concepts.append(concept)
        
        return filtered_concepts[:10]  # Limit to top 10
    
    def extract_summary(self, content: str) -> str:
        """Extract a summary from the episode content."""
        # Remove header and get first few paragraphs
        lines = content.split('\n')
        summary_lines = []
        
        in_content = False
        paragraph_count = 0
        
        for line in lines:
            line = line.strip()
            
            # Skip headers
            if line.startswith('#'):
                in_content = True
                continue
            
            if in_content and line and not line.startswith('#'):
                summary_lines.append(line)
                if line.endswith('.') or line.endswith('!') or line.endswith('?'):
                    paragraph_count += 1
                    if paragraph_count >= 2:  # First 2 paragraphs
                        break
        
        summary = ' '.join(summary_lines)
        if len(summary) > 500:
            summary = summary[:497] + "..."
        
        return summary
    
    def create_issue_body(self, episode_data: Dict[str, str]) -> str:
        """Create the issue body content."""
        body_parts = [
            f"## Episode Summary\n\n{episode_data['summary']}\n",
            f"## File Location\n\n`{episode_data['file_path']}`\n"
        ]
        
        if episode_data['sections']:
            sections_list = '\n'.join([f"- {section}" for section in episode_data['sections']])
            body_parts.append(f"## Key Sections\n\n{sections_list}\n")
        
        if episode_data['concepts']:
            concepts_list = '\n'.join([f"- {concept}" for concept in episode_data['concepts']])
            body_parts.append(f"## Key Concepts\n\n{concepts_list}\n")
        
        body_parts.extend([
            "## Discussion Points\n\n- [ ] Review episode content for implementation insights",
            "- [ ] Identify cognitive patterns mentioned in this episode",
            "- [ ] Extract relevant quotes or frameworks",
            "- [ ] Connect to existing CogPrime modules",
            "- [ ] Document any new concepts for implementation\n",
            "## Labels\n\n`episode`, `documentation`, `research`\n",
            "---\n",
            "*This issue was automatically generated from episode content. Please add relevant discussion points and implementation notes.*"
        ])
        
        return '\n'.join(body_parts)
    
    def check_issue_exists(self, title: str) -> bool:
        """Check if an issue with this title already exists."""
        search_url = f"{self.github_api_base}/issues"
        params = {
            'state': 'all',
            'labels': 'episode',
            'per_page': 100
        }
        
        try:
            response = requests.get(search_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            issues = response.json()
            for issue in issues:
                if issue['title'].strip() == title.strip():
                    return True
            return False
        except requests.RequestException as e:
            print(f"Error checking existing issues: {e}")
            return False
    
    def create_github_issue(self, episode_data: Dict[str, str]) -> bool:
        """Create a GitHub issue for an episode."""
        title = f"Episode Discussion: {episode_data['title']}"
        
        # Check if issue already exists
        if self.check_issue_exists(title):
            print(f"Issue already exists for: {title}")
            return False
        
        issue_data = {
            'title': title,
            'body': self.create_issue_body(episode_data),
            'labels': ['episode', 'documentation', 'research']
        }
        
        url = f"{self.github_api_base}/issues"
        
        try:
            response = requests.post(url, headers=self.headers, json=issue_data)
            response.raise_for_status()
            
            issue = response.json()
            print(f"Created issue #{issue['number']}: {title}")
            return True
            
        except requests.RequestException as e:
            print(f"Error creating issue for {title}: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return False
    
    def process_episodes(self) -> Dict[str, int]:
        """Process episodes and create issues."""
        episodes_dir = Path("50 Episodes in Relevance Realization")
        
        if not episodes_dir.exists():
            raise FileNotFoundError(f"Episodes directory not found: {episodes_dir}")
        
        episode_numbers = self.parse_episode_range()
        results = {"created": 0, "skipped": 0, "errors": 0}
        
        for episode_num in episode_numbers:
            episode_file = episodes_dir / f"Episode_{episode_num:02d}.md"
            
            if not episode_file.exists():
                print(f"Episode file not found: {episode_file}")
                results["errors"] += 1
                continue
            
            try:
                print(f"Processing {episode_file}...")
                episode_data = self.extract_episode_content(episode_file)
                
                if self.create_github_issue(episode_data):
                    results["created"] += 1
                else:
                    results["skipped"] += 1
                    
            except Exception as e:
                print(f"Error processing {episode_file}: {e}")
                results["errors"] += 1
        
        return results

def main():
    """Main function to run the episode processor."""
    try:
        processor = EpisodeProcessor()
        results = processor.process_episodes()
        
        print(f"\n=== Results ===")
        print(f"Issues created: {results['created']}")
        print(f"Issues skipped: {results['skipped']}")
        print(f"Errors: {results['errors']}")
        
        if results['errors'] > 0:
            exit(1)
            
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)

if __name__ == "__main__":
    main()