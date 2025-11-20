from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel


def get_llm(model_info: dict) -> BaseChatModel:
    print("Getting LLM with model info:")
    print(model_info)
    provider = model_info.get("provider")
    model_name = model_info.get("name")
    api_key = model_info.get("key")
    endpoint = model_info.get("endpoint")
    deployment = model_info.get("deployment")

    if provider == "azure_openai":
        llm = init_chat_model(
            model=model_name,
            model_provider="azure_openai",
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=deployment
        )
    elif provider == "openai":
        llm = init_chat_model(
            model=model_name,
            model_provider="openai",
            api_key=api_key,
        )
    elif provider == "anthropic":
        llm = init_chat_model(
            model=model_name,
            model_provider="anthropic",
            api_key=api_key,
            max_tokens=8192
        )
    elif provider == "ibm_model_gateway":
        llm = init_chat_model(
            model=model_name,
            model_provider="openai",
            api_key=api_key,
            base_url=endpoint,
            max_tokens=8192
        )  
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    return llm