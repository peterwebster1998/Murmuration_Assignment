from pydantic import BaseModel, Field
from psycopg2.extras import RealDictRow
from typing import List, Any, TypeVar, Generic

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    status: str
    data: T

class Response(BaseModel):
    id: str
    content: Any

class QuestionOrField(BaseModel):
    title: str
    responses: List[Response]

    @classmethod
    def from_real_dict(cls, title: str, responses: List[RealDictRow]) -> 'QuestionOrField':
        return cls(title=title, responses=[Response(id=row['id'], content=row[title]) for row in responses])

class Survey(BaseModel):
    name: str
    questions_or_fields: List[QuestionOrField]

    @classmethod
    def from_real_dict(cls, name: str, responses: List[RealDictRow]) -> 'Survey':
        fields = {}
        id = 0
        for response in responses:
            for k, v in response.items():
                if k == 'id':
                    id = v
                else:
                    if k not in fields:
                        fields[k] = []
                    fields[k].append(Response(id=id, content=v))
        for k, v in fields.items():
            fields[k] = QuestionOrField(title=k, responses=v)
        return cls(
            name=name,
            questions_or_fields=list(fields.values())
        )

class DBContents(BaseModel):
    surveys: List[Survey]