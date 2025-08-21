from enum import Enum
from typing import Dict, List, Set, Tuple, Optional
import numpy as np
from dataclasses import dataclass

class RelevanceMode(Enum):
    """Different modes of relevance realization"""
    SELECTIVE_ATTENTION = "selective_attention"  # Bottom-up salience
    WORKING_MEMORY = "working_memory"  # Active maintenance
    PROBLEM_SPACE = "problem_space"  # Search space navigation
    SIDE_EFFECTS = "side_effects"  # Action consequences
    LONG_TERM_MEMORY = "long_term_memory"  # Organization & access

@dataclass
class MeaningCrisisIndicators:
    """Indicators of meaning crisis as defined in Episode 00"""
    disconnection_level: float  # Self, others, world, future disconnection
    bullshit_ratio: float  # Proportion of low-quality information
    relevance_coherence: float  # Consistency of relevance judgments
    transformation_resistance: float  # Resistance to cognitive change
    historical_continuity: float  # Connection to wisdom traditions

class RelevanceCore:
    """Core relevance realization system that implements Vervaeke's framework.
    
    This system coordinates multiple interacting relevance modes to enable
    intelligent behavior through dynamic self-organization of salience landscapes.
    
    Enhanced with meaning crisis detection based on Episode 00 analysis.
    """
    
    def __init__(self):
        # Salience weights for different modes
        self.mode_weights: Dict[RelevanceMode, float] = {
            mode: 1.0 for mode in RelevanceMode
        }
        
        # Current active contents
        self.active_contents: Dict[RelevanceMode, Set] = {
            mode: set() for mode in RelevanceMode
        }
        
        # Salience thresholds for filtering
        self.thresholds: Dict[RelevanceMode, float] = {
            mode: 0.5 for mode in RelevanceMode
        }
        
        # Interaction weights between modes
        self.interaction_weights = np.ones((len(RelevanceMode), len(RelevanceMode)))
        
        # Meaning crisis detection state
        self.crisis_indicators = MeaningCrisisIndicators(
            disconnection_level=0.0,
            bullshit_ratio=0.0,
            relevance_coherence=1.0,
            transformation_resistance=0.0,
            historical_continuity=1.0
        )
        
        # Historical patterns for stability analysis
        self.relevance_history: List[float] = []
        self.coherence_window_size = 10
        
    def update_salience(self, mode: RelevanceMode, contents: Set, 
                       context: Optional[Dict] = None) -> Set:
        """Update salience weights for given contents in a mode.
        
        Args:
            mode: The relevance mode to update
            contents: Set of items to evaluate
            context: Optional contextual information
            
        Returns:
            Set of items above salience threshold
        """
        # Get base salience for contents
        salience = self._compute_base_salience(contents, context)
        
        # Modulate by mode interactions
        for other_mode in RelevanceMode:
            if other_mode != mode:
                mode_idx = list(RelevanceMode).index(mode)
                other_idx = list(RelevanceMode).index(other_mode)
                interaction_weight = self.interaction_weights[mode_idx, other_idx]
                other_contents = self.active_contents[other_mode]
                salience = self._modulate_salience(
                    salience, other_contents, interaction_weight
                )
                
        # Filter by threshold
        threshold = self.thresholds[mode]
        salient_items = {
            item for item, weight in salience.items() 
            if weight >= threshold
        }
        
        # Update active contents
        self.active_contents[mode] = salient_items
        
        return salient_items
    
    def _compute_base_salience(self, contents: Set, 
                             context: Optional[Dict]) -> Dict:
        """Compute base salience weights for contents."""
        # Placeholder for more sophisticated salience computation
        return {item: np.random.random() for item in contents}
        
    def _modulate_salience(self, salience: Dict, other_contents: Set,
                          interaction_weight: float) -> Dict:
        """Modulate salience based on contents in other modes."""
        # Placeholder for more sophisticated interaction
        return {
            k: v * interaction_weight 
            for k, v in salience.items()
        }
        
    def restructure_salience(self, mode: RelevanceMode,
                           new_context: Dict) -> None:
        """Dynamically restructure salience landscape based on new context.
        
        This implements the insight/reframing mechanism described by Vervaeke.
        """
        # Update thresholds based on context
        self.thresholds[mode] *= new_context.get('threshold_mod', 1.0)
        
        # Update interaction weights
        for other_mode in RelevanceMode:
            if other_mode != mode:
                mode_idx = list(RelevanceMode).index(mode)
                other_idx = list(RelevanceMode).index(other_mode)
                self.interaction_weights[mode_idx, other_idx] *= \
                    new_context.get('interaction_mod', 1.0)
                    
        # Re-evaluate active contents with new parameters
        self.update_salience(mode, self.active_contents[mode], new_context)

    def evaluate_relevance(self, query: Set, context: Dict) -> Tuple[Set, float]:
        """Evaluate relevance of query items in current context.
        
        Returns both relevant items and confidence score.
        """
        relevant_items = set()
        total_confidence = 0.0
        
        # Check relevance across all modes
        for mode in RelevanceMode:
            # Update salience landscape
            salient = self.update_salience(mode, query, context)
            
            # Accumulate results
            relevant_items.update(salient)
            total_confidence += len(salient) / len(query)
            
        # Normalize confidence
        confidence = total_confidence / len(RelevanceMode)
        
        # Update meaning crisis indicators
        self._update_crisis_indicators(confidence, context)
        
        return relevant_items, confidence
    
    def _update_crisis_indicators(self, confidence: float, context: Dict) -> None:
        """Update meaning crisis indicators based on Episode 00 framework."""
        # Track relevance coherence over time
        self.relevance_history.append(confidence)
        if len(self.relevance_history) > self.coherence_window_size:
            self.relevance_history.pop(0)
            
        # Calculate coherence as stability of relevance judgments
        if len(self.relevance_history) > 1:
            coherence_variance = np.var(self.relevance_history)
            self.crisis_indicators.relevance_coherence = max(0.0, 1.0 - coherence_variance)
        
        # Detect bullshit based on low-confidence, high-certainty claims
        claimed_certainty = context.get('certainty', 0.5)
        actual_confidence = confidence
        certainty_gap = abs(claimed_certainty - actual_confidence)
        self.crisis_indicators.bullshit_ratio = min(1.0, certainty_gap * 2.0)
        
        # Assess disconnection based on lack of cross-modal relevance
        mode_activations = [len(contents) for contents in self.active_contents.values()]
        if mode_activations:
            activation_variance = np.var(mode_activations) / (np.mean(mode_activations) + 1e-6)
            self.crisis_indicators.disconnection_level = min(1.0, activation_variance)
        
        # Historical continuity based on context connection to tradition
        tradition_markers = context.get('tradition_connection', 0.5)
        self.crisis_indicators.historical_continuity = tradition_markers
        
    def detect_meaning_crisis(self) -> Tuple[bool, float, Dict[str, float]]:
        """Detect meaning crisis based on Episode 00 indicators.
        
        Returns:
            - Crisis detected (bool)
            - Overall crisis severity (0-1)
            - Individual indicator scores
        """
        indicators = {
            'disconnection': self.crisis_indicators.disconnection_level,
            'bullshit_ratio': self.crisis_indicators.bullshit_ratio,
            'coherence_loss': 1.0 - self.crisis_indicators.relevance_coherence,
            'historical_disconnect': 1.0 - self.crisis_indicators.historical_continuity
        }
        
        # Weighted crisis score (based on Episode 00 emphasis)
        weights = {
            'disconnection': 0.3,
            'bullshit_ratio': 0.3,
            'coherence_loss': 0.25,
            'historical_disconnect': 0.15
        }
        
        crisis_score = sum(indicators[key] * weights[key] for key in indicators)
        crisis_detected = crisis_score > 0.6  # Threshold based on severity
        
        return crisis_detected, crisis_score, indicators
    
    def get_crisis_intervention_suggestions(self) -> List[str]:
        """Suggest interventions based on Episode 00 framework."""
        crisis_detected, severity, indicators = self.detect_meaning_crisis()
        suggestions = []
        
        if not crisis_detected:
            return ["Relevance realization functioning normally"]
            
        if indicators['disconnection'] > 0.5:
            suggestions.append("Enhance cross-modal integration to reduce disconnection")
            suggestions.append("Strengthen self-other-world-future connection patterns")
            
        if indicators['bullshit_ratio'] > 0.5:
            suggestions.append("Activate truth-seeking (Aletheia) processes")
            suggestions.append("Implement rigorous rational reflection protocols")
            
        if indicators['coherence_loss'] > 0.5:
            suggestions.append("Stabilize relevance judgment patterns")
            suggestions.append("Engage in collaborative investigation processes")
            
        if indicators['historical_disconnect'] > 0.5:
            suggestions.append("Integrate wisdom traditions and historical resources")
            suggestions.append("Activate psychotechnology integration protocols")
            
        return suggestions 