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
    elif llm == "deepseek-v3":
        deepseek = init_chat_model(
            model="azure_ai:DeepSeek-V3-0324",
            azure_deployment="DeepSeek-V3-0324",
        )
        return deepseek
    elif llm == "llama-4-maverick":
        llama = init_chat_model(
            model="azure_ai:Llama-4-Maverick-17B-128E-Instruct-FP8",
            azure_deployment="Llama-4-Maverick-17B-128E-Instruct-FP8"
        )
        return llama
    elif llm == "gpt-oss":
        gpt_oss = init_chat_model(
            model="azure_ai:gpt-oss-120b",
            azure_deployment="gpt-oss-120b",
        )
        return gpt_oss
    elif llm == "granite":
        granite = init_chat_model(
            model="ibm:ibm/granite-3-3-8b-instruct",
            model_provider="ibm",
            project_id=system_config.WATSONX_PROJECT_ID
        )
        return granite