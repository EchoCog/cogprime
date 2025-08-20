"""
SiliconSage: A high-level orchestrator that composes relevance realization,
wisdom, rationality, mindset, phenomenology, and ecology components into a
single advisory interface.

This module wires together the Vervaeke-inspired cores to provide simple
methods for advising, reflecting, and optimizing a wisdom ecology.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Tuple

from .relevance_core import RelevanceCore
from .meaning_making import MeaningMaker

# Disambiguate CognitiveCore implementations
from .cognitive_core import CognitiveCore as RelevanceCognitiveCore
from .cognitive_science import CognitiveCore as FourECognitiveCore

from .rationality_core import RationalityCore
from .mindset import MindsetCore
from .wisdom import WisdomCore as WisdomCoreV1
from .phenomenology import PhenomenologyCore as SimplePhenomenologyCore
from .aletheia import AletheiaCore
from .phenomenology_core import PhenomenologyCore as EnhancedPhenomenologyCore
from .wisdom_ecology import WisdomEcology, PsychotechnologyType
from .phenomenology import ExperienceMode
from .phenomenology_core import PhenomenologicalMode


@dataclass
class SageReport:
    refined_message: str
    message_confidence: float
    wisdom_metrics: Dict[str, float]
    rationality_metrics: Dict[str, float]
    ecology_metrics: Dict[str, float]
    recommendations: List[str]


class SiliconSage:
    """
    SiliconSage composes the existing modules into a coherent advisory agent.

    Components:
    - RelevanceCore + MeaningMaker for communication refinement
    - RelevanceCognitiveCore for relevance-based cognition
    - RationalityCore + MindsetCore for rationality and cognitive styles
    - WisdomCoreV1 for wisdom evaluation and guidance
    - SimplePhenomenologyCore + AletheiaCore + EnhancedPhenomenologyCore for
      phenomenological depth and truth disclosure dynamics
    - FourECognitiveCore + WisdomEcology for 4E integration and ecology-level
      optimization
    """

    def __init__(self) -> None:
        # Core relevance and meaning
        self.relevance_core = RelevanceCore()
        self.meaning_maker = MeaningMaker(self.relevance_core)

        # Cognitive cores
        self.relevance_cognitive = RelevanceCognitiveCore()
        self.four_e_cognitive = FourECognitiveCore()

        # Rationality and mindset
        self.rationality_core = RationalityCore(self.relevance_cognitive, self.relevance_core)
        self.mindset_core = MindsetCore(self.rationality_core, self.relevance_cognitive)

        # Wisdom core
        self.wisdom_core = WisdomCoreV1(
            rationality_core=self.rationality_core,
            mindset_core=self.mindset_core,
            cognitive_core=self.relevance_cognitive,
        )

        # Phenomenology and aletheia (simple + enhanced)
        self.simple_phenomenology = SimplePhenomenologyCore()
        self.aletheia_core = AletheiaCore(self.simple_phenomenology)
        self.enhanced_phenomenology = EnhancedPhenomenologyCore(self.aletheia_core)

        # Wisdom ecology (uses 4E cognitive + simple phenomenology)
        self.wisdom_ecology = WisdomEcology(
            wisdom_core=self.wisdom_core,
            rationality_core=self.rationality_core,
            cognitive_core=self.four_e_cognitive,
            phenomenology_core=self.simple_phenomenology,
        )

    def advise(self, message: str, context: Dict[str, Any]) -> SageReport:
        """
        Provide refined communication and a multi-core evaluation with recommendations.
        """
        refined_message, msg_conf = self.meaning_maker.communicate(message, context)

        wisdom_metrics = self.wisdom_core.evaluate_wisdom()
        rationality_metrics = self.rationality_core.evaluate_rationality()
        ecology_metrics = self.wisdom_ecology.evaluate_ecology()

        recs: List[str] = []
        recs.extend(self.wisdom_core.optimize_wisdom())
        recs.extend(self.rationality_core.optimize_rationality())
        recs.extend(self.wisdom_ecology.get_optimization_recommendations())

        return SageReport(
            refined_message=refined_message,
            message_confidence=msg_conf,
            wisdom_metrics=wisdom_metrics,
            rationality_metrics=rationality_metrics,
            ecology_metrics=ecology_metrics,
            recommendations=recs,
        )

    def contemplate(self, experience: Dict[str, Any], context: Dict[str, Any]) -> None:
        """
        Update wisdom ecology and phenomenology based on a new experience.
        """
        # Activate some ecology dimensions heuristically
        self.wisdom_ecology.activate_psychotechnology(
            tech_type=PsychotechnologyType.UNDERSTANDING,
            intensity=0.4,
        )
        self.wisdom_ecology.activate_psychotechnology(
            tech_type=PsychotechnologyType.INSIGHT,
            intensity=0.3,
        )
        # Drive phenomenology with simple triggers
        self.simple_phenomenology.induce_wonder({"elements": list(experience.keys())})
        self.enhanced_phenomenology.activate_mode(
            mode=PhenomenologicalMode.REFLECTIVE,
            intensity=0.3,
        )

    def optimize(self) -> List[str]:
        """
        Return a deduplicated set of optimization recommendations across systems.
        """
        recs: List[str] = []
        recs.extend(self.wisdom_core.optimize_wisdom())
        recs.extend(self.rationality_core.optimize_rationality())
        recs.extend(self.wisdom_ecology.get_optimization_recommendations())
        # Deduplicate preserving order
        seen = set()
        unique_recs: List[str] = []
        for r in recs:
            if r not in seen:
                seen.add(r)
                unique_recs.append(r)
        return unique_recs

