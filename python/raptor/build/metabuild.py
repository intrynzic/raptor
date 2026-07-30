from __future__ import annotations

from typing import Optional

from raptor.build.backends import default, premake
from raptor.build.metabuild_backend import MetaBuildBackend
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
