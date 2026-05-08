"""LLM client that uses Claude via the user's Claude subscription (Claude Code SDK).

Works without an Anthropic API key. Requires the `claude` CLI to be installed
and authenticated (`claude --version` should work in the shell).
"""

import asyncio
import concurrent.futures
import json
import re
import uuid
from typing import Any, Iterator, List, Optional, Sequence

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import BaseTool

from .base_client import BaseLLMClient
from .validators import validate_model

_TOOL_CALL_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)

_TOOL_SYSTEM_INSTRUCTION = """\

## Tool Calling Instructions
When you need to call a tool, output ONLY the following JSON object on its own line — nothing else on that line:
<tool_call>{"name": "TOOL_NAME", "id": "UNIQUE_ID", "arguments": {"arg": "value"}}</tool_call>

Replace TOOL_NAME with the exact tool name, UNIQUE_ID with a random string, and fill in the arguments.
Do NOT add any text before or after the <tool_call> tag on the same line.
If you do not need a tool, respond normally in plain text.

## Available Tools
"""


def _fmt_messages(messages: List[BaseMessage], tools: List[dict]) -> tuple[str, str]:
    """Convert LangChain messages to (system_prompt, user_prompt).

    The user_prompt contains the full conversation history formatted as text.
    The system_prompt contains the original system content plus tool definitions.
    """
    system_parts: list[str] = []
    turns: list[str] = []

    for msg in messages:
        if isinstance(msg, SystemMessage):
            system_parts.append(str(msg.content))

        elif isinstance(msg, HumanMessage):
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            turns.append(f"USER:\n{content}")

        elif isinstance(msg, AIMessage):
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    tc_json = json.dumps({
                        "name": tc["name"],
                        "id": tc.get("id", str(uuid.uuid4())),
                        "arguments": tc.get("args", {}),
                    })
                    turns.append(f"ASSISTANT:\n<tool_call>{tc_json}</tool_call>")
            else:
                content = msg.content if isinstance(msg.content, str) else str(msg.content)
                turns.append(f"ASSISTANT:\n{content}")

        elif isinstance(msg, ToolMessage):
            tool_name = getattr(msg, "name", "tool")
            turns.append(f"TOOL RESULT [{tool_name}]:\n{msg.content}")

    system_text = "\n\n".join(system_parts)

    if tools:
        tool_block = _TOOL_SYSTEM_INSTRUCTION
        for tool in tools:
            fn = tool.get("function", tool)
            tool_block += f"\n### {fn['name']}\n"
            if fn.get("description"):
                tool_block += f"{fn['description']}\n"
            if "parameters" in fn:
                tool_block += f"Parameters (JSON schema):\n{json.dumps(fn['parameters'], indent=2)}\n"
        system_text += tool_block

    user_prompt = "\n\n".join(turns)
    if not user_prompt:
        user_prompt = "(begin)"
    return system_text, user_prompt


def _parse_tool_calls(text: str) -> tuple[list[dict], str]:
    """Extract structured tool calls from raw response text."""
    tool_calls = []
    for match in _TOOL_CALL_RE.finditer(text):
        try:
            data = json.loads(match.group(1))
            tool_calls.append({
                "name": data["name"],
                "id": data.get("id", str(uuid.uuid4())),
                "args": data.get("arguments", data.get("args", {})),
                "type": "tool_call",
            })
        except (json.JSONDecodeError, KeyError):
            pass
    clean = _TOOL_CALL_RE.sub("", text).strip()
    return tool_calls, clean


def _sdk_query(prompt: str, system_prompt: str, model: Optional[str]) -> str:
    """Run a single-turn query via the Claude Code SDK in a fresh event loop."""

    async def _run():
        from claude_code_sdk import AssistantMessage, ClaudeCodeOptions, TextBlock, query
        from claude_code_sdk._errors import MessageParseError

        text = ""
        opts = ClaudeCodeOptions(
            max_turns=1,
            system_prompt=system_prompt or None,
            model=model or None,
        )
        try:
            async for msg in query(prompt=prompt, options=opts):
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            text += block.text
        except MessageParseError:
            # SDK doesn't recognise all server message types (e.g. rate_limit_event).
            # Any assistant text collected before the unknown message is still usable.
            pass
        return text

    def _in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_run())
        finally:
            loop.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(_in_thread).result()


class ClaudeSubscriptionChatModel(BaseChatModel):
    """LangChain-compatible chat model using Claude via Claude subscription."""

    model: Optional[str] = None  # None → CLI uses the default model for your plan

    def bind_tools(
        self,
        tools: Sequence,
        **kwargs: Any,
    ) -> "ClaudeSubscriptionChatModel":
        from langchain_core.utils.function_calling import convert_to_openai_tool
        tool_defs = [convert_to_openai_tool(t) for t in tools]
        return self.bind(tools=tool_defs, **kwargs)  # type: ignore[return-value]

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        tools: list[dict] = kwargs.get("tools", [])
        system_prompt, user_prompt = _fmt_messages(messages, tools)

        raw = _sdk_query(user_prompt, system_prompt, self.model)

        if not raw:
            raise RuntimeError(
                "Claude subscription returned an empty response. "
                "This usually means you hit a rate limit — wait a moment and retry."
            )

        tool_calls, clean_text = _parse_tool_calls(raw)

        ai_msg = AIMessage(content=clean_text, tool_calls=tool_calls)
        return ChatResult(generations=[ChatGeneration(message=ai_msg)])

    @property
    def _llm_type(self) -> str:
        return "claude-subscription"


class ClaudeSubscriptionClient(BaseLLMClient):
    """Wraps ClaudeSubscriptionChatModel for the TradingAgents factory."""

    def get_llm(self) -> ClaudeSubscriptionChatModel:
        self.warn_if_unknown_model()
        # Pass None when the user picks the special "default" model entry.
        model = self.model if self.model != "default" else None
        return ClaudeSubscriptionChatModel(model=model)

    def validate_model(self) -> bool:
        return validate_model("claude_subscription", self.model)
