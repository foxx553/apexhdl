from apex.context import Context
from apex.generation_stage.generation_registry import GenerationRegistry
from apex.generation_stage.generation_base import GenerationStage

@GenerationRegistry.register(predicate=lambda ctx: True, priority=0)
class GenerationDefault(GenerationStage):
    """
    Default generation stage
    """

    def execute(self, ctx: Context) -> bool:
        return True