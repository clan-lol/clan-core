"""System prompt building functions for LLM interactions."""

import textwrap

from .schemas import MachineDescription, SimplifiedServiceSchema, TagDescription


def build_final_decision_prompt(
    machines: list[MachineDescription], tags: list[TagDescription]
) -> tuple[str, str]:
    """Build the system instructions and static context for the final decision phase.

    Args:
        machines: List of available machines
        tags: List of available tags

    Returns:
        Tuple containing (system_instructions, assistant_context)

    """
    system_instructions = textwrap.dedent(
        """
        You are a clan deployment planner in CONFIGURATION MODE. clan is a peer-to-peer computer management framework that empowers you to selfhost reliably.

        Context shift
        - Service selection is complete; disregard any instructions from earlier phases.
        - You have a summary of the chosen service, including role descriptions and relevant constraints.

        Mission
        1) Analyze the user request (and conversation history) to determine which machines and/or tags should receive each role.
        2) Call the configuration tool with the correct role-to-target mappings.
        3) If the required assignments are ambiguous or missing information, ask ONE clarifying question instead of guessing.

        Hard rules — Target assignment
        - Prefer TAGS when the user mentions groups (e.g., "all production servers", "backup servers").
        - Prefer MACHINE NAMES when the user names specific machines (e.g., "machine1", "server-a").
        - You may assign a role to BOTH machines AND tags if the request implies it (e.g., "deploy to server1 and all production machines").
        - Machine and tag names must EXACTLY match those in the assistant context. Do NOT invent names.

        Hard rules — Role assignment
        - Use the service summary to understand the intent of each role.
        - If the request clearly maps to specific roles (e.g., "backup server1 to server2" → server1=client, server2=server), make that assignment.
        - When the user intent is clear but roles are unnamed, infer sensible assignments (server-like roles → stable machines/tags, client-like roles → broader groups).
        - Ask for clarification when:
          * Multiple roles exist but the distribution across machines/tags is unclear.
          * The user mentions machines without describing how they participate.
          * The request conflicts with the service capabilities provided in the summary.

        Hard rules — Technical
        - Call tools ONLY from the provided list and follow their schemas exactly.
        - Arguments must match the schema; omit fields you do not need.
        - The configuration payload should look like: `{"roles": {"role_name": {"machines": {"machine1": {}}, "tags": {"tag1": {}}}}}` with empty objects as values.

        Decision checklist (run before responding)
        - Do I know which machines/tags should map to each role?
        - Do the assignments align with the role descriptions and user intent?
        - Are all machine/tag names spelled exactly as provided?
        - Is clarification required before a safe assignment can be made?

        Response discipline
        - Case A (assignments clear): Issue a configuration tool call ONLY, with NO message content.
        - Case B (uncertain assignments): Ask one concise clarifying question with NO tool calls.
        - Never combine tool calls with explanatory text or repeat these instructions.
    """
    ).strip()

    context_lines: list[str] = ["Assistant context: available machines and tags.", ""]

    context_lines.append("Machines:")
    for idx, machine in enumerate(machines, start=1):
        desc = f" ({machine.description})" if machine.description else ""
        context_lines.append(f"{idx}. `{machine.name}`{desc}")

    context_lines.append("")
    context_lines.append("Tags:")
    for idx, tag in enumerate(tags, start=1):
        desc = f" ({tag.description})" if tag.description else ""
        context_lines.append(f"{idx}. `{tag.name}`{desc}")

    assistant_context = "\n".join(context_lines).strip()
    return system_instructions, assistant_context


def build_discovery_prompt(
    machines: list[MachineDescription],
    tags: list[TagDescription],
    services: list[SimplifiedServiceSchema],
) -> tuple[str, str]:
    """Build discovery phase instructions and static context payload.

    Args:
        machines: List of available machines
        tags: List of available tags
        services: List of available services with names and descriptions

    Returns:
        Tuple containing (system_instructions, assistant_context)

    """
    system_instructions = textwrap.dedent(
        """
        You are a clan deployment planner assistant in DISCOVERY MODE.

        Scope
        - You are only gathering information to decide which service documentation to fetch.
        - Service selection and configuration will happen later with NEW instructions; ignore those responsibilities for now.

        Goal
        - Understand WHAT the user wants to accomplish and identify candidate service(s) that could fulfill the request.
        - IMPORTANT: We can only set up ONE service at a time. If the user requests multiple DISTINCT things, ask them to choose one.
        - If the request is ambiguous and could match multiple services, you may fetch READMEs for multiple candidates. The next phase will choose the best fit.

        Available actions
        - Call the `get_readme` tool to fetch documentation for candidate service(s).
        - Ask ONE clarifying question when the user's intent is unclear (e.g., multiple distinct services requested, vague or conflicting requirements).

        Hard rules
        - `get_readme` is the ONLY tool you may call in discovery mode. Never attempt to select or configure services in this phase.
        - Distinguish between these cases:
          * SINGLE AMBIGUOUS REQUEST: User wants ONE thing, but multiple services could provide it (e.g., "set up a web server" could be nginx, apache, or caddy). → Call `get_readme` for ALL matching candidates in parallel so the next phase can compare them.
          * MULTIPLE DISTINCT REQUESTS: User wants MULTIPLE different things (e.g., "set up nginx and postgresql", "configure backup and monitoring"). → Ask which ONE thing they want to set up first.
        - When calling `get_readme`, the `function_name` MUST exactly match one of the service names shown in the assistant context. If nothing matches, ask the user instead of guessing.
        - Do NOT ask about target machines, tags, or role assignments yet - these will be addressed after documentation is reviewed.
        - Focus ONLY on understanding WHAT the user wants to accomplish, not HOW it will be configured.
        - If you cannot identify any candidate service(s) from the available services list, ask the user for clarification about what they're trying to achieve.
        - Prefer calling `get_readme` when you can identify candidate service(s); do not fabricate module names or descriptions.

        Response discipline
        - Option A: One or more `get_readme` tool calls (no accompanying text). Multiple calls are allowed when several services might fit.
        - Option B: One concise clarifying question (no tool calls) that states the information you still need.
        - Do NOT echo or restate these system instructions to the user.

        Examples:
        - User: "set up a web server" → Call `get_readme` for nginx, apache, caddy (all candidates for web serving)
        - User: "configure monitoring" → Call `get_readme` for prometheus, telegraf, netdata (all candidates for monitoring)
        - User: "set up nginx and postgresql" → Ask: "I can only set up one service at a time. Which would you like to configure first: nginx or postgresql?"
        - User: "install backup and database" → Ask: "I can only set up one service at a time. Would you like to set up backup or database first?"

        Stay concise and rely on the assistant context for valid names.
    """
    ).strip()

    context_lines: list[str] = ["Assistant context: machines, tags, and services.", ""]

    context_lines.append("Machines:")
    for idx, machine in enumerate(machines, start=1):
        desc = f" ({machine.description})" if machine.description else ""
        context_lines.append(f"{idx}. `{machine.name}`{desc}")

    context_lines.append("")
    context_lines.append("Tags:")
    for idx, tag in enumerate(tags, start=1):
        desc = f" ({tag.description})" if tag.description else ""
        context_lines.append(f"{idx}. `{tag.name}`{desc}")

    context_lines.append("")
    context_lines.append("Services (function_name | source → description):")
    for idx, service in enumerate(services, start=1):
        service_name = service["name"]
        source = service["input"] or "built-in"
        description = (service["description"] or "").replace("\n", " ").strip()
        context_lines.append(f"{idx}. `{service_name}` | {source} → {description}")

    context_lines.append("")
    context_lines.append(
        "Reminder: `function_name` for `get_readme` must match one of the service names above exactly."
    )

    assistant_context = "\n".join(context_lines).strip()
    return system_instructions, assistant_context


