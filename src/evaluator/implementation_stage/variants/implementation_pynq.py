from context import Context
from implementation_registry import ImplementationRegistry
from implementation_base import ImplementationStage

@ImplementationRegistry.register(predicate=lambda: True, priority=0)
class ImplementationPynq(ImplementationStage):
    
    def execute(self, ctx: Context) -> bool:
        return True