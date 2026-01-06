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

    _variants: List[tuple[Predicate, GenerationClass]] = []
    
    @classmethod
    def register(cls, predicate: Predicate):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
        """
        def decorator(generation_class: GenerationClass) -> GenerationClass:
            cls._variants.insert(0, (predicate, generation_class))
            return generation_class
        return decorator
    
    @classmethod
    def select(cls, ctx: Context) -> Optional[GenerationClass]:
        """
        Generation variant retrieval
        
        Parameters:
            ctx (Context): Context of the pipeline execution

        Returns:
            Optional[GenerationClass]: Retrieved generation variant
        """
        for predicate, generation_class in cls._variants:
            if predicate(ctx):
                return generation_class
        
        return None