from typing import List, Optional
from evaluator.context import Context
from evaluator.utils import Predicate
from simulation_base import SimulationClass

class SimulationRegistry:
    """
    Registry allowing predicate-based simulation variant retrieval

    Attributes:
        _variants (List[tuple[Predicate, SimulationClass]]): List of all variants stored in the registry
    """

    _variants: List[tuple[int, Predicate, SimulationClass]] = []
    
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