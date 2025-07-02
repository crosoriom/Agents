import os
import json
from google import genai
from google.genai import types
from knowledge_base import KnowledgeBase
from tools import ToolBox

class LLMAgent:
    def __init__(self, knowledge_base: KnowledgeBase):
        """
        Initializes the agent using the NEW google-genai SDK.
        """
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY not found in .env file.")

        # CORRECT: Initialize the client as per the migration guide.
        # The new SDK uses a client object to make API calls.
        self.client = genai.Client()

        self.toolbox = ToolBox(knowledge_base)
        self.tool_functions = self.toolbox.get_tool_functions()
        
        # CORRECT: Tools are passed in the GenerateContentConfig.
        # The new SDK uses a GenerateContentConfig object to pass configuration, including tools.
        self.config = types.GenerateContentConfig(
            tools=list(self.tool_functions.values())
        )

        # The model name should include the 'models/' prefix. This is correct.
        self.model_name = 'models/gemini-2.5-flash' 

        self.system_prompt = f"""
        You are an advanced AI Shopping Assistant with a dynamic Knowledge Base (KB) that you MUST keep up-to-date.
        Your primary goal is to find the best products for the user by following a strict, cyclical reasoning process.

        **Core Reasoning Cycle:**

        1.  **Read from KB (ALWAYS Step 1):**
            - At the start of every new user query, your absolute first action must be `get_shop_details_from_kb()`. This gives you the current state of all known stores, their capabilities, and their performance metrics.

        2.  **Plan & Act (Step 2):**
            - Analyze the KB data and the user's request.
            - Formulate a plan, prioritizing the best-performing methods (MCP > API > Scraping). Use the latency and success rates from the KB to inform your choice.
            - Execute the appropriate communication tool (`fetch_products_via_mcp`, `make_http_get_request`, or `scrape_and_summarize_website_text`).
            - **CRITICAL:** The output from these tools is a JSON string containing `result`, `success`, and `latency`. You MUST parse this JSON to get the data.

        3.  **Synthesize & Respond (Step 4):**
            - After updating the KB, analyze the `result` data you received.
            - If you need to search other stores, go back to Step 2 and repeat the cycle.
            - Once you have enough information, present the top 3 products to the user, unless they ask for a different number.

        By following this Read-Act-Write cycle, you constantly learn and improve your own performance.
        """

    def process_user_query(self, user_query: str) -> str:
        """
        Processes the user's query using a manually managed chat history and the correct tool-calling loop.
        """
        print(f"\n[LLM Agent] Starting to process query: '{user_query}'")
        
        # Manually manage conversation history as a list of Content objects
        # The new SDK uses genai.to_content() to convert text to Content objects
        conversation_history = [
            types.Content(role="user", parts=[types.Part.from_text(text=self.system_prompt)]),
            types.Content(role="user", parts=[types.Part.from_text(text=user_query)])
        ]

        while True:
            print("[LLM Agent] Sending request to Gemini...")
            try:
                # CORRECT: API call through the client object.
                # The `generate_content` method is on the `client.models` object.
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=conversation_history,
                    config=self.config
                )

                # The old check 'response.candidates[0].finish_reason == types.FinishReason.TOOL_CALL' is incorrect.
                # The new, correct way is to directly check if 'response.function_calls' exists and has content.
                if response.function_calls:
                    print("[LLM Agent] Gemini is requesting a tool call.")
                    # Append the model's request to the history
                    conversation_history.append(response.candidates[0].content)

                    # Getting function calls is now done via response.function_calls
                    function_calls = response.function_calls
                    
                    # Construct the tool response using types.Part.from_function_response
                    tool_response_parts = []
                    for call in function_calls:
                        function_name = call.name
                        function_args = dict(call.args)
                        print(f"  - Tool: {function_name}, Arguments: {function_args}")

                        if function_name in self.tool_functions:
                            tool_function = self.tool_functions[function_name]
                            try:
                                tool_output = tool_function(**function_args)
                                tool_response_parts.append(
                                    types.Part.from_function_response(
                                        name=function_name,
                                        response={'result': tool_output}
                                    )
                                )
                            except Exception as e:
                                print(f"[LLM Agent] Error executing tool {function_name}: {e}")
                                tool_response_parts.append(
                                    types.Part.from_function_response(
                                        name=function_name,
                                        response={'error': str(e)}
                                    )
                                )
                    
                    print("[LLM Agent] Tools executed. Sending results back to Gemini.")
                    # Append the tool results as a new Content object to the history
                    conversation_history.append(types.Content(role="tool", parts=tool_response_parts))

                else:
                    # The model has finished its reasoning
                    print("[LLM Agent] Gemini has provided the final answer.")
                    return response.text.strip()
            
            except Exception as e:
                print(f"[LLM Agent] An error occurred during generation: {e}")
                return "I'm sorry, I encountered an issue while processing your request. Please try again."
