"""
Integration tests for the complete CogPrime system.
"""

import unittest
import tempfile
from pathlib import Path

class TestCogPrimeIntegration(unittest.TestCase):
    """Integration tests for the complete CogPrime system."""
    
    def test_documentation_exists(self):
        """Test that core documentation files exist."""
        # Check main README
        readme_path = Path("README.md")
        self.assertTrue(readme_path.exists(), "README.md should exist")
        
        # Check architecture documentation
        arch_path = Path("docs/ARCHITECTURE.md")
        self.assertTrue(arch_path.exists(), "Architecture documentation should exist")
        
        # Check configuration
        config_path = Path("config/daemon.yml")
        self.assertTrue(config_path.exists(), "Daemon configuration should exist")
    
    def test_vm_daemon_sys_modules(self):
        """Test that vm-daemon-sys modules can be imported."""
        try:
            from src.vm_daemon_sys import (
                ServiceManager, LoadBalancer, HealthMonitor, 
                CognitiveOrchestrator, CognitiveDaemon
            )
            # If we get here, imports worked
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import vm-daemon-sys modules: {e}")
    
    def test_github_actions_workflow(self):
        """Test that GitHub Actions workflow exists."""
        workflow_path = Path(".github/workflows/generate-episode-issues.yml")
        self.assertTrue(workflow_path.exists(), "GitHub Actions workflow should exist")
        
        script_path = Path(".github/scripts/generate_episode_issues.py")
        self.assertTrue(script_path.exists(), "Episode processor script should exist")
    
    def test_episode_files_exist(self):
        """Test that episode files exist."""
        episodes_dir = Path("50 Episodes in Relevance Realization")
        self.assertTrue(episodes_dir.exists(), "Episodes directory should exist")
        
        # Check that we have episode files
        episode_files = list(episodes_dir.glob("Episode_*.md"))
        self.assertGreater(len(episode_files), 40, "Should have many episode files")
        
        # Check specific episodes
        episode_00 = episodes_dir / "Episode_00.md"
        episode_01 = episodes_dir / "Episode_01.md"
        self.assertTrue(episode_00.exists(), "Episode 00 should exist")
        self.assertTrue(episode_01.exists(), "Episode 01 should exist")
    
    def test_cognitive_cli_executable(self):
        """Test that the cognitive CLI script exists and is valid Python."""
        cli_path = Path("cognitive_cli.py")
        self.assertTrue(cli_path.exists(), "Cognitive CLI should exist")
        
        # Try to compile it
        with open(cli_path, 'r') as f:
            source = f.read()
        
        try:
            compile(source, str(cli_path), 'exec')
        except SyntaxError as e:
            self.fail(f"Cognitive CLI has syntax errors: {e}")
    
    def test_mermaid_diagrams_in_docs(self):
        """Test that documentation contains mermaid diagrams."""
        # Check README
        with open("README.md", 'r') as f:
            readme_content = f.read()
        
        self.assertIn("```mermaid", readme_content, "README should contain mermaid diagrams")
        
        # Check architecture doc
        with open("docs/ARCHITECTURE.md", 'r') as f:
            arch_content = f.read()
        
        self.assertIn("```mermaid", arch_content, "Architecture doc should contain mermaid diagrams")
        
        # Count mermaid diagrams
        mermaid_count = arch_content.count("```mermaid")
        self.assertGreaterEqual(mermaid_count, 5, "Should have multiple mermaid diagrams")
    
    def test_configuration_validity(self):
        """Test that configuration files are valid YAML."""
        import yaml
        
        config_path = Path("config/daemon.yml")
        with open(config_path, 'r') as f:
            try:
                config = yaml.safe_load(f)
                self.assertIsInstance(config, dict, "Config should be a dictionary")
                
                # Check required sections
                self.assertIn("daemon", config, "Config should have daemon section")
                self.assertIn("services", config, "Config should have services section")
                self.assertIn("monitoring", config, "Config should have monitoring section")
                
            except yaml.YAMLError as e:
                self.fail(f"Configuration file is not valid YAML: {e}")

if __name__ == '__main__':
    unittest.main()