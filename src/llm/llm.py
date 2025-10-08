from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from src.config import system_config

def get_llm(llm: str)-> BaseChatModel:
    if llm == "gpt-4.1":
        gpt = init_chat_model(
            model="azure-gpt-4.1",
            model_provider="openai",
            base_url=system_config.MODEL_GATEWAY_URL,
            api_key=system_config.MODEL_GATEWAY_APIKEY,
        )
        return gpt
    elif llm == "claude-sonnet-4":
        claude = init_chat_model(
            model="claude-sonnet-4",
            model_provider="openai",
            base_url=system_config.MODEL_GATEWAY_URL,
            api_key=system_config.MODEL_GATEWAY_APIKEY,
        )
        return claude
    elif llm == "llama-4-maverick":
        llama = init_chat_model(
            model="ibm-llama-maverick",
            model_provider="openai",
            base_url=system_config.MODEL_GATEWAY_URL,
            api_key=system_config.MODEL_GATEWAY_APIKEY,
            max_tokens=8192
        )
        return llama
    elif llm == "gpt-oss":
        gpt_oss = init_chat_model(
            model="ibm-gpt-oss",
            model_provider="openai",
            base_url=system_config.MODEL_GATEWAY_URL,
            api_key=system_config.MODEL_GATEWAY_APIKEY,
            max_tokens=8192
        )
        return gpt_oss
    elif llm == "granite-4":
        granite = init_chat_model(
            model="granite-4",
            model_provider="openai",
            base_url=system_config.MODEL_GATEWAY_URL,
            api_key=system_config.MODEL_GATEWAY_APIKEY,
            max_tokens=8192
        )
        return granite