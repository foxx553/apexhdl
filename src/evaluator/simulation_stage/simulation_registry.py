from typing import List, Optional
import pkgutil
import importlib
from evaluator.context import Context
from evaluator.utils import Predicate
from evaluator.simulation_stage.simulation_base import SimulationClass

class SimulationRegistry:
    """
    Registry allowing predicate-based simulation variant retrieval
    """

    _variants: List[tuple[int, Predicate, SimulationClass]] = []
    """List of all variants stored in the registry"""
    
    @classmethod
    def register(cls, predicate: Predicate, priority: int = 0):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
            priority (int): Predicate priority (higher number for higher priority)
        """
        def decorator(simulation_class: SimulationClass) -> SimulationClass:
            cls._variants.insert(0, (priority, predicate, simulation_class))
            cls._variants.sort(key = lambda x: x[0], reverse=True)
            return simulation_class
        return decorator
    
    @classmethod
    def select(cls, ctx: Context) -> SimulationClass:
        """
        Simulation variant retrieval
        
        Parameters:
            ctx (Context): Context of the pipeline execution

        Returns:
            SimulationClass: Retrieved simulation variant
        """
        for priority, predicate, simulation_class in cls._variants:
            if predicate(ctx):
                return simulation_class
        
        raise RuntimeError("No simulation variant found matching the starting context")
    
    @classmethod
    def load_variants(cls):
        """
        Dynamic import of all variants in ./variants subfolder
        """
        import evaluator.simulation_stage.variants as variants_pkg
        for loader, module_name, is_pkg in pkgutil.walk_packages(
            variants_pkg.__path__, 
            variants_pkg.__name__ + "."
        ):
            importlib.import_module(module_name)