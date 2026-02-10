from typing import Type
from abc import ABC, abstractmethod
from apex.context import Context

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