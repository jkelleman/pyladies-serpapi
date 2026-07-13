# Talk Proposal: Designing Custom AI Agents for Everyday Workflows: Behind the Scenes of a Smart Assistant

## 📋 Overview
Move beyond simple prompt engineering! This talk takes you behind the scenes of building end-to-end, multi-step AI agents. We will treat daily automated workflows—such as web monitoring, personal content orchestrations, or budget/planning trackers—as structured data platform problems. We will explore how to build autonomous agents using Python, APIs, and modern embedding databases.

## 🎯 Target Audience
- Python hobbyists looking to build real-world automation scripts
- Developers wanting to understand autonomous agent loops (ReAct pattern)
- Anyone looking to save time on repetitive personal or professional workflows

## 🛠️ Key Takeaways
- **Prompt vs. Agent:** Learn the difference between static LLM prompts and autonomous agent loops.
- **Relatable Systems Design:** See how to decompose everyday workflows (like tracking prices or personal planning) into database models and tool calls.
- **Orchestration Patterns:** Best practices for robust agentic systems, including parsing structured JSON, retrying on API failures, and using embeddings.

## 🕒 Suggested Agenda (45 Minutes)
- **00:00 - 00:15 | Decomposing the Workflow:** How to approach everyday automation as a data platform problem (using real case studies).
- **00:15 - 00:35 | Code & Architecture Review:** Walking through the implementation of a smart assistant (e.g., using FastAPI, database triggers, and OpenAI/Anthropic APIs).
- **00:35 - 00:45 | Q&A & Ideation:** Brainstorming session on what the audience wants to automate next.

## 🔗 Connection to Portfolio Repositories
- [ai-content-orchestrator](https://github.com/jkelleman/ai-content-orchestrator)
- [wedding-planning-agent](https://github.com/jkelleman/wedding-planning-agent)
- [price-is-right-agent](https://github.com/jkelleman/price-is-right-agent)

---

## 🛠️ Attendee Pre-requisites & Setup Guide
- **Python 3.10+** installed on your system.
- Understanding of async Python and REST API basics (FastAPI/requests).
- An API Key from **OpenAI** or **Anthropic**.
- Install requirements: `pip install openai fastapi pydantic`
- Recommended tool: **Postman** or **curl** to test local endpoints.

## 📢 Promotion & Marketing Copy
**Meetup Description:**
Move beyond simple prompt engineering! This Friday at noon, we're going behind the scenes of **Autonomous AI Agents** in Python. Learn how to decompose daily workflows—like price tracking or personal planning—into structured database models and self-correcting agent loops (using the ReAct pattern).

**Hashtags:**
#PyLadies #Python #AIAgents #AgenticWorkflows #FastAPI #Automation #ReActPattern

## 💬 Interactive Audience Engagement Plan
- **Icebreaker Poll:** "What is the most tedious, repetitive task you do every day that you wish an AI agent could do for you?"
- **Interactive Checkpoint:** Present a scenario where an agent gets stuck in a loop (e.g., an API is down) and ask: "How should the agent handle this failure? Retry, fail gracefully, or ask for human-in-the-loop help?"

## 💻 Interactive Code Sandbox Link
- **Status:** Under development (see preparation roadmap in [README.md](./README.md)). Once configured, you can try out the agent loops with zero local setup using [GitHub Codespaces](https://github.com/features/codespaces) on the [ai-content-orchestrator](https://github.com/jkelleman/ai-content-orchestrator) repository.
