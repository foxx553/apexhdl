from typing import Type
from abc import ABC, abstractmethod
from apex.context import Context

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