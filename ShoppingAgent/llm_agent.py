import os
import json
from google import genai
from google.genai import types
from knowledge_base import KnowledgeBase
from tools import scrape_and_summarize_website_text, make_http_get_requests, fetch_products_via_mcp

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

        self.tool_functions = {
            "scrape_and_summarize_website_text": scrape_and_summarize_website_text,
            "make_http_get_requests": make_http_get_requests,
            "fetch_products_via_mcp": fetch_products_via_mcp
        }
        
        # CORRECT: Tools are passed in the GenerateContentConfig.
        # The new SDK uses a GenerateContentConfig object to pass configuration, including tools.
        self.config = types.GenerateContentConfig(
            tools=list(self.tool_functions.values())
        )

        # The model name should include the 'models/' prefix. This is correct.
        self.model_name = 'models/gemini-2.5-flash' 

        all_shops = knowledge_base.get_all_shops()
        shop_list_str = "\n".join(
            [f"- {shop['name']} (Scope: {shop['scope']}, Supports MCP: {shop['mcp_enabled']}, Supports API: {shop['api_enabled']})" for shop in all_shops]
        )

        self.system_prompt = f"""
        You are an expert AI Shopping Assistant. Your primary goal is to find and recommend the best products for a user based on their request.
        **CRITICAL INSTRUCTION**: You MUST conduct your search using ONLY the following list of pre-approved stores. This list has been verified. Do not search anywhere else.
        **Available Stores:**
        {shop_list_str}
        Follow these steps:
        1.  **Analyze the Query:** Understand the user's request (product, features, constraints).
        2.  **Use Your Tools Strategically:**
            - For stores where 'Supports MCP' is True (like Amazon), you should prioritize using the `fetch_products_via_mcp` tool.
            - For other stores, try to use `make_http_get_requests` or `scrape_and_summarize_website_text` to find products. Construct URLs logically (e.g., 'https://www.bestbuy.com/search?q=...').
        3.  **Evaluate and Score:** Gather product information and internally score each product against the user's request.
        4.  **Formulate and Present Recommendation:** Select the top 3 products and present them to the user, explaining *why* each is a good choice.
        If you cannot find good matches in the provided stores, inform the user. Do not make up products.
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

                # The finish reason check is incorrect. It should be checked against the FinishReason enum.
                if response.candidates[0].finish_reason == types.FinishReason.TOOL_CALL:
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
