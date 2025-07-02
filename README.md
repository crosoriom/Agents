# A Showcase of AI Agent Architectures

This repository serves as a showcase of different AI agent architectures, designed for academical and demonstrative purposes. It contains two distinct projects, each built with a different philosophy and technology stack, to illustrate various approaches to building intelligent, autonomous systems.

1.  **Project 1: The Python AI Shopping Agent** - A self-learning agent built from scratch in Python that demonstrates persistent memory and dynamic tool use.
2.  **Project 2: The "Concierge" n8n WhatsApp Assistant** - A low-code agent built in n8n that demonstrates complex API orchestration and multi-modal interactions through a simple chat interface.

---

## 1. Python AI Shopping Agent

This agent is a custom-coded, self-improving system designed to find the best products based on user queries. Its core concept is **persistent learning**; the agent not only acts on the world but learns from its actions to make better decisions in the future.

### Concept & Philosophy

The agent's intelligence is built upon a **Read -> Plan -> Act & Learn** cycle.

*   **Read:** It consults its internal Knowledge Base (a SQLite database) to understand its environment, including available stores, their communication methods (API vs. Scraping), and their historical performance (latency, success rate).
*   **Plan:** Based on this data, the LLM core (Google Gemini) formulates a strategy, prioritizing the most efficient and reliable tools first.
*   **Act & Learn:** When a tool is executed, it **automatically reports its own performance** back to the Knowledge Base. A successful and fast API call reinforces that method's priority, while a slow or failed attempt will demote it, making the agent adapt over time.

### Demonstrated Concepts

This project is an excellent case study for:

*   **Persistent State in Agents:** How an agent can maintain and benefit from long-term memory.
*   **Dynamic Tool Use:** An LLM choosing the right tool for a job based on empirical data.
*   **Graceful Fallbacks:** The agent's ability to try a less optimal method (scraping) if a better one (API) fails.
*   **Dependency Injection:** The correct way to manage and share a single database connection across different modules.
*   **Autonomous Systems:** Building a system that improves its own performance without human intervention.

---

## 2. "Concierge" n8n WhatsApp Assistant

This agent demonstrates the power of **low-code automation platforms** like n8n to orchestrate complex workflows involving multiple APIs and AI models. "Concierge" acts as a personal productivity assistant, accessed through the simple and ubiquitous interface of WhatsApp.

### Concept & Philosophy

The core idea is to use n8n as a visual "nervous system" that connects various external services. The agent is event-driven, triggered by a WhatsApp message, and follows a branching path to provide a rich, multi-modal response. It showcases how to build powerful applications with minimal code, focusing on the logic of the data flow.

### Demonstrated Concepts

This project is an excellent case study for:

*   **Low-Code AI Integration:** Building complex AI-powered workflows without extensive programming.
*   **API Orchestration:** Seamlessly connecting and passing data between multiple, unrelated web services.
*   **Event-Driven Architecture:** Creating reactive systems that are triggered by external events (a WhatsApp message).
*   **Multi-Modal AI:** Combining language models (for text) and diffusion models (for images) in a single workflow to provide richer outputs.
*   **ChatOps:** Using a chat interface to control and interact with complex backend systems.

## Academic Use

Both projects in this repository are intended for academic and educational purposes. You are encouraged to explore, modify, and use the code and architectural patterns as a reference for your own research, studies, and demonstrations.
