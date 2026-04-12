from typing import Optional
import pkgutil
import importlib
from apex.context import Context
from apex.utils import Predicate
from apex.generation_stage.generation_base import GenerationClass

class GenerationRegistry:
    """
    Registry allowing predicate-based generation variant retrieval
    """

    _variants: list[tuple[int, Predicate, GenerationClass]] = []
    """list of all variants stored in the registry"""
    
    @classmethod
    def register(cls, predicate: Predicate, priority: int = 0):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
            priority (int): Predicate priority (higher number for higher priority)
        """
        def decorator(generation_class: GenerationClass) -> GenerationClass:
            cls._variants.insert(0, (priority, predicate, generation_class))
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
    
    @classmethod
    def load_variants(cls):
        """
        Dynamic import of all variants in ./variants subfolder
        """
        import apex.generation_stage.variants as variants_pkg
        for loader, module_name, is_pkg in pkgutil.walk_packages(
            variants_pkg.__path__, 
            variants_pkg.__name__ + "."
        ):
            importlib.import_module(module_name)