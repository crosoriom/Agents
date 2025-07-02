# AI Shopping Agent: A Self-Learning Bot for Product Discovery

This project implements an advanced AI Shopping Agent powered by Google's Gemini Pro. Unlike simple scripts, this agent is built on a philosophy of continuous learning. It dynamically discovers online stores, learns the best way to communicate with them (API vs. web scraping), and updates its own knowledge base in real-time based on the performance of its actions.

## Core Philosophy: The Read -> Plan -> Act & Learn Cycle

The agent's intelligence comes from a simple but powerful operational loop that happens for every user query:

1.  **Read:** The agent first consults its internal Knowledge Base (a SQLite database) to understand the available stores, their capabilities (API support, URLs), and their last known performance (success rate, latency).
2.  **Plan:** Based on this data and the user's request, the LLM formulates a plan. It prioritizes the most efficient communication methods first (e.g., using a store's API over web scraping).
3.  **Act & Learn:** The agent executes its plan by calling the chosen tool. The tool not only fetches the product data but **automatically records its own performance** (success/failure and speed) back into the Knowledge Base. This ensures that every action makes the agent smarter for the next request.

## Key Features

*   **Dynamic Store Discovery:** On first run, the agent discovers local, national, and international stores and probes them to identify their communication capabilities.
*   **Persistent Knowledge Base:** Uses a SQLite database (`shops.db`) to store information about stores, including API endpoints and performance metrics.
*   **Autonomous Tool Selection:** The LLM independently decides the best tool for the job (`API request` vs. `Web Scraping`) based on the data in its Knowledge Base.
*   **Real-time Performance-Based Learning:** Every tool call is timed and its success is logged. A slow or failing API will be deprioritized by the agent in the future in favor of more reliable methods.
*   **Automated API Authentication:** The agent's tools automatically detect and inject the necessary API keys from an environment file, keeping the LLM's logic clean and secure.
*   **Graceful Fallback:** If a high-priority method like an API call fails, the agent can fall back to web scraping to ensure the user's request is still fulfilled.

## Agent Operational Flow

This flowchart illustrates the agent's lifecycle, from the initial one-time setup to the dynamic, cyclical process for handling every user query.

```mermaid
graph TD
    subgraph "Phase 1: One-Time Setup (on first run)"
        direction TB
        A[User Location Input] --> B{Discovery Engine};
        B --> C[Identify Stores];
        C --> D{Verify Methods & URLs};
        D --> E[Populate Knowledge Base with Initial Data];
    end

    subgraph "Phase 2: User Query Cycle (for every request)"
        direction TB
        F[User Query e.g., 'best 4k tv'] --> G{LLM Agent};

        subgraph "Step 1: Read"
            G -- 1. "What are my options?" --> H[Call Tool: get_shop_details_from_kb()];
            H -- 2. Reads from --> KB[(Knowledge Base)];
            KB -- 3. Returns store list, URLs, & performance data --> G;
        end

        subgraph "Step 2: Plan & Act/Learn"
            G -- 4. "Best Buy has a fast API. I'll use that." --> I{Choose Tool e.g., make_api_request};
            I -- 5. Executes request --> BBApi((Best Buy API));
            BBApi -- 6. Returns product data --> I;
            I -- 7. AUTOMATICALLY updates performance --> KB;
            I -- 8. Returns final product data --> G;
        end
        
        subgraph "Step 3: Synthesize & Respond"
            G -- 9. "I have the data. Time to formulate a response." --> J[Ranked Recommendations];
            J -- 10. Presents final answer --> User([User]);
        end

    end

    style G fill:#e6f3ff,stroke:#333,stroke-width:2px
    style KB fill:#e6ffe6,stroke:#333,stroke-width:2px
    style BBApi fill:#f0f0f0,stroke:#333
```

## Project Structure

```
.
├── .env.example          # Template for environment variables
├── AIShoppingAgent_2_0.md  # Original planning document
├── discovery.py          # Handles store discovery and capability verification
├── knowledge_base.py     # Manages the SQLite database (the agent's "memory")
├── llm_agent.py          # Contains the core LLM agent logic and system prompt
├── main.py               # Main entry point to run the application
├── tools.py              # Defines the tools the LLM can use (API calls, scraping)
└── README.md             # This file
```

## Setup and Installation

Follow these steps to get the agent running on your local machine.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <repository-directory>
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Create and Populate `requirements.txt`

Create a file named `requirements.txt` and add the following lines:

```
google-generativeai
requests
python-dotenv
beautifulsoup4
```

Then, install the dependencies:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

You need to provide API keys for the services the agent uses.

a. Copy the example file:
```bash
cp .env.example .env
```
b. **Edit the `.env` file** and add your secret keys. You will need:
    *   **`GEMINI_API_KEY`**: Get this from [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   **`GOOGLE_PLACES_API_KEY`**: For discovering real local stores. Get this from the [Google Cloud Console](https://console.cloud.google.com/).

```ini
# .env file
GEMINI_API_KEY="your-google-gemini-api-key"
GOOGLE_PLACES_API_KEY="your-google-places-api-key"
```

## How to Run

Once the setup is complete, run the agent from your terminal:

```bash
python main.py
```

The application will first guide you through the initial store discovery phase and then hand you over to the AI Assistant for your queries.

### Example Usage

```
$ python main.py
Please enter your location (e.g., 'New York, NY'): New York, NY

[Setup] Performing store discovery for: 'New York, NY'...
... (Discovery logs) ...
[Setup] Initial setup complete. Knowledge Base is populated.

[Main] Initializing AI Shopping Assistant and injecting Knowledge Base...
[ToolBox] Initialized with shared Knowledge Base.
[Main] AI Assistant is ready.

Welcome to the AI Shopping Assistant!
I will consult my knowledge base to decide the best way to search.

What would you like to search for? (type 'quit' to exit)
> Find me a cheap 4k tv from Best Buy

[LLM Agent] Starting query: 'Find me a cheap 4k tv from Best Buy'
[LLM Agent] Sending request to Gemini...
... (Tool call logs) ...
[LLM Agent] Gemini has provided the final answer.

**************************************************
      AI Assistant Recommendation
**************************************************
Based on your request, I found these great options for affordable 4K TVs at Best Buy:

1.  **Insignia™ - 50" Class F30 Series LED 4K UHD Smart Fire TV**
    *   **Price:** $239.99
    *   **Store:** Best Buy

2.  **TCL - 55" Class 4-Series 4K UHD HDR Smart Roku TV**
    *   **Price:** $269.99
    *   **Store:** Best Buy

3.  **Hisense - 55" Class A6 Series 4K UHD Smart Google TV**
    *   **Price:** $249.99
    *   **Store:** Best Buy
**************************************************
```
