from pydantic import BaseModel


def to_camel(snake_str: str) -> str:
    components = snake_str.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])


class CamelSchema(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
