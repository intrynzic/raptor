from raptor.config.defines import CONFIG_FILE_NAME
from raptor.core.log import critical
from functools import cached_property
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional


class PathsConfig(BaseModel):
    docs_dir: Optional[Path] = None
    temp_dir: Optional[Path] = None
    tools_dir: Optional[Path] = None

class SetupTask(BaseModel):
    name: str
    min_version: str

class SetupConfig(BaseModel):
    headless: bool
    environment: list[SetupTask] = Field(default_factory = list)

    def has(self, name: str) -> bool:
        return name in self._env_map

    def get(self, name: str) -> SetupTask:
        res = self._env_map.get(name)
        return SetupTask(name = name, min_version = "0.0.0") if res is None else res

    @property
    def git(self) -> bool:
        return self.has("git")

    @property
    def git_hooks(self) -> bool:
        return self.has("git-hooks")

    @property
    def vulkan(self) -> bool:
        return self.has("vulkan")

    @property
    def dotnet(self) -> bool:
        return self.has("dotnet")

    @property
    def doxygen(self) -> bool:
        return self.has("doxygen")

    @cached_property
    def _env_map(self) -> dict[str, SetupTask]:
        return {task.name: task for task in self.environment}

class CheckConfig(BaseModel):
    name: str
    enabled: bool = True

class DoctorConfig(BaseModel):
    checks: list[CheckConfig] = Field(default_factory = list)

    def has(self, name: str) -> bool:
        return name in self._env_map

    def get(self, name: str) -> CheckConfig | None:
        return self._env_map.get(name)

    @cached_property
    def _env_map(self) -> dict[str, CheckConfig]:
        return {task.name: task for task in self.checks}

class PremakeConfig(BaseModel):
    default_action: str
    supported_actions: list[str] = Field(default_factory = list)

    def model_post_init(self, context):
        if self.default_action not in self.supported_actions:
            critical(f"{CONFIG_FILE_NAME}: 'default_action' must be in 'supported_actions'!")

class ProjectConfig(BaseModel):
    dir: Path
    language: str
    arch: str
    build_mode: str

class WorkspaceConfig(BaseModel):
    dir: Path
    name: str
    configs: list[str] = Field(default_factory = list)
    default_config: str
    default_arch: str
    executable_projects: dict[str, ProjectConfig] = Field(default_factory = dict)

    def model_post_init(self, context):
        if self.default_config not in self.configs:
            critical(f"{CONFIG_FILE_NAME}: 'default_config' must be in 'configs'!")

class CleanTarget(BaseModel):
    search_dirs: list[Path] = Field(default_factory = list)
    delete_dirs: list[Path] = Field(default_factory = list)
    files: list[Path] = Field(default_factory = list)
    file_exts: list[str] = Field(default_factory = list)
    depth: str

    def model_post_init(self, context):
        if self.depth not in ["shallow", "recursive"]:
            critical(f"Unknown clean target depth setting '{self.depth}'!")

class CleanConfig(BaseModel):
    targets: dict[str, CleanTarget] = Field(default_factory = dict)

class RaptorConfig(BaseModel):
    version: str
    paths: PathsConfig
    setup: SetupConfig
    doctor: DoctorConfig
    premake: PremakeConfig
    workspace: WorkspaceConfig
    clean: CleanConfig

class RaptorConfigFile(BaseModel):
    raptor: RaptorConfig
