from context import Context
from analysis_registry import AnalysisRegistry
from analysis_base import AnalysisStage

@AnalysisRegistry.register(predicate=lambda ctx: True, priority=0)
class AnalysisDefault(AnalysisStage):
    """
    Default analysis stage
    """
    
    def execute(self, ctx: Context) -> bool:
        return True