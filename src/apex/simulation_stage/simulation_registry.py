from abc import ABC, abstractmethod
import pkgutil
import importlib
from apex.context import Context
from apex.utils import Predicate

class SimulationStage(ABC):
	"""
    Abstract base class for simulation stage definition
    """

	@abstractmethod
	def execute(self, ctx: Context) -> bool:
		"""
        Main method for simulation stage execution
        
        Parameters:
            ctx (Context): Context of the current approximator simulation
			
        Returns:
            bool: Whether the stage execution was successful or not
        """
		pass

class SimulationRegistry:
    """
    Registry allowing predicate-based simulation variant retrieval
    """

    _variants: list[tuple[int, Predicate, type[SimulationStage]]] = []
    """list of all variants stored in the registry"""
    
    @classmethod
    def register(cls, predicate: Predicate, priority: int = 0):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
            priority (int): Predicate priority (higher number for higher priority)
        """
        def decorator(simulation_class: type[SimulationStage]) -> type[SimulationStage]:
            cls._variants.append((priority, predicate, simulation_class))
            return simulation_class
        return decorator
    
    @classmethod
    def select(cls, ctx: Context) -> type[SimulationStage]:
        """
        Simulation variant retrieval
        
        Parameters:
            ctx (Context): Context of the pipeline execution

        Returns:
            type[SimulationStage]: Retrieved simulation variant
        """
        cls._variants.sort(key = lambda x: x[0], reverse=True)
        for _, predicate, simulation_class in cls._variants:
            if predicate(ctx):
                return simulation_class
        
        raise RuntimeError("No simulation variant found matching the starting context")
    
    @classmethod
    def load_variants(cls):
        """
        Dynamic import of all variants in ./variants subfolder
        """
        import apex.simulation_stage.variants as variants_pkg
        for _, module_name, _ in pkgutil.walk_packages(
            variants_pkg.__path__, 
            variants_pkg.__name__ + "."
        ):
            importlib.import_module(module_name)