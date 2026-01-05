from EvaluatorStage import EvaluatorStage
from EvaluatorContext import EvaluatorContext

class EvaluatorPipeline:
    """
    Context of the approximator's generation
    
    Attributes:
        context (EvaluatorContext): Parameters for the pipeline execution
        stages (list[EvaluatorStage]): Ordered list of the pipeline stages
    """
    
    context: EvaluatorContext
    stages: list[EvaluatorStage]

    def run(self) -> bool:
        """
        Main method for pipeline execution        
        """
        
        for stage in self.stages:
            if not stage.execute(self.context):
                return False
            
        return True
