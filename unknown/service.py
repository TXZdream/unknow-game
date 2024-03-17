import logging
import time
from sqlitedict import SqliteDict
from io import StringIO
from contextlib import redirect_stdout
from langchain.prompts.chat import ChatPromptTemplate
from llm.client import llm_client
from llm.prompt import UnknownPrompt
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.output_parsers import StructuredOutputParser, ResponseSchema, PydanticOutputParser
from langchain.schema import BaseOutputParser, OutputParserException

from unknown.model import Operation, TurnEvent, TurnEvents, UnknownModel
import json
import re
import json5

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
            if iterator_dict[k].get('error', None):
                print(
                    f"------ skip iterator named {k} because of history error ------")
                continue
            used_turn = iterator_dict[k].get('used_turn', 0)
            max_turn = iterator_dict[k].get('turn', 0)
            if max_turn != -1 and used_turn >= max_turn:
                print(
                    f"------ skip iterator named {k} because of iter max turns ------")
                continue
            # 准备数据和执行用的代码
            logic = v.get("logic")
            # 执行并更新结果
            try:
                data_ctx = {k: v.get("value", 0) for k, v in data.items()}
                # code = f"import json\n{logic}\nprint(json.dumps(run()))"
                exec(logic, data_ctx, data_ctx)
            except Exception as e:
                iterator_dict[k]['error'] = str(e)
            # new_data = json.loads(f.getvalue())
            for k1 in data.keys():
                if k1 in data_ctx:
                    data[k1]['value'] = data_ctx[k1]
            # 更新迭代器次数
            iterator_dict[k]['used_turn'] = used_turn + 1
            print(f"------  end run iterator named {k}  ------")
        # 回写数据
        for k, v in data.items():
            self.db.data[k] = v
        for k, v in iterator_dict.items():
            self.db.iterator[k] = v
            if v.get('error', None):
                del self.db.iterator[k]
        self.db.global_data['turn'] = self.db.global_data.get(
            'turn', 0) + 1

        # 记录日志
        self.db.data_log[self.incr()] = {
            'data': data, 'iterator': iterator_dict, 'turn': self.db.global_data['turn']}

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
            | llm_client.qwen_turbo
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
        matches = re.findall(r"```json\n(.*?)\n```", result, re.DOTALL)
        if matches:
            result = matches[0]
        result = json.dumps(json5.loads(result))
        result = parser.parse(result)
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
                del self.db.data[data_op.data_name]

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
                del self.db.iterator[iter_op.iterator_name]
        print(
            f"==== Finish applying the unknown with sentence {word} ====")

        turn = self.db.global_data.get('turn', 0)
        self.db.story[self.incr()] = {
            'data': word, 'turn': turn, 'manual': 1}
        # 记录日志
        self.db.data_log[self.incr()] = {
            'data': {k: v for k, v in self.db.data.items()}, 'iterator': {k: v for k, v in self.db.iterator.items()}, 'turn': turn}

    def show(self):
        global_data = f"Global data:\n    - Turn: {self.db.global_data.get('turn', 0)}"
        data = "Current data is:\n"+"\n".join(
            [f"    - {k}, value is {v.get('value')}{v.get('unit', '')}, description: {v.get('desc')}" for k, v in self.db.data.items()])
        iterator = "Current iterator is:\n"+"\n".join(
            [f"    - {k}, max iter turn {v.get('turn', 0)}, used iter turn {v.get('used_turn', 0)}, description is {v.get('desc')}" for k, v in self.db.iterator.items()])

        print(global_data, "\n", data, "\n", iterator, "\n")

    def get_describe_parser(self):
        parser = PydanticOutputParser(pydantic_object=TurnEvents)
        return parser

    def prepare_describe_agent(self, parser: BaseOutputParser):
        prompt = ChatPromptTemplate.from_template(
            UnknownPrompt.describe_game_prompt
        )
        data = "\n".join(
            [f"{k}, value is {v.get('value')}{v.get('unit', '')}, description: {v.get('desc')}" for k, v in self.db.data.items()])
        iterator = "\n".join(
            [f"{k}: {v.get('desc')}" for k, v in self.db.iterator.items()])
        past_events = "\n".join(
            [f"turn {v.get('turn', 0)}: {v.get('data', '')}" for k, v in self.db.story.items()])

        prompt = prompt.partial(
            data=data,
            iterator=iterator,
            language="Chinese",
            past_events=past_events,
            turn=self.db.global_data.get('turn', 0),
            format_instructions=parser.get_format_instructions(),
        )
        agent = (
            {}
            | prompt
            | llm_client.qwen_turbo
        )
        return agent.with_config(
            {
                "run_name": "UnknownDescribeAgent",
                # "callbacks": [ConsoleCallbackHandler()],
            }
        )

    def incr(self):
        incr_id = self.db.global_data.get('incr_id', 0)
        self.db.global_data['incr_id'] = incr_id + 1

        return incr_id

    def describe(self) -> str:
        parser = self.get_describe_parser()
        agent = self.prepare_describe_agent(parser)
        result = agent.invoke({})
        result = parser.parse(result.content)

        for data in result.events:
            self.db.story[self.incr()] = {
                'data': data.event, 'turn': data.turn}

        for k, v in self.db.story.items():
            print(
                f"- Turn {v.get('turn', 0)}({'手动事件' if v.get('manual', 0) else 'AI事件'}): {v.get('data', '')}")
