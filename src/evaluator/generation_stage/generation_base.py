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
        """
		pass

GenerationClass = Type[GenerationStage]
"""
Alias for a boolean check on pipeline context
"""