from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import URLIn, URLOut
from app.database import get_db
from app.crud import insert_long_url, set_short_code
from app.utils import convert_to_base62
from app.config import settings


router = APIRouter()


async def db_connection():
    db = get_db()
    return await anext(db)


@router.post("/short_urls")
async def generate_short_url(url_in: URLIn, session: AsyncSession = Depends(db_connection)) -> URLOut:
    long_url_str: str = str(url_in.long_url)
    id: int = await insert_long_url(session, long_url_str)

    try:
        short_code: str = convert_to_base62(id)
    except ValueError:
        raise HTTPException(507, detail="Short code capacity exceeded.")

    await set_short_code(session, id, short_code)
    await session.commit()

    short_url = f"{settings.BASE_URL}/{short_code}"
    return URLOut(short_url=short_url)