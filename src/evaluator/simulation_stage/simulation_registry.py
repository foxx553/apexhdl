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

    _variants: List[tuple[Predicate, SimulationClass]] = []
    
    @classmethod
    def register(cls, predicate: Predicate):
        """
        Decorator for variant registration

        Parameters:
            predicate (Predicate): Condition to be met, checked on the execution context
        """
        def decorator(simulation_class: SimulationClass) -> SimulationClass:
            cls._variants.insert(0, (predicate, simulation_class))
            return simulation_class
        return decorator
    
    @classmethod
    def select(cls, ctx: Context) -> Optional[SimulationClass]:
        """
        Simulation variant retrieval
        
        Parameters:
            ctx (Context): Context of the pipeline execution

        Returns:
            Optional[SimulationClass]: Retrieved simulation variant
        """
        for predicate, simulation_class in cls._variants:
            if predicate(ctx):
                return simulation_class
        
        return None