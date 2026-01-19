from evaluator.context import Context
from evaluator.generation_stage.generation_registry import GenerationRegistry
from evaluator.generation_stage.generation_base import GenerationStage

@GenerationRegistry.register(predicate=lambda ctx: True, priority=0)
class GenerationDefault(GenerationStage):
    """
    Default generation stage
    """

    def execute(self, ctx: Context) -> bool:
        return True