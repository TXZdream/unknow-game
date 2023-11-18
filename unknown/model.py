import os
from typing import List
from sqlitedict import SqliteDict
from langchain.pydantic_v1 import BaseModel, Field, validator


class UnknownModel:
    _db_name = "unknown.sqlite"
    _data_table_name = "data"
    _iter_table_name = "iterator"
    _global_table_name = "global"
    _story_table_name = "story"

    def __init__(self, db_path: str) -> None:
        os.makedirs(db_path, exist_ok=True)
        self.data = SqliteDict(
            f"{db_path}/{UnknownModel._db_name}", tablename=UnknownModel._data_table_name, autocommit=True)
        self.iterator = SqliteDict(
            f"{db_path}/{UnknownModel._db_name}", tablename=UnknownModel._iter_table_name, autocommit=True)
        self.global_data = SqliteDict(
            f"{db_path}/{UnknownModel._db_name}", tablename=UnknownModel._global_table_name, autocommit=True)
        self.story = SqliteDict(
            f"{db_path}/{UnknownModel._db_name}", tablename=UnknownModel._story_table_name, autocommit=True)


class DataOperation(BaseModel):
    operation: str = Field(
        description="operation of data, allowed values: add, remove")
    data_name: str = Field(
        description="name of data which will be operated")
    description: str = Field(
        description="description of new added data")
    init_value: float = Field(
        description="init value of new added data",
    )
    unit: str = Field(
        description="unit of new added data",
    )
    reason: str = Field(description="reason of why operate this data")


class IteratorOperation(BaseModel):
    operation: str = Field(
        description="operation of iterator, allowed values: add, remove")
    iterator_name: str = Field(
        description="name of iterator which will be operated")
    description: str = Field(
        description="description of new added iterator")
    # related_data_keys: List[str] = Field(
    #     description="keys of related data which will is related to this iterator, date key must exist in available data list, code can only access these datas",
    # )
    code: str = Field(
        description="code of new added iterator, each data code used must exist in available data list. Iterator is a python function with format: def run(): ..., no argument should be passed, dict of new data value should be returned",
    )
    turn: int = Field(
        description="the total turns number of new added iterator will be run, -1 means run forever",
    )
    reason: str = Field(description="reason of why operate this iterator")


class Operation(BaseModel):
    data_operations: List[DataOperation] = Field(
        description="list of data operations",
    )
    iterator_operations: List[IteratorOperation] = Field(
        description="list of iterator operations",
    )
