import sys
from abc import ABC, abstractmethod
import pkgutil
import importlib
from apex.context import Context
from apex.utils import Predicate

import logging
current_logger = logging.getLogger(__name__)

class SynthesisStage(ABC):
	"""
    Abstract base class for synthesis stage definition
    """
     
	def __init__(self):
		"""
		Synthesis stage initialization
		"""
		self.logger = logging.getLogger(f"{self.__class__.__module__}")

	@abstractmethod
	def execute(self, ctx: Context) -> dict[str, float]:
		"""
        Main method for synthesis stage execution
        
        Parameters:
            ctx (Context): Context of the current approximator synthesis
			
        Returns:
            dict[str, float]: Metrics returned by the stage execution
        """
		pass

class SynthesisRegistry:
    """
    Registry allowing predicate-based synthesis variant retrieval
    """

    _variants: list[tuple[int, Predicate, type[SynthesisStage]]] = []
    """list of all variants stored in the registry"""
    
    @classmethod
    def register(cls, predicate: Predicate, priority: int = 0):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
            priority (int): Predicate priority (higher number for higher priority)
        """
        def decorator(synthesis_class: type[SynthesisStage]) -> type[SynthesisStage]:
            cls._variants.append((priority, predicate, synthesis_class))
            return synthesis_class
        return decorator
    
    @classmethod
    def select(cls, ctx: Context) -> type[SynthesisStage]:
        """
        Synthesis variant retrieval
        
        Parameters:
            ctx (Context): Context of the pipeline execution

        Returns:
            type[SynthesisStage]: Retrieved synthesis variant
        """
        cls._variants.sort(key = lambda x: x[0], reverse=True)
        for _, predicate, synthesis_class in cls._variants:
            if predicate(ctx):
                return synthesis_class
        
        current_logger.error("No synthesis variant found matching the starting context...")
        sys.exit(1)
    
    @classmethod
    def load_variants(cls):
        """
        Dynamic import of all variants in ./variants subfolder
        """
        import apex.synthesis_stage.variants as variants_pkg
        for _, module_name, _ in pkgutil.walk_packages(
            variants_pkg.__path__, 
            variants_pkg.__name__ + "."
        ):
            importlib.import_module(module_name)