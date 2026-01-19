from evaluator.context import Context
from evaluator.simulation_stage.simulation_registry import SimulationRegistry
from evaluator.simulation_stage.simulation_base import SimulationStage

@SimulationRegistry.register(predicate=lambda ctx: True, priority=0)
class SimulationDefault(SimulationStage):
    """
    Default simulation stage
    """
    
    def execute(self, ctx: Context) -> bool:
        return True