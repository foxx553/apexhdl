from typing import List, Optional
from evaluator.context import Context
from evaluator.utils import Predicate
from implementation_base import ImplementationClass

class ImplementationRegistry:
    """
    Registry allowing predicate-based implementation variant retrieval

    Attributes:
        _variants (List[tuple[Predicate, ImplementationClass]]): List of all variants stored in the registry
    """

    _variants: List[tuple[Predicate, ImplementationClass]] = []
    
    @classmethod
    def register(cls, predicate: Predicate):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
        """
        def decorator(implementation_class: ImplementationClass) -> ImplementationClass:
            cls._variants.insert(0, (predicate, implementation_class))
            return implementation_class
        return decorator
    
    @classmethod
    def select(cls, ctx: Context) -> Optional[ImplementationClass]:
        """
        Implementation variant retrieval
        
        Parameters:
            ctx (Context): Context of the pipeline execution

        Returns:
            Optional[ImplementationClass]: Retrieved implementation variant
        """
        for predicate, implementation_class in cls._variants:
            if predicate(ctx):
                return implementation_class
        
        return None