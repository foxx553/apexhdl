from apex.context import Context
from apex.analysis_stage.analysis_registry import AnalysisRegistry
from apex.analysis_stage.analysis_base import AnalysisStage

@AnalysisRegistry.register(predicate=lambda ctx: True, priority=0)
class AnalysisDefault(AnalysisStage):
    """
    Default analysis stage
    """
    
    def execute(self, ctx: Context) -> bool:
        return True