import logging
from sqlitedict import SqliteDict
from io import StringIO
from contextlib import redirect_stdout
from langchain.prompts.chat import ChatPromptTemplate
from llm.client import llm_client
from llm.prompt import UnknownPrompt
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.output_parsers import StructuredOutputParser, ResponseSchema, PydanticOutputParser

from unknown.model import Operation, UnknownModel

logger = logging.getLogger(__name__)


class UnknownService:
    def __init__(self, path: str) -> None:
        self.path = path
        self.db = UnknownModel(path)

    def iter(self) -> None:
        data = {}
        for k, v in self.db.data.items():
            data[k] = v
        # 执行迭代器
        for k, v in self.db.iterator.items():
            logger.info(f"------ start run iterator named {k} ------")
            # 准备数据和执行用的代码
            logic = v.get("logic")
            related_data_key = v.get('related_data_key', None)
            if not related_data_key or data.get(related_data_key, None):
                logger.warn(
                    f"skip run iterator named {k}, data key {related_data_key} not found")
                continue
            # 执行并更新结果
            f = StringIO()
            with redirect_stdout(f):
                exec(
                    f"{logic}\nprint(run({data[related_data_key].get('value')}))")
            data[related_data_key]['value'] = float(f.getvalue())
            logger.info(f"------  end run iterator named {k}  ------")
        # 回写数据
        for k, v in data.items():
            self.db.data[k] = v

    def prepare_agent(self):
        prompt = ChatPromptTemplate.from_template(
            UnknownPrompt.generate_data_and_iterator_prompt
        )
        data = "\n".join(
            [f"{k}, value is {v.get('value')}, description: {v.get('desc')}" for k, v in self.db.data.items()])
        iterator = "\n".join(
            [f"{k}: {v.get('desc')}" for k, v in self.db.iterator.items()])
        prompt = prompt.partial(
            data=data,
            iterator=iterator,
        )
        agent = (
            {
                "input": lambda x: x["input"],
            }
            | prompt
            | llm_client.gpt_4_128k
        )
        return agent.with_config(
            {
                "run_name": "UnknownUpdaterAgent",
                "callbacks": [ConsoleCallbackHandler()],
            }
        )

    def get_output_parser(self):
        parser = PydanticOutputParser(pydantic_object=Operation)
        return parser

    def generate_data_and_iterator(self, word: str):
        agent = self.prepare_agent()
        parser = self.get_output_parser()
        result = agent.invoke({"input": word})
        result = parser.parse(result.content)

        print(result)
