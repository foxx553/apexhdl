from typing import List, Optional
from evaluator.context import Context
from evaluator.utils import Predicate
from generation_base import GenerationClass

class GenerationRegistry:
    """
    Registry allowing predicate-based generation variant retrieval

    Attributes:
        _variants (List[tuple[Predicate, GenerationClass]]): List of all variants stored in the registry
    """

    _variants: List[tuple[int, Predicate, GenerationClass]] = []
    
    @classmethod
    def register(cls, predicate: Predicate, priority: int = 0):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
            priority (int): Predicate priority (higher number for higher priority)
        """
        def decorator(generation_class: GenerationClass) -> GenerationClass:
            cls._variants.append(0, (priority, predicate, generation_class))
            cls._variants.sort(key = lambda x: x[0], reverse=True)
            return generation_class
        return decorator
    
    @classmethod
    def select(cls, ctx: Context) -> GenerationClass:
        """
        Generation variant retrieval
        
        Parameters:
            ctx (Context): Context of the pipeline execution

        Returns:
            GenerationClass: Retrieved generation variant
        """
        for priority, predicate, generation_class in cls._variants:
            if predicate(ctx):
                return generation_class
        
        raise RuntimeError("No generation variant found matching the starting context")