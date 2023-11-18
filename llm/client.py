from langchain.chat_models import ChatOpenAI
from langchain.prompts import *
from langchain.embeddings.openai import OpenAIEmbeddings
from config import settings

class LLMClient:
    def __init__(self) -> None:
        self.init_openai()

    def init_openai(self) -> None:
        key = settings.openai.key
        key_3_5 = settings.openai.key_3_5
        base = settings.openai.base

        self.gpt_3_5 = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            openai_api_key=key_3_5 if key_3_5 else key,
            openai_api_base=base,
        )
        self.gpt_3_5_16k = ChatOpenAI(
            model_name="gpt-3.5-turbo-16k",
            openai_api_key=key_3_5 if key_3_5 else key,
            openai_api_base=base,
        )
        self.gpt_4 = ChatOpenAI(
            model_name="gpt-4",
            openai_api_key=key,
            openai_api_base=base,
            temperature=0,
        )
        self.gpt_4_128k = ChatOpenAI(
            model_name="gpt-4-1106-preview",
            openai_api_key=key,
            openai_api_base=base,
            temperature=0,
        )
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=key_3_5 if key_3_5 else key,
            openai_api_base=base,
            model="text-embedding-ada-002",
            chunk_size=1,
        )

llm_client = LLMClient()