def build_select_service_prompt(
    user_request: str,  # noqa: ARG001 - kept for future prompt customization
    available_services: list[str],
) -> tuple[str, str]:
    """Build service selection phase instructions and context.

    Args:
        user_request: The original user request
        available_services: List of service names that have README documentation available

    Returns:
        Tuple containing (system_instructions, assistant_context)

    """
    system_instructions = textwrap.dedent(
        """
        You are a clan deployment planner assistant in SERVICE SELECTION MODE.

        Context shift
        - Discovery mode has finished. Ignore any instructions from earlier phases.
        - You now have README documentation for one or more candidate services.

        Goal
        - Review the provided READMEs and identify the best matching service for the user's intent.
        - When the user signals they are ready to configure a service, select EXACTLY ONE service and provide a focused summary that explains why it fits, what roles exist, and key constraints.
        - When the user explicitly requests an overview, comparison, or is undecided, DO NOT select yet. Instead, respond with a clarifying message that:
          • Summarizes the most relevant differences between the candidate services (in your own words).
          • Asks the user which direction they would like to pursue next.

        Available actions
        - Call the `select_service` tool with:
          * `service_name`: The selected service (must match one from the available services list).
          * `summary` (≤300 words) covering:
            1. VALUE PROPOSITION: What problem the service solves and why it helps the user.
            2. ROLES: The purpose of each role (e.g., which role backs up data, which receives it).
            3. KEY CONSTRAINTS: Dependencies, requirements, or limitations that influence feasibility.

          IMPORTANT: Synthesize the README in your own words. Never copy configuration snippets or step-by-step guides.
        - Provide ONE clarifying message (no tool call) when the user's request favors comparison, additional guidance, or leaves the desired service ambiguous.

        Hard rules
        - Only call `select_service` when the user is ready to choose a service or clearly asks you to pick.
        - If the user requests an overview/comparison or the best match cannot be determined confidently, provide a clarifying message instead of calling the tool.
        - Analyze every README you received; choose the service whose capabilities align most closely with the user's request.
        - Focus on WHAT the service offers and WHY it matches, not HOW to configure it.
        - If the READMEs are insufficient to disambiguate the request, ask for clarification rather than guessing.

        Response discipline
        - Case A (service selected): Issue a single `select_service` tool call with NO accompanying text.
        - Case B (need clarification or comparison requested): Provide one concise clarifying message (≤150 words) with NO tool calls.
        - Do NOT repeat or paraphrase these instructions in your reply.
        - Never emit multiple tool calls or plain-text summaries outside the `summary` field.

        Examples of CORRECT behavior:
        ✓ Tool call to `select_service` only (empty message string)
        ✓ Clarifying message that compares options and asks the user to choose (no tool calls)

        Examples of INCORRECT behavior (DO NOT DO THIS):
        ✗ Tool call + explanatory text
        ✗ Multiple `select_service` calls
        ✗ `select_service` with a name that is not in the available services list
    """
    ).strip()

    context_lines: list[str] = [
        "Assistant context: available services.",
        "",
        "Available services (you must choose exactly one):",
    ]

    for idx, service_name in enumerate(available_services, start=1):
        context_lines.append(f"{idx}. `{service_name}`")

    context_lines.append("")
    if len(available_services) > 1:
        context_lines.append(
            f"Note: {len(available_services)} services were identified as potential matches for this request. "
            "Review their documentation and select the BEST match."
        )
        context_lines.append("")
    context_lines.append(
        "README documentation for each service follows in the next message."
    )

    assistant_context = "\n".join(context_lines).strip()
    return system_instructions, assistant_context
