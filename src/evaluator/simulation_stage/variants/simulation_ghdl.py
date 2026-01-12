from context import Context
from simulation_registry import SimulationRegistry
from simulation_base import SimulationStage

@SimulationRegistry.register(predicate=lambda: True, priority=0)
class SimulationGhdl(SimulationStage):
    
    def execute(self, ctx: Context) -> bool:
        return True