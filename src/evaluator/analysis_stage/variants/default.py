from context import Context
from analysis_registry import AnalysisRegistry
from analysis_base import AnalysisStage

@AnalysisRegistry.register(predicate=lambda: True, priority=0)
class AnalysisDefault(AnalysisStage):
    
    def execute(self, ctx: Context) -> bool:
        return True