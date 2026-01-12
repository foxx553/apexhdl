from context import Context
from generation_registry import GenerationRegistry
from generation_base import GenerationStage

@GenerationRegistry.register(predicate=lambda: True, priority=0)
class GenerationRom(GenerationStage):
    
    def execute(self, ctx: Context) -> bool:
        return True