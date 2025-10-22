"""High-level LLM orchestration functions.

This module re-exports the LLM orchestration API from submodules.
"""

# Re-export types and dataclasses
from .llm_types import (  # noqa: F401
    DEFAULT_MODELS,
    ChatResult,
    ConversationProgressEvent,
    DiscoveryProgressEvent,
    FinalDecisionProgressEvent,
    ModelConfig,
    ProgressCallback,
    ProgressEvent,
    ReadmeFetchProgressEvent,
    ServiceSelectionProgressEvent,
    ServiceSelectionResult,
    get_model_config,
)

# Re-export high-level orchestrator
from .orchestrator import process_chat_turn  # noqa: F401

# Re-export low-level phase functions
from .phases import (  # noqa: F401
    execute_readme_requests,
    get_llm_discovery_phase,
    get_llm_final_decision,
    get_llm_service_selection,
    llm_final_decision_to_inventory_instances,
)

# Re-export commonly used functions and types from schemas
from .schemas import (  # noqa: F401
    AiAggregate,
    ChatMessage,
    ConversationHistory,
    FunctionCallType,
    JSONValue,
    MachineDescription,
    OllamaFunctionSchema,
    OpenAIFunctionSchema,
    PendingFinalDecisionState,
    PendingServiceSelectionState,
    ReadmeRequest,
    SessionState,
    SimplifiedServiceSchema,
    TagDescription,
    aggregate_ollama_function_schemas,
    aggregate_openai_function_schemas,
    create_get_readme_tool,
    create_select_service_tool,
    create_simplified_service_schemas,
)

# Re-export service functions
from .service import create_llm_model, run_llm_service  # noqa: F401

# Re-export utility functions and constants
from .utils import (  # noqa: F401
    ASSISTANT_MODE_DISCOVERY,
    ASSISTANT_MODE_FINAL,
    ASSISTANT_MODE_SELECTION,
)
