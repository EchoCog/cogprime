from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
from .aletheia import AletheiaCore
from .phenomenology import ExperienceMode, PhenomenologicalState

class PhenomenologyCore:
    """Enhanced phenomenological investigation and existential dimensions.
    
    Extends the base phenomenology implementation with deeper integration
    of Vervaeke's insights about participatory knowing and relevance realization.
    """
    
    def __init__(
        self,
        aletheia_core: AletheiaCore
    ):
        self.aletheia_core = aletheia_core
        
        self.phenomenological_state = PhenomenologicalState(
            active_modes={mode: 0.0 for mode in PhenomenologicalMode},
            existential_dimensions={dim: 0.0 for dim in ExistentialDimension},
            intentional_relations=[],
            world_disclosures=[],
            participatory_depth=0.0
        )
        
    def activate_mode(
        self,
        mode: PhenomenologicalMode,
        intensity: float = 0.5
    ) -> None:
        """Activate a phenomenological mode with aletheia integration."""
        self.phenomenological_state.active_modes[mode] = min(
            1.0,
            self.phenomenological_state.active_modes[mode] + intensity
        )
        self._update_relations()
        self._process_disclosures()
        
        # Integrate with aletheia
        if mode == PhenomenologicalMode.REFLECTIVE:
            self.aletheia_core.activate_truth_mode("aletheia", intensity * 0.8)
        elif mode == PhenomenologicalMode.EXPLORATORY:
            self.aletheia_core.engage_being_mode("dasein", intensity * 0.7)
        
    def explore_dimension(
        self,
        dimension: ExistentialDimension,
        intensity: float = 0.5
    ) -> None:
        """Explore an existential dimension with aletheia integration."""
        self.phenomenological_state.existential_dimensions[dimension] = min(
            1.0,
            self.phenomenological_state.existential_dimensions[dimension] + intensity
        )
        self._update_participatory()
        
        # Integrate with aletheia
        if dimension == ExistentialDimension.BEING:
            self.aletheia_core.engage_being_mode("being", intensity * 0.8)
        elif dimension == ExistentialDimension.PARTICIPATORY:
            self.aletheia_core.activate_truth_mode("attunement", intensity * 0.7)
        
    def _update_relations(self) -> None:
        """Update intentional relations with enhanced aletheia awareness."""
        new_relations = []
        
        # Reflective mode enhances intentionality
        if (self.phenomenological_state.active_modes[PhenomenologicalMode.REFLECTIVE] > 0.7 and
            self.phenomenological_state.existential_dimensions[ExistentialDimension.INTENTIONALITY] > 0.6):
            new_relations.append({
                "type": "noetic_enhancement",
                "source": PhenomenologicalMode.REFLECTIVE,
                "target": ExistentialDimension.INTENTIONALITY,
                "strength": 0.8,
                "aletheia_resonance": True
            })
            
        # Exploratory mode enhances world disclosure
        if (self.phenomenological_state.active_modes[PhenomenologicalMode.EXPLORATORY] > 0.6 and
            self.phenomenological_state.existential_dimensions[ExistentialDimension.WORLD_DISCLOSURE] > 0.5):
            new_relations.append({
                "type": "world_opening",
                "source": PhenomenologicalMode.EXPLORATORY,
                "target": ExistentialDimension.WORLD_DISCLOSURE,
                "strength": 0.7,
                "aletheia_resonance": True
            })
            
        self.phenomenological_state.intentional_relations = new_relations
        
    def _process_disclosures(self) -> None:
        """Process world disclosures with enhanced aletheia awareness."""
        new_disclosures = []
        
        # Check for dasein disclosure
        if self._check_dasein_conditions():
            new_disclosures.append({
                "type": "being_disclosure",
                "components": [
                    ExistentialDimension.DASEIN,
                    ExistentialDimension.BEING
                ],
                "strength": 0.8,
                "aletheia_resonance": True
            })
            
        # Check for participatory disclosure
        if self._check_participatory_conditions():
            new_disclosures.append({
                "type": "participatory_disclosure",
                "components": [
                    ExistentialDimension.PARTICIPATORY,
                    ExistentialDimension.WORLD_DISCLOSURE
                ],
                "strength": 0.7,
                "aletheia_resonance": True
            })
            
        self.phenomenological_state.world_disclosures = new_disclosures
        
    def _update_participatory(self) -> None:
        """Update participatory depth with enhanced aletheia awareness."""
        being = self.phenomenological_state.existential_dimensions[ExistentialDimension.BEING]
        dasein = self.phenomenological_state.existential_dimensions[ExistentialDimension.DASEIN]
        participatory = self.phenomenological_state.existential_dimensions[ExistentialDimension.PARTICIPATORY]
        
        # Include aletheia resonance
        aletheia_factor = (
            self.aletheia_core.aletheia_state.truth_modes["aletheia"] +
            self.aletheia_core.aletheia_state.being_modes["being"]
        ) / 2.0
        
        self.phenomenological_state.participatory_depth = (
            0.3 * being +
            0.3 * dasein +
            0.3 * participatory +
            0.1 * aletheia_factor
        )
        
    def _check_dasein_conditions(self) -> bool:
        """Check conditions for dasein disclosure with aletheia integration."""
        base_conditions = (
            self.phenomenological_state.existential_dimensions[ExistentialDimension.DASEIN] > 0.7 and
            self.phenomenological_state.existential_dimensions[ExistentialDimension.BEING] > 0.6 and
            self.phenomenological_state.active_modes[PhenomenologicalMode.REFLECTIVE] > 0.6
        )
        
        aletheia_conditions = (
            self.aletheia_core.aletheia_state.being_modes["dasein"] > 0.5 and
            self.aletheia_core.aletheia_state.truth_modes["aletheia"] > 0.5
        )
        
        return base_conditions and aletheia_conditions
        
    def _check_participatory_conditions(self) -> bool:
        """Check conditions for participatory disclosure with aletheia integration."""
        base_conditions = (
            self.phenomenological_state.existential_dimensions[ExistentialDimension.PARTICIPATORY] > 0.6 and
            self.phenomenological_state.existential_dimensions[ExistentialDimension.WORLD_DISCLOSURE] > 0.6 and
            self.phenomenological_state.active_modes[PhenomenologicalMode.EXPLORATORY] > 0.5
        )
        
        aletheia_conditions = (
            self.aletheia_core.aletheia_state.truth_modes["attunement"] > 0.5 and
            self.aletheia_core.aletheia_state.being_modes["presence"] > 0.5
        )
        
        return base_conditions and aletheia_conditions
        
    def evaluate_investigation(self) -> Dict[str, float]:
        """Evaluate the current state of phenomenological investigation."""
        active_modes = sum(
            1.0 for level in self.phenomenological_state.active_modes.values()
            if level > 0.5
        ) / len(PhenomenologicalMode)
        
        dimensions = sum(
            1.0 for level in self.phenomenological_state.existential_dimensions.values()
            if level > 0.5
        ) / len(ExistentialDimension)
        
        relations = len(self.phenomenological_state.intentional_relations) / 10.0
        disclosures = len(self.phenomenological_state.world_disclosures) / 5.0
        
        # Include aletheia resonance
        aletheia_factor = (
            sum(1.0 for level in self.aletheia_core.aletheia_state.truth_modes.values() if level > 0.5) / len(self.aletheia_core.aletheia_state.truth_modes) +
            sum(1.0 for level in self.aletheia_core.aletheia_state.being_modes.values() if level > 0.5) / len(self.aletheia_core.aletheia_state.being_modes)
        ) / 2.0
        
        return {
            "active_modes": active_modes,
            "existential_dimensions": dimensions,
            "intentional_relations": relations,
            "world_disclosures": disclosures,
            "participatory_depth": self.phenomenological_state.participatory_depth,
            "aletheia_resonance": aletheia_factor,
            "overall_investigation": (
                0.2 * active_modes +
                0.2 * dimensions +
                0.2 * relations +
                0.2 * disclosures +
                0.1 * self.phenomenological_state.participatory_depth +
                0.1 * aletheia_factor
            )
        }
        
    def get_investigation_recommendations(self) -> List[str]:
        """Get recommendations for deepening phenomenological investigation."""
        recommendations = []
        
        # Check for weak modes
        weak_modes = [
            mode for mode, level in self.phenomenological_state.active_modes.items()
            if level < 0.3
        ]
        if weak_modes:
            recommendations.append(
                f"Develop phenomenological modes: {', '.join(m.value for m in weak_modes)}"
            )
            
        # Check dimensions
        weak_dims = [
            dim for dim, level in self.phenomenological_state.existential_dimensions.items()
            if level < 0.3
        ]
        if weak_dims:
            recommendations.append(
                f"Explore existential dimensions: {', '.join(d.value for d in weak_dims)}"
            )
            
        # Check participatory depth
        if self.phenomenological_state.participatory_depth < 0.5:
            recommendations.append(
                "Deepen participatory knowing through existential investigation"
            )
            
        # Check aletheia resonance
        aletheia_factor = (
            sum(1.0 for level in self.aletheia_core.aletheia_state.truth_modes.values() if level > 0.5) / len(self.aletheia_core.aletheia_state.truth_modes) +
            sum(1.0 for level in self.aletheia_core.aletheia_state.being_modes.values() if level > 0.5) / len(self.aletheia_core.aletheia_state.being_modes)
        ) / 2.0
        
        if aletheia_factor < 0.5:
            recommendations.append(
                "Enhance aletheia resonance through truth disclosure and being engagement"
            )
            
        return recommendations 