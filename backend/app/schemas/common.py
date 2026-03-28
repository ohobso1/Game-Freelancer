from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class MongoModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class IdResponse(MongoModel):
    id: str = Field(alias="_id")


def parse_object_id(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValueError("Invalid ObjectId")
    return ObjectId(value)


def to_object_id_str(document: dict) -> dict:
    converted = dict(document)
    if "_id" in converted:
        converted["_id"] = str(converted["_id"])
    return converted
