from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, Optional
from packaging.version import Version

from raptor.build.metabuild_backend import MetaBuildBackend
from raptor.build.backends import default, premake
from raptor.config.loader import CONFIG


def generate(args: Optional[list[str]]):
    generator: MetaBuildBackend
    match CONFIG.metabuild.generator.lower():
        case "premake":
            generator = premake.Premake()

        case _:
            generator = default.DefaultBackend()

    # TODO: Should we do a detect here?
    generator.generate(args)

