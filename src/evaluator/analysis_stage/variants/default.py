from evaluator.context import Context
from evaluator.analysis_stage.analysis_registry import AnalysisRegistry
from evaluator.analysis_stage.analysis_base import AnalysisStage

@AnalysisRegistry.register(predicate=lambda ctx: True, priority=0)
class AnalysisDefault(AnalysisStage):
    """
    Default analysis stage
    """
    
    def execute(self, ctx: Context) -> bool:
        return True