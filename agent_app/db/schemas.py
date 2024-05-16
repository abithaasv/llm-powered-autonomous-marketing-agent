from lancedb.pydantic import Vector, LanceModel
from datetime import date


class PgSchema(LanceModel):
    chunk : int
    detail : str
    text : str
    vector : Vector(384)

class NewsSchema(LanceModel):
    id : str
    date : date
    source : str
    link : str
    content : str
    text : str
    vector : Vector(384)
    overall_similarity : float = None
    is_relevant : int = None
    topics : str = None
    topics_context : str = None


schemas = {
    "pgmain" : PgSchema,
    "news" : NewsSchema,
}