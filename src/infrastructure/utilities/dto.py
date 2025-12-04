import typing
from dataclasses import asdict, is_dataclass
from typing import Union


class BaseDTOMixin:
    def to_payload(self, exclude_none: bool = False) -> dict:
        data = asdict(self) if is_dataclass(self) else dict(self)
        return {k: v for k, v in data.items() if exclude_none and v is not None}

    @classmethod
    def from_orm(cls, orm_obj) -> Union["BaseDTOMixin", None]:
        if orm_obj is None:
            return None
        type_hints = typing.get_type_hints(cls)
        obj = orm_obj.__dict__
        new_dict = {}
        for attr_name in type_hints.keys():
            if attr_name in obj:
                new_dict[attr_name] = obj[attr_name]
        return cls(**new_dict)
