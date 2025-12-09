from pydantic import BaseModel, Field


class StringQuery(BaseModel):
    query_string: str = Field(..., min_length=1, max_length=1000)
    ignore_case: bool = True
    include_substring_matches: bool = False


class StringMatch(BaseModel):
    matched_string: str
    source: str
