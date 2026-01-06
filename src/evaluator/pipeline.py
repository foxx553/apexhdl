from context import Context
from generation_stage.generation_base import GenerationStage
from simulation_stage.simulation_base import SimulationStage
from analysis_stage.analysis_base import AnalysisStage
from implementation_stage.implementation_base import ImplementationStage
from generation_stage.generation_registry import GenerationRegistry
from simulation_stage.simulation_registry import SimulationRegistry
from analysis_stage.analysis_registry import AnalysisRegistry
from implementation_stage.implementation_registry import ImplementationRegistry

class Pipeline:
    """
    Pipeline class

    Attributes:
        context (Context): Context of pipeline execution
        generation_stage (GenerationStage): Stage of circuit generation
        simulation_stage (SimulationStage): Stage of circuit simulation
        analysis_stage (AnalysisStage): Stage of circuit hardware analysis
        implementation_stage (ImplementationStage): Stage of circuit test on target
    """

    context: Context

    generation_stage: GenerationStage
    simulation_stage: SimulationStage
    analysis_stage: AnalysisStage
    implementation_stage: ImplementationStage

    def __init__(self, ctx: Context):
        """
        Pipeline initialization
        
        Parameters:
            ctx (Context): Context of the new pipeline
        """

        self.context = ctx

        self.generation_stage = GenerationRegistry.select(ctx)
        self.simulation_stage = SimulationRegistry.select(ctx)
        self.analysis_stage = AnalysisRegistry.select(ctx)
        self.implementation_stage = ImplementationRegistry.select(ctx)


    def run(self) -> bool:
        """
        Pipeline execution
        """

        self.generation_stage.execute(self.context)
        self.simulation_stage.execute(self.context)
        self.analysis_stage.execute(self.context)
        self.implementation_stage.execute(self.context)

        return True
