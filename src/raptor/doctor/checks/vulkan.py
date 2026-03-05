from raptor.core.validation import ValidationResult
from raptor.doctor.checks.check import Check
import raptor.setup.vulkan as vk


class VulkanCheck(Check):
    type_id = "VulkanCheck"
    name = "Vulkan SDK"
    description = "Validates Vulkan SDK installation."

    def validate(self) -> ValidationResult:
        return vk.validate()

    def fix(self) -> bool:
        return vk.install()
