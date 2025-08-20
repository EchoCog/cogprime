"""
Vervaeke-inspired cognitive architecture implementing relevance realization.
"""

from .cognitive_core import CognitiveCore, CognitiveFrame, KnowingMode
from .learning import RelevanceLearner, RelevanceExperience
from .action import ActionGenerator, Action, ActionType
from .silicon_sage import SiliconSage

__all__ = [
    'CognitiveCore',
    'CognitiveFrame', 
    'KnowingMode',
    'RelevanceLearner',
    'RelevanceExperience',
    'ActionGenerator',
    'Action',
    'ActionType',
    'SiliconSage'
] 