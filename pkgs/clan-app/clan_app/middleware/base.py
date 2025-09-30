from abc import ABC, abstractmethod
from contextlib import AbstractContextManager, ExitStack
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from clan_app.api.api_bridge import ApiBridge, BackendRequest


@dataclass
class MiddlewareContext:
    request: "BackendRequest"
    bridge: "ApiBridge"
    exit_stack: ExitStack
    original_traceback: list[str]


class MiddlewareError(Exception):
    """Exception that preserves original calling context."""

    def __init__(
        self, message: str, original_frames: list[str], original_error: Exception
    ) -> None:
        # Store just the original error message for API responses
        super().__init__(str(original_error))
        self.method_message = message
        self.original_frames = original_frames
        self.original_error = original_error

    def __str__(self) -> str:
        # For traceback display, show in proper Python traceback order (oldest to newest)
        original_context = "".join(self.original_frames)
        return f"Traceback (most recent call last):\n{original_context.rstrip()}\nMethodExecutionError: {self.original_error}"


@dataclass(frozen=True)
class Middleware(ABC):
    """Abstract base class for middleware components."""

    @abstractmethod
    def process(self, context: MiddlewareContext) -> None:
        """Process the request through this middleware."""

    def register_context_manager(
        self,
        context: MiddlewareContext,
        cm: AbstractContextManager[Any],
    ) -> Any:
        """Register a context manager with the exit stack."""
        return context.exit_stack.enter_context(cm)
