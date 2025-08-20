"""Test for enhanced RelevanceCore with meaning crisis detection."""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from src.vervaeke.relevance_core import RelevanceCore, RelevanceMode


class TestRelevanceCoreEnhanced:
    """Test enhanced RelevanceCore with Episode 00 insights."""
    
    def setup_method(self):
        """Setup test instance."""
        self.relevance_core = RelevanceCore()
    
    def test_meaning_crisis_detection_initialization(self):
        """Test that crisis indicators are properly initialized."""
        indicators = self.relevance_core.crisis_indicators
        
        assert indicators.disconnection_level == 0.0
        assert indicators.bullshit_ratio == 0.0
        assert indicators.relevance_coherence == 1.0
        assert indicators.transformation_resistance == 0.0
        assert indicators.historical_continuity == 1.0
    
    def test_meaning_crisis_not_detected_initially(self):
        """Test that no crisis is detected in healthy state."""
        crisis_detected, severity, indicators = self.relevance_core.detect_meaning_crisis()
        
        assert not crisis_detected
        assert severity < 0.6
        assert all(value <= 0.5 for value in indicators.values())
    
    def test_bullshit_detection(self):
        """Test bullshit detection based on certainty-confidence gap."""
        # Simulate low confidence but high claimed certainty (bullshit indicator)
        query = {'claim1', 'claim2', 'claim3'}
        context = {'certainty': 0.9}  # High claimed certainty
        
        # This should result in low actual confidence due to random salience
        relevant, confidence = self.relevance_core.evaluate_relevance(query, context)
        
        # Should detect bullshit due to certainty-confidence gap
        crisis_detected, severity, indicators = self.relevance_core.detect_meaning_crisis()
        
        # Bullshit ratio should be elevated
        assert indicators['bullshit_ratio'] > 0.0
    
    def test_coherence_tracking(self):
        """Test that relevance coherence is tracked over time."""
        query = {'item1', 'item2'}
        
        # Make multiple evaluations to build history
        for i in range(5):
            context = {'test_run': i}
            self.relevance_core.evaluate_relevance(query, context)
        
        # Check that history is being tracked
        assert len(self.relevance_core.relevance_history) == 5
        
        # Coherence should be calculated
        coherence = self.relevance_core.crisis_indicators.relevance_coherence
        assert 0.0 <= coherence <= 1.0
    
    def test_crisis_intervention_suggestions(self):
        """Test that crisis intervention suggestions are provided."""
        # Force crisis indicators high to trigger suggestions
        self.relevance_core.crisis_indicators.disconnection_level = 0.8
        self.relevance_core.crisis_indicators.bullshit_ratio = 0.7
        
        suggestions = self.relevance_core.get_crisis_intervention_suggestions()
        
        assert len(suggestions) > 0
        assert any("disconnection" in suggestion.lower() for suggestion in suggestions)
        assert any("truth-seeking" in suggestion.lower() or "aletheia" in suggestion.lower() 
                  for suggestion in suggestions)
    
    def test_historical_continuity_tracking(self):
        """Test historical continuity assessment."""
        query = {'wisdom_concept'}
        
        # Context with strong tradition connection
        context_traditional = {'tradition_connection': 0.9}
        self.relevance_core.evaluate_relevance(query, context_traditional)
        
        assert self.relevance_core.crisis_indicators.historical_continuity == 0.9
        
        # Context with weak tradition connection
        context_modern = {'tradition_connection': 0.2}
        self.relevance_core.evaluate_relevance(query, context_modern)
        
        assert self.relevance_core.crisis_indicators.historical_continuity == 0.2
    
    def test_comprehensive_crisis_detection(self):
        """Test comprehensive crisis detection with multiple indicators."""
        # Simulate a comprehensive meaning crisis
        query = {'confusing_info'}
        context = {
            'certainty': 0.95,  # High claimed certainty
            'tradition_connection': 0.1  # Low historical continuity
        }
        
        # Make multiple evaluations with inconsistent results
        for i in range(10):
            self.relevance_core.evaluate_relevance(query, context)
        
        # Manually set disconnection to trigger crisis
        self.relevance_core.crisis_indicators.disconnection_level = 0.7
        
        crisis_detected, severity, indicators = self.relevance_core.detect_meaning_crisis()
        
        # Should detect crisis with multiple indicators
        assert crisis_detected
        assert severity >= 0.6
        assert indicators['bullshit_ratio'] > 0.5
        assert indicators['historical_disconnect'] > 0.5
        
        # Should provide comprehensive intervention suggestions
        suggestions = self.relevance_core.get_crisis_intervention_suggestions()
        assert len(suggestions) >= 4  # Multiple intervention types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])