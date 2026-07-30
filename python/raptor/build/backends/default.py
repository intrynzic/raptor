from typing import Sequence
from raptor.build.metabuild_backend import ToolRequirement, MetaBuildBackend


class DefaultBackend(MetaBuildBackend):
    name = "default"
    friendly_name = "DefaultBackend"

    @property
    def tool_requirements(self) -> Sequence[ToolRequirement]:
        return super().tool_requirements


    def generate(self, args: list[str] | None):
        return super().generate(args)


    def detect(self) -> bool:
        return super().detect()
