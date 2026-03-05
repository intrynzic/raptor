from raptor.core.log import info
from raptor.core.process import run_ex
from raptor.core.validation import ValidationResult, Severity
from raptor.doctor.checks.check import Check
import re


class VulkanDriverCheck(Check):
    type_id = "VulkanDriverCheck"
    name = "Vulkan GPU Drivers"
    description = "Validates the Vulkan capabilities of the installed GPU drivers."

    def validate(self) -> ValidationResult:
        result = run_ex(["vulkanInfo"])
        if result is None or (result.returncode != 0):
            return ValidationResult(
                valid = False,
                severity = Severity.ERROR,
                message = "Failed to run vulkanInfo.exe! It is likely that the Vulkan Runtime is corrupt."
            )

        result_stdout = result.stdout.strip()
        if "GPU id" not in result_stdout:
            return ValidationResult(
                valid = False,
                severity = Severity.ERROR,
                message = "No Vulkan-compatible GPU detected!"
            )

        info("Vulkan-compatible GPUs:")

        # Extract GPU name
        pattern = r"GPU id = (\d+) \((.+)\)"
        matches = sorted(set(re.findall(pattern, result_stdout)), key = lambda x: int(x[0]))
        for gpu_id, name in matches:
            info(f"Device {gpu_id}: {name}")

        return ValidationResult(
            valid = True,
            severity = Severity.NONE
        )
