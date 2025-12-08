from pydantic import BaseModel


class StringQuery(BaseModel):
    query_string: str
    ignore_case: bool = False
    include_substring_matches: bool = False


class StringMatch(BaseModel):
    matched_string: str
    source: str
