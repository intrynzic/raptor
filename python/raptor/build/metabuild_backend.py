from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence

from raptor.core.log import warn


@dataclass(frozen=True)
class ToolRequirement:
    name: str
    min_ver: Optional[str] = None
    auto_install: bool = False


class MetaBuildBackend(ABC):
    """
    Base class for all Raptor meta-build backends.

    A meta-build backend is responsible for generating files
    required by the build.
    """

    name: str
    friendly_name: str

    @property
    @abstractmethod
    def tool_requirements(self) -> Sequence["ToolRequirement"]:
        warn("The meta-build backend hasn't been configured for this project.")

    @abstractmethod
    def generate(self, args: Optional[list[str]]):
        warn("The meta-build backend hasn't been configured for this project.")

    @abstractmethod
    def detect(self) -> bool:
        """
        Returns True if this backend appears to be configured for the
        repository.

        Examples:
            Premake -> premake5.lua exists
            CMake   -> CMakeLists.txt exists
            Meson   -> meson.build exists
        """
        warn("The meta-build backend hasn't been configured for this project.")
