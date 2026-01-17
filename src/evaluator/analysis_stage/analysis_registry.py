from typing import List, Optional
from evaluator.context import Context
from evaluator.utils import Predicate
from analysis_base import AnalysisClass

class AnalysisRegistry:
    """
    Registry allowing predicate-based analysis variant retrieval
    """

    _variants: List[tuple[int, Predicate, AnalysisClass]] = []
    """List of all variants stored in the registry"""
    
    @classmethod
    def register(cls, predicate: Predicate, priority: int = 0):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
            priority (int): Predicate priority (higher number for higher priority)
        """
        def decorator(analysis_class: AnalysisClass) -> AnalysisClass:
            cls._variants.insert(0, (priority, predicate, analysis_class))
            cls._variants.sort(key = lambda x: x[0], reverse=True)
            return analysis_class
        return decorator
    
    @classmethod
    def select(cls, ctx: Context) -> AnalysisClass:
        """
        Analysis variant retrieval
        
        Parameters:
            ctx (Context): Context of the pipeline execution

        Returns:
            AnalysisClass: Retrieved analysis variant
        """
        for priority, predicate, analysis_class in cls._variants:
            if predicate(ctx):
                return analysis_class
        
        raise RuntimeError("No analysis variant found matching the starting context")