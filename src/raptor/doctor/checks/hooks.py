import raptor.hooks.post_checkout as hook_pc
import raptor.hooks.post_merge as hook_pm
import raptor.hooks.post_rewrite as hook_pr

from raptor.core.validation import ValidationResult
from raptor.doctor.checks.check import Check


class PostCheckoutHookCheck(Check):
    type_id = "PostCheckoutHookCheck"
    name = "Git post-checkout hook"
    description = "Validates the Git post-checkout hook."

    def validate(self) -> ValidationResult:
        return hook_pc.validate()

    def fix(self) -> bool:
        hook_pc.install()
        return True


class PostMergeHookCheck(Check):
    type_id = "PostMergeHookCheck"
    name = "Git post-merge hook"
    description = "Validates the Git post-merge hook."

    def validate(self) -> ValidationResult:
        return hook_pm.validate()

    def fix(self) -> bool:
        hook_pm.install()
        return True


class PostRewriteHookCheck(Check):
    type_id = "PostRewriteHookCheck"
    name = "Git post-rewrite hook"
    description = "Validates the Git post-rewrite hook."

    def validate(self) -> ValidationResult:
        return hook_pr.validate()

    def fix(self) -> bool:
        hook_pr.install()
        return True
