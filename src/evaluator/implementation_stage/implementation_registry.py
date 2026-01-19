from typing import List, Optional
import pkgutil
import importlib
from evaluator.context import Context
from evaluator.utils import Predicate
from evaluator.implementation_stage.implementation_base import ImplementationClass

class ImplementationRegistry:
    """
    Registry allowing predicate-based implementation variant retrieval
    """

    _variants: List[tuple[int, Predicate, ImplementationClass]] = []
    """List of all variants stored in the registry"""
    
    @classmethod
    def register(cls, predicate: Predicate, priority: int = 0):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
            priority (int): Predicate priority (higher number for higher priority)
        """
        def decorator(implementation_class: ImplementationClass) -> ImplementationClass:
            cls._variants.insert(0, (priority, predicate, implementation_class))
            cls._variants.sort(key = lambda x: x[0], reverse=True)
            return implementation_class
        return decorator
    
    @classmethod
    def select(cls, ctx: Context) -> ImplementationClass:
        """
        Implementation variant retrieval
        
        Parameters:
            ctx (Context): Context of the pipeline execution

        Returns:
            ImplementationClass: Retrieved implementation variant
        """
        for priority, predicate, implementation_class in cls._variants:
            if predicate(ctx):
                return implementation_class
        
        raise RuntimeError("No implementation variant found matching the starting context")
    
    @classmethod
    def load_variants(cls):
        """
        Dynamic import of all variants in ./variants subfolder
        """
        import evaluator.implementation_stage.variants as variants_pkg
        for loader, module_name, is_pkg in pkgutil.walk_packages(
            variants_pkg.__path__, 
            variants_pkg.__name__ + "."
        ):
            importlib.import_module(module_name)