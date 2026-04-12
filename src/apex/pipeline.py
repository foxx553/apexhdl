from apex.context import Context
from apex.generation_stage.generation_base import GenerationStage
from apex.simulation_stage.simulation_base import SimulationStage
from apex.analysis_stage.analysis_base import AnalysisStage
from apex.implementation_stage.implementation_base import ImplementationStage
from apex.generation_stage.generation_registry import GenerationRegistry
from apex.simulation_stage.simulation_registry import SimulationRegistry
from apex.analysis_stage.analysis_registry import AnalysisRegistry
from apex.implementation_stage.implementation_registry import ImplementationRegistry
from apex.generation_stage.generation_base import GenerationClass
from apex.simulation_stage.simulation_base import SimulationClass
from apex.analysis_stage.analysis_base import AnalysisClass
from apex.implementation_stage.implementation_base import ImplementationClass

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

    analysis_stage: AnalysisStage
    """Stage of circuit hardware analysis"""

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
        generation_variant: GenerationClass = GenerationRegistry.select(ctx)
        simulation_variant: SimulationClass = SimulationRegistry.select(ctx)
        analysis_variant: AnalysisClass = AnalysisRegistry.select(ctx)
        implementation_variant: ImplementationClass = ImplementationRegistry.select(ctx)

        # Instanciating these variants
        self.generation_stage = generation_variant()
        self.simulation_stage = simulation_variant()
        self.analysis_stage = analysis_variant()
        self.implementation_stage = implementation_variant()


    def run(self) -> bool:
        """
        Pipeline execution

        Returns:
            bool: Whether the pipeline execution was successful or not
        """

        self.generation_stage.execute(self.context)
        self.simulation_stage.execute(self.context)
        self.analysis_stage.execute(self.context)
        self.implementation_stage.execute(self.context)

        return True
