from typing import List
from sqlitedict import SqliteDict
from langchain.pydantic_v1 import BaseModel, Field, validator


class UnknownModel:
    _db_name = "unknown.sqlite"
    _data_table_name = "data"
    _iter_table_name = "iterator"

    def __init__(self, db_path: str) -> None:
        self.data = SqliteDict(
            f"{db_path}/{UnknownModel._db_name}", tablename=UnknownModel._data_table_name, autocommit=True)
        self.iterator = SqliteDict(
            f"{db_path}/{UnknownModel._db_name}", tablename=UnknownModel._iter_table_name, autocommit=True)


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
    reason: str = Field(description="reason of why operate this data")


class IteratorOperation(BaseModel):
    operation: str = Field(
        description="operation of iterator, allowed values: add, remove")
    iterator_name: str = Field(
        description="name of iterator which will be operated")
    description: List[str] = Field(
        description="description of new added iterator")
    related_data_key: str = Field(
        description="key of related data which will is related to this iterator",
    )
    code: str = Field(
        description="code of new added iterator, a python function, format: def run(x): ...",
    )
    reason: str = Field(description="reason of why operate this iterator")


class Operation(BaseModel):
    data_operations: List[DataOperation] = Field(
        description="list of data operations",
    )
    iterator_operations: List[IteratorOperation] = Field(
        description="list of iterator operations",
    )
