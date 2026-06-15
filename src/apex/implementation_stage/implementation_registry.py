import sys
from abc import ABC, abstractmethod
import pkgutil
import importlib
from apex.context import Context
from apex.utils import Predicate

import logging
current_logger = logging.getLogger(__name__)

class ImplementationStage(ABC):
	"""
    Abstract base class for implementation stage definition
    """
     
	def __init__(self):
		"""
		Implementation stage initialization
		"""
		self.logger = logging.getLogger(f"{self.__class__.__module__}")

	@abstractmethod
	def execute(self, ctx: Context) -> dict[str, float]:
		"""
        Main method for implementation stage execution
        
        Parameters:
            ctx (Context): Context of the current approximator implementation
			
        Returns:
            dict[str, float]: Metrics returned by the stage execution
        """
		pass

class ImplementationRegistry:
    """
    Registry allowing predicate-based implementation variant retrieval
    """

    _variants: list[tuple[int, Predicate, type[ImplementationStage]]] = []
    """list of all variants stored in the registry"""
    
    @classmethod
    def register(cls, predicate: Predicate, priority: int = 0):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
            priority (int): Predicate priority (higher number for higher priority)
        """
        def decorator(implementation_class: type[ImplementationStage]) -> type[ImplementationStage]:
            cls._variants.append((priority, predicate, implementation_class))
            return implementation_class
        return decorator
    
    @classmethod
    def select(cls, ctx: Context) -> type[ImplementationStage]:
        """
        Implementation variant retrieval
        
        Parameters:
            ctx (Context): Context of the pipeline execution

        Returns:
            type[ImplementationStage]: Retrieved implementation variant
        """
        cls._variants.sort(key = lambda x: x[0], reverse=True)
        for _, predicate, implementation_class in cls._variants:
            if predicate(ctx):
                return implementation_class
        
        current_logger.error("No implementation variant found matching the starting context...")
        sys.exit(1)
    
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