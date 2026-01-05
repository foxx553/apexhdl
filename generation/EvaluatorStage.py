from abc import ABC, abstractmethod

from EvaluatorContext import EvaluatorContext

class EvaluatorStage(ABC):
	"""
    Abstract base class for pipeline stage definition
    """

	@abstractmethod
	def execute(self, context: EvaluatorContext) -> None:
		"""
        Main method for the pipeline stage
        
        Args:
            context (EvaluatorContext): Context of the current approximator generation
        """
		pass