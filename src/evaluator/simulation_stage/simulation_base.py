from typing import Type
from abc import ABC, abstractmethod
from evaluator.context import Context

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
        """
		pass

SimulationClass = Type[SimulationStage]
"""
Alias for a boolean check on pipeline context
"""