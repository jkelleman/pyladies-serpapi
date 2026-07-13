# Talk Proposal: Building Custom AI Assistants with the Model Context Protocol (MCP) and FastMCP

## 📋 Overview
The Model Context Protocol (MCP) is an open-source standard that enables developers to build secure, two-way connections between AI models (like Claude) and data sources/tools. In this talk, we’ll demystify MCP and show how to use the fast-growing `FastMCP` framework in Python to build your own custom AI assistants that can read local files, fetch real-time APIs, and query databases.

## 🎯 Target Audience
- Python Developers curious about AI integration
- Data Scientists and Software Engineers looking to build customized LLM workflows
- Members interested in the next generation of AI tooling

## 🛠️ Key Takeaways
- **What is MCP?:** Understand the client-server architecture of the Model Context Protocol.
- **FastMCP Framework:** Learn how to declare tools, resources, and prompts in a few lines of Python.
- **Live Implementation:** Watch a live demo connecting a local dataset/API directly to an AI agent.
- **Security & Sandboxing:** How to run MCP servers securely in local or cloud environments.

## 🕒 Suggested Agenda (45 Minutes)
- **00:00 - 00:15 | Intro to MCP:** The problem MCP solves (bridging the gap between LLMs and tools) and the architecture overview.
- **00:15 - 00:35 | Live Coding Lab:** Creating a custom Python MCP server using `FastMCP` that wraps a public API or local database.
- **00:35 - 00:45 | Q&A & Wrap-Up:** Live troubleshooting, community ideas, and open discussion.

## 🔗 Connection to Portfolio Repositories
- [semantic-metrics-modeling-assistant](https://github.com/jkelleman/semantic-metrics-modeling-assistant)
- [ai-assisted-insights-agent](https://github.com/jkelleman/ai-assisted-insights-agent)

---

## 🛠️ Attendee Pre-requisites & Setup Guide
- **Python 3.10+** installed on your system.
- Basic familiarity with Python and decorators.
- An API Key from **Anthropic** or **OpenAI** (optional, but recommended for testing with Claude Desktop).
- Install `uv` (recommended fast package manager): `pip install uv` or via standalone installer.
- Recommended text editor: **VS Code** with the Python extension.

## 📢 Promotion & Marketing Copy
**Meetup Description:**
Ready to give your AI assistants superpowers? Join us this Friday at noon for a hands-on exploration of the **Model Context Protocol (MCP)** and **FastMCP**! We'll show you how to securely connect local data sources, APIs, and tools to LLMs in just a few lines of Python.

**Hashtags:**
#PyLadies #Python #ModelContextProtocol #FastMCP #AIAssistants #OpenSource

## 💬 Interactive Audience Engagement Plan
- **Icebreaker Poll:** "How many of you have built custom tools or APIs for LLMs before? (None / Some / I do this daily!)"
- **Interactive Checkpoint:** Pause after declaring the first tool to ask the audience: "What real-world database or API in your daily work would you want to wrap in an MCP server next?"

## 💻 Interactive Code Sandbox Link
- **Status:** Under development (see preparation roadmap in [README.md](./README.md)). Once configured, you can launch a pre-configured development container with FastMCP pre-installed using [GitHub Codespaces](https://github.com/features/codespaces) on the companion repository [semantic-metrics-modeling-assistant](https://github.com/jkelleman/semantic-metrics-modeling-assistant).
