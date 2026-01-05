from EvaluatorStage import EvaluatorStage
from EvaluatorContext import EvaluatorContext

class EvaluatorPipeline:
    """
    Context of the approximator's generation

    Attributes:
        stages (list[EvaluatorStage]): Ordered list of the pipeline stages
    """
    
    context: EvaluatorContext
    stages: list[EvaluatorStage]

    def run(self) -> None:
        """
        Main method for pipeline execution        
        """
        
        for stage in self.stages:
            stage.execute(self.context)
