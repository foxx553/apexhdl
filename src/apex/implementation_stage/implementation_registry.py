from typing import Type
from abc import ABC, abstractmethod
import pkgutil
import importlib
from apex.context import Context
from apex.utils import Predicate

class ImplementationStage(ABC):
	"""
    Abstract base class for implementation stage definition
    """

	@abstractmethod
	def execute(self, ctx: Context) -> bool:
		"""
        Main method for implementation stage execution
        
        Parameters:
            ctx (Context): Context of the current approximator implementation
			
        Returns:
            bool: Whether the stage execution was successful or not
        """
		pass

ImplementationClass = Type[ImplementationStage]
"""
Alias for a boolean check on pipeline context
"""

class ImplementationRegistry:
    """
    Registry allowing predicate-based implementation variant retrieval
    """

    _variants: list[tuple[int, Predicate, ImplementationClass]] = []
    """list of all variants stored in the registry"""
    
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
        for _, predicate, implementation_class in cls._variants:
            if predicate(ctx):
                return implementation_class
        
        raise RuntimeError("No implementation variant found matching the starting context")
    
    @classmethod
    def load_variants(cls):
        """
        Dynamic import of all variants in ./variants subfolder
        """
        import apex.implementation_stage.variants as variants_pkg
        for _, module_name, _ in pkgutil.walk_packages(
            variants_pkg.__path__, 
            variants_pkg.__name__ + "."
        ):
            importlib.import_module(module_name)