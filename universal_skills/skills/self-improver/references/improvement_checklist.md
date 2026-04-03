# Agentic Software Improvement Checklist

Use this checklist to brainstorm enhancements and optimizations for any agentic repository or tool.

## 🏗️ Architecture & Orchestration
- [ ] **Graph-Based Logic**: For tasks with more than 3 steps or complex decision trees, migrate from "Flat" agents to `pydantic-graph`.
- [ ] **State Persistence**: Implement checkpointing so the agent can resume from failures or long pauses.
- [ ] **Parallel Execution**: Identify bottleneck steps (e.g., multiple search vectors) that can run concurrently.
- [ ] **Domain Isolation**: Split monolithic agents into specialized subagents with clear handoff protocols.

## 🧠 Prompt Management & DX
- [ ] **Externalized Prompts**: Move all system prompts into `prompts/*.md` for easier iteration and version control.
- [ ] **Dynamic Variable Injection**: Use a `prompt_builder` pattern instead of hardcoded f-strings.
- [ ] **Structured Tool Output**: Ensure all tools return JSON or Pydantic models with clear field descriptions.
- [ ] **Streaming UI**: Implement SSE (Server-Sent Events) for real-time thought/action visibility.

## 🏎️ Performance & Scalability
- [ ] **Prompt Caching**: Use model provider features (e.g. Anthropic/Google caching) for long system prompts.
- [ ] **Vector Optimization**: Switch from linear search to HNSW indices (e.g. via `llama-index` or `chromadb`).
- [ ] **Lazy Loading**: Import heavy dependencies only when the specific tool is called.
- [ ] **Tool Filtering**: Dynamically restrict visible tools based on the current graph state to reduce token usage.

## 🛡️ Security & Reliability
- [ ] **Tool Guards**: Implement runtime validation for destructive tools (e.g. `rm`, `overwrite`).
- [ ] **Environment Isolation**: Ensure `.env` is never committed and sensitive keys are accessed via `Settings` objects.
- [ ] **Automated Retries**: Wrap network-dependent tools in exponential backoff logic.
- [ ] **Truthfulness Verification**: Add a "Verifier" node to the graph to double-check LLM outputs against ground truth data.

## 🎨 Design & Aesthetics (Brainstorming)
- [ ] **Visual Cohesion**: Use a curated color palette (Helsinki Dark, Aurora Night) instead of browser defaults.
- [ ] **Interactive Elements**: Add hover states, loaders, and micro-interactions for every tool trigger.
- [ ] **Modern Typography**: Replace generic sans-serif with high-quality fonts (Inter, Roboto Mono, Outfit).
- [ ] **Glassmorphism**: Use `backdrop-filter: blur(10px)` and semi-transparent borders for a premium feel.
