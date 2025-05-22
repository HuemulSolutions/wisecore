from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from dotenv import load_dotenv
import os
load_dotenv()

def get_llm(llm: str)-> BaseChatModel:
    if llm == "gpt-4.1":
        gpt = init_chat_model(
            model="azure_openai:gpt-4.1",
            azure_deployment="gpt-4.1",
        )
        return gpt
    elif llm == "llama":
        llama = init_chat_model(
            model="ibm:meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
            project_id=os.getenv("WATSONX_PROJECT_ID")
        )
        return llama
    elif llm == "granite":
        granite = init_chat_model(
            model="ibm:ibm/granite-3-3-8b-instruct",
            model_provider="ibm",
            project_id=os.getenv("WATSONX_PROJECT_ID")
        )
        return granite