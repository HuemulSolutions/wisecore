from typing_extensions import TypedDict, Optional, Annotated
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph.message import add_messages
from src.database.core import get_graph_session
from .services import ChatbotServices
from .prompt import chatbot_prompt

class State(TypedDict):
    execution_id: str
    messages: Annotated[list, add_messages]
    content: Optional[str]
    llm: Optional[object]
    
async def entrypoint(state: State) -> State:
    print("Entrypoint")
    """
    Entry point for the chatbot. It initializes the conversation state.
    """
    async with get_graph_session() as session:
        service = ChatbotServices(session)
        state['content'] = await service.get_execution_content(state['execution_id'])
        state['llm'] = await service.get_llm()
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
    llm = state['llm']
    response = await llm.ainvoke(prompt.format_messages(history=state['messages']))
    state['messages'] = response
    return state
        