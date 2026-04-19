from abc import ABC, abstractmethod
import pkgutil
import importlib
from apex.context import Context
from apex.utils import Predicate

class SynthesisStage(ABC):
	"""
    Abstract base class for synthesis stage definition
    """

	@abstractmethod
	def execute(self, ctx: Context) -> bool:
		"""
        Main method for synthesis stage execution
        
        Parameters:
            ctx (Context): Context of the current approximator synthesis
			
        Returns:
            bool: Whether the stage execution was successful or not
        """
		pass

class SynthesisRegistry:
    """
    Registry allowing predicate-based synthesis variant retrieval
    """

    _variants: list[tuple[int, Predicate, SynthesisStage]] = []
    """list of all variants stored in the registry"""
    
    @classmethod
    def register(cls, predicate: Predicate, priority: int = 0):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
            priority (int): Predicate priority (higher number for higher priority)
        """
        def decorator(synthesis_class: SynthesisStage) -> SynthesisStage:
            cls._variants.insert(0, (priority, predicate, synthesis_class))
            cls._variants.sort(key = lambda x: x[0], reverse=True)
            return synthesis_class
        return decorator
    
    @classmethod
    def select(cls, ctx: Context) -> SynthesisStage:
        """
        Synthesis variant retrieval
        
        Parameters:
            ctx (Context): Context of the pipeline execution

        Returns:
            SynthesisStage: Retrieved synthesis variant
        """
        for _, predicate, synthesis_class in cls._variants:
            if predicate(ctx):
                return synthesis_class
        
        raise RuntimeError("No synthesis variant found matching the starting context")
    
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