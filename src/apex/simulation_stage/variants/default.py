from apex.context import Context
from apex.simulation_stage.simulation_registry import SimulationRegistry
from apex.simulation_stage.simulation_base import SimulationStage

@SimulationRegistry.register(predicate=lambda ctx: True, priority=0)
class SimulationDefault(SimulationStage):
    """
    Default simulation stage
    """
    
    def execute(self, ctx: Context) -> bool:
        return True