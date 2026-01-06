from typing import List, Optional
from evaluator.context import Context
from evaluator.utils import Predicate
from analysis_base import AnalysisClass

class AnalysisRegistry:
    """
    Registry allowing predicate-based analysis variant retrieval

    Attributes:
        _variants (List[tuple[Predicate, AnalysisClass]]): List of all variants stored in the registry
    """

    _variants: List[tuple[Predicate, AnalysisClass]] = []
    
    @classmethod
    def register(cls, predicate: Predicate):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
        """
        def decorator(analysis_class: AnalysisClass) -> AnalysisClass:
            cls._variants.insert(0, (predicate, analysis_class))
            return analysis_class
        return decorator
    
    @classmethod
    def select(cls, ctx: Context) -> Optional[AnalysisClass]:
        """
        Analysis variant retrieval
        
        Parameters:
            ctx (Context): Context of the pipeline execution

        Returns:
            Optional[AnalysisClass]: Retrieved analysis variant
        """
        for predicate, analysis_class in cls._variants:
            if predicate(ctx):
                return analysis_class
        
        return None