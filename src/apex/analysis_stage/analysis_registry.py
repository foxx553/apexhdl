from typing import Type
from abc import ABC, abstractmethod
import pkgutil
import importlib
from apex.context import Context
from apex.utils import Predicate

class AnalysisStage(ABC):
	"""
    Abstract base class for analysis stage definition
    """

	@abstractmethod
	def execute(self, ctx: Context) -> bool:
		"""
        Main method for analysis stage execution
        
        Parameters:
            ctx (Context): Context of the current approximator analysis
			
        Returns:
            bool: Whether the stage execution was successful or not
        """
		pass

AnalysisClass = Type[AnalysisStage]
"""
Alias for a boolean check on pipeline context
"""

class AnalysisRegistry:
    """
    Registry allowing predicate-based analysis variant retrieval
    """

    _variants: list[tuple[int, Predicate, AnalysisClass]] = []
    """list of all variants stored in the registry"""
    
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
        for _, predicate, analysis_class in cls._variants:
            if predicate(ctx):
                return analysis_class
        
        raise RuntimeError("No analysis variant found matching the starting context")
    
    @classmethod
    def load_variants(cls):
        """
        Dynamic import of all variants in ./variants subfolder
        """
        import apex.analysis_stage.variants as variants_pkg
        for _, module_name, _ in pkgutil.walk_packages(
            variants_pkg.__path__, 
            variants_pkg.__name__ + "."
        ):
            importlib.import_module(module_name)