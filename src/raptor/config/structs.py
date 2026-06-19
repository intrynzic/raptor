from functools import cached_property
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from raptor.config.defines import CONFIG_FILE_NAME
from raptor.core.log import critical, warn


class PathsConfig(BaseModel):
    docs_dir: Optional[Path] = None
    tools_dir: Optional[Path] = None


class SetupTask(BaseModel):
    name: str
    min_version: str


class SetupConfig(BaseModel):
    headless: bool
    environment: list[SetupTask] = Field(default_factory=list)

    def has(self, name: str) -> bool:
        return name in self._env_map

    def get(self, name: str) -> SetupTask:
        res = self._env_map.get(name)
        return SetupTask(name=name, min_version="0.0.0") if res is None else res

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
    checks: list[CheckConfig] = Field(default_factory=list)

    def has(self, name: str) -> bool:
        return name in self._env_map

    def get(self, name: str) -> CheckConfig | None:
        return self._env_map.get(name)

    @cached_property
    def _env_map(self) -> dict[str, CheckConfig]:
        return {task.name: task for task in self.checks}


class PremakeConfig(BaseModel):
    default_action: str
    supported_actions: list[str] = Field(default_factory=list)

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
    configs: list[str] = Field(default_factory=list)
    default_config: str
    default_arch: str
    executable_projects: dict[str, ProjectConfig] = Field(default_factory=dict)

    def model_post_init(self, context):
        if self.default_config not in self.configs:
            critical(f"{CONFIG_FILE_NAME}: 'default_config' must be in 'configs'!")


class CleanTarget(BaseModel):
    search_dirs: list[Path] = Field(default_factory=list)
    delete_dirs: list[Path] = Field(default_factory=list)
    files: list[Path] = Field(default_factory=list)
    file_exts: list[str] = Field(default_factory=list)
    depth: str

    def model_post_init(self, context):
        if self.depth not in ["shallow", "recursive"]:
            critical(f"Unknown clean target depth setting '{self.depth}'!")


class CleanConfig(BaseModel):
    targets: dict[str, CleanTarget] = Field(default_factory=dict)


class Task(BaseModel):
    description: Optional[str] = None
    command: Optional[str] = None
    args: list[str] = Field(default_factory=list)
    cwd: Optional[str] = None
    depends_on: list[str] = Field(default_factory=list)


class RaptorConfig(BaseModel):
    version: str
    paths: PathsConfig
    setup: SetupConfig
    doctor: DoctorConfig
    premake: PremakeConfig
    workspace: WorkspaceConfig
    clean: CleanConfig
    tasks: dict[str, Task] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_tasks(self):
        # Validate task structure
        # A task is empty if both the 'command' and 'depends_on' fields are empty
        for task_name, task in self.tasks.items():
            if not task.description:
                warn(f"Task '{task_name}' does not have a description.")

            if not task.command and not task.depends_on:
                critical(f"Task '{task_name}' is empty. A task must define either a command or at least one dependency.")
                return self

        # Validate dependencies exist
        task_names = set(self.tasks)
        for task_name, task in self.tasks.items():
            for dependency in task.depends_on:
                if dependency not in task_names:
                    critical(f"Task '{task_name}' depends on an undefined task '{dependency}'.")
                    return self

        # Detect cycles using DFS
        visited: set[str] = set()
        visiting: set[str] = set()

        def dfs(task_name: str, path: list[str]):
            if task_name in visiting:
                cycle_start = path.index(task_name)
                cycle = path[cycle_start:] + [task_name]
                critical(f"Task dependency cycle detected: {' -> '.join(cycle)}")
                return self

            if task_name in visited:
                return self

            visiting.add(task_name)
            path.append(task_name)

            for dependency in self.tasks[task_name].depends_on:
                dfs(dependency, path)

            path.pop()
            visiting.remove(task_name)
            visited.add(task_name)

        for task_name in self.tasks:
            dfs(task_name, [])

        return self


class RaptorConfigFile(BaseModel):
    raptor: RaptorConfig
