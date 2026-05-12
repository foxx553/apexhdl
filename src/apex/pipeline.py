from apex.context import Context
from apex.generation_stage.generation_registry import GenerationRegistry, GenerationStage
from apex.simulation_stage.simulation_registry import SimulationRegistry, SimulationStage
from apex.synthesis_stage.synthesis_registry import SynthesisRegistry, SynthesisStage
from apex.implementation_stage.implementation_registry import ImplementationRegistry, ImplementationStage

class Pipeline:
    """
    Pipeline class for managing circuit generation lifecycle
    """

    context: Context
    """Context of pipeline execution"""

    generation_stage: GenerationStage
    """Stage of circuit generation"""

    simulation_stage: SimulationStage
    """Stage of circuit simulation"""

    synthesis_stage: SynthesisStage
    """Stage of circuit hardware synthesis"""

    implementation_stage: ImplementationStage
    """Stage of circuit test on target"""


    def __init__(self, ctx: Context):
        """
        Pipeline initialization
        
        Parameters:
            ctx (Context): Context of the new pipeline
        """

        # Init the context
        self.context = ctx

        # Selecting the correct variants
        generation_variant: type[GenerationStage] = GenerationRegistry.select(ctx)
        simulation_variant: type[SimulationStage] = SimulationRegistry.select(ctx)
        synthesis_variant: type[SynthesisStage] = SynthesisRegistry.select(ctx)
        implementation_variant: type[ImplementationStage] = ImplementationRegistry.select(ctx)

        # Instanciating these variants
        self.generation_stage = generation_variant()
        self.simulation_stage = simulation_variant()
        self.synthesis_stage = synthesis_variant()
        self.implementation_stage = implementation_variant()


    def run(self) -> dict[str, float]:
        """
        Pipeline execution

        Returns:
            dict[str, float]: Metrics extracted during the pipeline execution
        """

        return (
            self.generation_stage.execute(self.context) |
            self.simulation_stage.execute(self.context) |
            self.synthesis_stage.execute(self.context) |
            self.implementation_stage.execute(self.context)
        )
