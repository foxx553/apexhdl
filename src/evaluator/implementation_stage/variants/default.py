from context import Context
from implementation_registry import ImplementationRegistry
from implementation_base import ImplementationStage

@ImplementationRegistry.register(predicate=lambda ctx: True, priority=0)
class ImplementationDefault(ImplementationStage):
    """
    Default implementation stage
    """
    
    def execute(self, ctx: Context) -> bool:
        return True