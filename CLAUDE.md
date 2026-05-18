# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install (editable, for development)
pip install -e .

# Run CLI
tradingagents
python -m cli.main

# Run all tests
pytest

# Run a single test file
pytest tests/test_ticker_symbol_handling.py -v

# Run only unit tests (no external APIs)
pytest -m unit

# Run a quick propagation from Python
python main.py
```

## Architecture Overview

TradingAgents is a **LangGraph-based multi-agent pipeline** that produces buy/sell/hold decisions for a ticker on a given date. The pipeline is orchestrated by `TradingAgentsGraph` (`tradingagents/graph/trading_graph.py`).

### Pipeline stages (in order)

1. **Analyst Team** — four parallel agents (market, social, news, fundamentals) each call data tools and write reports. Configured by `selected_analysts` in `TradingAgentsGraph.__init__`.
2. **Research Manager** — structured-output agent that synthesises analyst reports.
3. **Researcher Debate** — Bull and Bear researchers debate via `InvestDebateState`; rounds controlled by `max_debate_rounds`.
4. **Trader** — reads debate output and produces an investment plan.
5. **Risk Management Debate** — three debators (aggressive, conservative, neutral) run via `RiskDebateState`; rounds controlled by `max_risk_discuss_rounds`.
6. **Portfolio Manager** — makes the final `final_trade_decision` from the risk debate and injects past-run memory context.

The shared graph state type is `AgentState` (`tradingagents/agents/utils/agent_states.py`), which extends LangGraph's `MessagesState`.

### Key data-flow abstractions

**Data routing** — `tradingagents/dataflows/interface.py` is the single dispatch layer. Agent tool functions (defined in `tradingagents/agents/utils/`) call `route_to_vendor(method, ...)` which resolves to the configured vendor (yfinance, alpha_vantage, etc.) based on `config["data_vendors"]` and `config["tool_vendors"]`. Tool-level config overrides category-level config.

**Asset types** — `tradingagents/dataflows/asset_detection.py` auto-detects `"stock"`, `"crypto"`, or `"b3"` from the ticker string. Crypto tickers are normalised to `SYMBOL-USD`; B3 tickers gain a `.SA` suffix. The `asset_type` field propagates through `AgentState` so agents can adapt their prompts.

**LLM clients** — `tradingagents/llm_clients/factory.py` is the entry point. All OpenAI-compatible providers (xai, deepseek, qwen, glm, ollama, openrouter) share `OpenAIClient`. The `claude_subscription` provider (`ClaudeSubscriptionClient`) uses the Claude Code SDK with no API key required.

**Memory log** — `tradingagents/agents/utils/memory.py`. After each run, the decision is appended as a pending entry to `~/.tradingagents/memory/trading_memory.md`. On the next same-ticker run, returns are fetched and a reflection is generated; the resolved entries and cross-ticker lessons are injected into the Portfolio Manager prompt via `past_context` in `AgentState`.

**Checkpointing** — opt-in via `config["checkpoint_enabled"] = True` or `--checkpoint` CLI flag. Uses LangGraph's `SqliteSaver`; one DB per ticker at `~/.tradingagents/cache/checkpoints/<TICKER>.db`.

### Configuration

All tuneable knobs live in `tradingagents/default_config.py`. Key fields:

| Field | Purpose |
|---|---|
| `llm_provider` | `openai`, `anthropic`, `google`, `xai`, `deepseek`, `qwen`, `glm`, `ollama`, `openrouter`, `azure`, `claude_subscription` |
| `deep_think_llm` / `quick_think_llm` | Model names for reasoning-heavy vs. fast nodes |
| `data_vendors` | Per-category vendor selection (`yfinance`, `alpha_vantage`, `crypto_yfinance`, `b3_yfinance`) |
| `tool_vendors` | Per-tool overrides; takes precedence over `data_vendors` |
| `max_debate_rounds` / `max_risk_discuss_rounds` | How many rounds each debate runs |
| `output_language` | Language for analyst reports and final decision (internal debate stays in English) |
| `checkpoint_enabled` | Enable LangGraph checkpoint/resume |

### Adding a new data vendor

1. Add implementation module in `tradingagents/dataflows/`.
2. Register it in `VENDOR_METHODS` in `tradingagents/dataflows/interface.py`.
3. Add a `data_vendors` key in `DEFAULT_CONFIG` if it represents a new category.

### Adding a new LLM provider

1. Subclass `BaseLLMClient` (`tradingagents/llm_clients/base_client.py`).
2. Register it in `create_llm_client` in `tradingagents/llm_clients/factory.py`.
3. Add model entries to `tradingagents/llm_clients/model_catalog.py`.

## Test markers

Tests use three markers defined in `pyproject.toml`:
- `unit` — fast, no network, no real API keys
- `integration` — requires live external services
- `smoke` — quick sanity checks

`conftest.py` auto-fills all API key env vars with `"placeholder"` so test collection never fails due to missing keys, and provides a `mock_llm_client` fixture.
