import logging
from sqlitedict import SqliteDict
from io import StringIO
from contextlib import redirect_stdout
from langchain.prompts.chat import ChatPromptTemplate
from llm.client import llm_client
from llm.prompt import UnknownPrompt
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.output_parsers import StructuredOutputParser, ResponseSchema, PydanticOutputParser
from langchain.schema import BaseOutputParser, OutputParserException

from unknown.model import Operation, UnknownModel
import json

logger = logging.getLogger(__name__)


class UnknownService:
    def __init__(self, path: str) -> None:
        self.path = path
        self.db = UnknownModel(path)

    def iter(self) -> None:
        data = {}
        for k, v in self.db.data.items():
            data[k] = v
        iterator_dict = {}
        for k, v in self.db.iterator.items():
            iterator_dict[k] = v
        # 执行迭代器
        for k, v in iterator_dict.items():
            print(f"------ start run iterator named {k} ------")
            used_turn = iterator_dict[k].get('used_turn', 0)
            max_turn = iterator_dict[k].get('turn', 0)
            if max_turn != -1 and used_turn >= max_turn:
                print(
                    f"------ skip iterator named {k} because of iter max turns ------")
                continue
            # 准备数据和执行用的代码
            logic = v.get("logic")
            # 执行并更新结果
            f = StringIO()
            with redirect_stdout(f):
                data_ctx = {k: v.get("value", 0) for k, v in data.items()}
                code = f"import json\n{logic}\nprint(json.dumps(run()))"
                exec(code, data_ctx)
            new_data = json.loads(f.getvalue())
            for k1, v1 in new_data.items():
                data[k1]['value'] = v1
            # 更新迭代器次数
            iterator_dict[k]['used_turn'] = used_turn + 1
            print(f"------  end run iterator named {k}  ------")
        # 回写数据
        for k, v in data.items():
            self.db.data[k] = v
        for k, v in iterator_dict.items():
            self.db.iterator[k] = v
        self.db.global_data['turn'] = self.db.global_data.get(
            'turn', 0) + 1

    def prepare_update_agent(self, parser: BaseOutputParser):
        prompt = ChatPromptTemplate.from_template(
            UnknownPrompt.generate_data_and_iterator_prompt
        )
        data = "\n".join(
            [f"{k}, value is {v.get('value')}{v.get('unit', '')}, description is {v.get('desc')}" for k, v in self.db.data.items()])
        iterator = "\n".join(
            [f"{k}, max iter turn {v.get('turn', 0)}, used iter turn {v.get('used_turn', 0)}, description is {v.get('desc')}" for k, v in self.db.iterator.items()])
        prompt = prompt.partial(
            data=data,
            iterator=iterator,
            format_instructions=parser.get_format_instructions(),
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
                # "callbacks": [ConsoleCallbackHandler()],
            }
        )

    def get_update_output_parser(self):
        parser = PydanticOutputParser(pydantic_object=Operation)
        return parser

    def update_data_and_iterator(self, word: str):
        parser = self.get_update_output_parser()
        agent = self.prepare_update_agent(parser)
        result = agent.invoke({"input": word})
        result = parser.parse(result.content)
        # 写入数据
        print(
            f"==== Start applying the unknown with sentence {word} ====")
        print(f"Start data operation")
        for data_op in result.data_operations:
            print(
                f"operation: {data_op.operation}, data: {data_op.data_name}, reason: {data_op.reason}")
            if data_op.operation == 'add':
                self.db.data[data_op.data_name] = {
                    'value': data_op.init_value,
                    'desc': data_op.description,
                    'unit': data_op.unit,
                }
            elif data_op.operation == 'remove':
                self.db.data.pop(data_op.data_name, None)

        print(f"Start iterator operation")
        for iter_op in result.iterator_operations:
            print(
                f"operation: {iter_op.operation}, iterator: {iter_op.iterator_name}, reason: {iter_op.reason}")
            if iter_op.operation == 'add':
                self.db.iterator[iter_op.iterator_name] = {
                    'desc': iter_op.description,
                    'logic': iter_op.code,
                    'turn': iter_op.turn,
                    # 'related_data_key': iter_op.related_data_key,
                }
            elif iter_op.operation == 'remove':
                self.db.iterator.pop(iter_op.iterator_name, None)
        print(
            f"==== Finish applying the unknown with sentence {word} ====")

    def show(self):
        global_data = f"Global data:\n    - Turn: {self.db.global_data.get('turn', 0)}"
        data = "Current data is:\n"+"\n".join(
            [f"    - {k}, value is {v.get('value')}{v.get('unit', '')}, description: {v.get('desc')}" for k, v in self.db.data.items()])
        iterator = "Current iterator is:\n"+"\n".join(
            [f"    - {k}, max iter turn {v.get('turn', 0)}, used iter turn {v.get('used_turn', 0)}, description is {v.get('desc')}" for k, v in self.db.iterator.items()])

        print(global_data, "\n", data, "\n", iterator, "\n")

    def prepare_describe_agent(self):
        prompt = ChatPromptTemplate.from_template(
            UnknownPrompt.describe_game_prompt
        )
        data = "\n".join(
            [f"{k}, value is {v.get('value')}, description: {v.get('desc')}" for k, v in self.db.data.items()])
        iterator = "\n".join(
            [f"{k}: {v.get('desc')}" for k, v in self.db.iterator.items()])
        prompt = prompt.partial(
            data=data,
            iterator=iterator,
            language="Chinese",
        )
        agent = (
            {}
            | prompt
            | llm_client.gpt_4_128k
        )
        return agent.with_config(
            {
                "run_name": "UnknownDescribeAgent",
                # "callbacks": [ConsoleCallbackHandler()],
            }
        )

    def describe(self) -> str:
        agent = self.prepare_describe_agent()
        result = agent.invoke({})
        result = result.content
        self.db.story[self.db.global_data['turn', 0]] = result

        for k, v in self.db.story.items():
            print(f'- Turn {k}: {v}')
