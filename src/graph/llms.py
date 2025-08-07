from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from src.config import system_config

def get_llm(llm: str)-> BaseChatModel:
    if llm == "gpt-4.1":
        gpt = init_chat_model(
            model="azure_openai:gpt-4.1",
            azure_deployment="gpt-4.1",
        )
        return gpt
    elif llm == "deepseek":
        deepseek = init_chat_model(
            model="azure_ai:DeepSeek-V3-0324",
            azure_deployment="DeepSeek-V3-0324",
        )
        return deepseek
    elif llm == "llama":
        llama = init_chat_model(
            model="ibm:meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
            project_id=system_config.WATSONX_PROJECT_ID
        )
        return llama
    elif llm == "granite":
        granite = init_chat_model(
            model="ibm:ibm/granite-3-3-8b-instruct",
            model_provider="ibm",
            project_id=system_config.WATSONX_PROJECT_ID
        )
        return granite