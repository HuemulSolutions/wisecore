from typing_extensions import TypedDict, Optional, Annotated
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from src.database.core import get_graph_session
from .services import ChatbotServices
from .prompt import chatbot_prompt

class State(TypedDict):
    execution_id: str
    messages: Annotated[list, add_messages]
    content: Optional[str]

llm = init_chat_model(
            model="azure_openai:gpt-4.1",
            azure_deployment="gpt-4.1",
        )
    
async def entrypoint(state: State) -> State:
    print("Entrypoint")
    """
    Entry point for the chatbot. It initializes the conversation state.
    """
    async with get_graph_session() as session:
        service = ChatbotServices(session)
        state['content'] = await service.get_execution_content(state['execution_id'])
    return state


async def agent(state: State)-> State:
    print("Agent")
    """
    Main agent function to process the conversation.
    """
    formated_prompt = chatbot_prompt.format(content=state['content'])
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=formated_prompt),
        MessagesPlaceholder(variable_name="history")
    ])
    
    response = await llm.ainvoke(prompt.format_messages(history=state['messages']))
    state['messages'] = response
    return state
        