from typing import Type
from abc import ABC, abstractmethod
from evaluator.context import Context

class GenerationStage(ABC):
	"""
    Abstract base class for generation stage definition
    """

	@abstractmethod
	def execute(self, ctx: Context) -> bool:
		"""
        Main method for generation stage execution
        
        Parameters:
            ctx (Context): Context of the current approximator generation
			
        Returns:
            bool: Whether the stage execution was successful or not
        """
		pass

GenerationClass = Type[GenerationStage]
"""
Alias for a boolean check on pipeline context
"""