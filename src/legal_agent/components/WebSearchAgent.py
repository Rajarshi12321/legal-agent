from legal_agent import (
    ChatGoogleGenerativeAI,
    DuckDuckGoSearchResults,
    create_tool_calling_agent,
    AgentExecutor,
    ChatPromptTemplate,
    MessagesPlaceholder,
)


class WebSearchAgent:

    def __init__(self):
        # Initialize the chat model, prompt template, and search tools using LangGraph.
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
        self.tools = [DuckDuckGoSearchResults()]
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Provide a detailed answer based on web search for:"),
                ("human", "{input}"),
                MessagesPlaceholder(
                    "agent_scratchpad"
                ),  # This placeholder is required!
            ]
        )

    def web_based_response(self, user_input):
        """
        Sets up an agent with tool access, executes a tutorial-style response based on the user query,
        and saves the response to a markdown file.
        """
        # Create an agent that can call tools (i.e. DuckDuckGo search) during processing.
        agent = create_tool_calling_agent(self.model, self.tools, self.prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        response = agent_executor.invoke({"input": user_input})

        # Save and display the response as a markdown file.
        output = str(response.get("output")).replace("```markdown", "").strip()

        return output
