from apex.context import Context
from apex.synthesis_stage.synthesis_registry import SynthesisRegistry, SynthesisStage

@SynthesisRegistry.register(predicate=lambda ctx: True, priority=0)
class SynthesisDefault(SynthesisStage):
    """
    Default synthesis stage
    """
    
    def execute(self, ctx: Context) -> bool:
        return True