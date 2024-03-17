from langchain.chat_models import ChatOpenAI
from langchain.prompts import *
from langchain.embeddings.openai import OpenAIEmbeddings
from config import settings
import dashscope
from langchain_community.llms.tongyi import Tongyi

dashscope.api_key = settings.dashscope.key


class LLMClient:
    def __init__(self) -> None:
        self.init_qwen()

    def init_qwen(self) -> None:
        key = settings.dashscope.key

        self.qwen_turbo = Tongyi(
            model_name="qwen-turbo",
            dashscope_api_key=key,
        )


llm_client = LLMClient()
