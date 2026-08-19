from pydantic import BaseModel, HttpUrl, Field


class URLIn(BaseModel):
    long_url: HttpUrl = Field(max_length=2048)


class URLOut(BaseModel):
    short_url: HttpUrl