from typing import List, Optional
import pkgutil
import importlib
from apex.context import Context
from apex.utils import Predicate
from apex.analysis_stage.analysis_base import AnalysisClass

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
    
    @classmethod
    def load_variants(cls):
        """
        Dynamic import of all variants in ./variants subfolder
        """
        import apex.analysis_stage.variants as variants_pkg
        for loader, module_name, is_pkg in pkgutil.walk_packages(
            variants_pkg.__path__, 
            variants_pkg.__name__ + "."
        ):
            importlib.import_module(module_name)