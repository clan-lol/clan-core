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


@dataclass(frozen=True)
class Middleware(ABC):
    """Abstract base class for middleware components."""

    @abstractmethod
    def process(self, context: MiddlewareContext) -> None:
        """Process the request through this middleware."""

    def register_context_manager(
        self, context: MiddlewareContext, cm: AbstractContextManager[Any]
    ) -> Any:
        """Register a context manager with the exit stack."""
        return context.exit_stack.enter_context(cm)
