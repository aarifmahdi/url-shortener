from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import URLIn, URLOut
from app.database import get_db
from app.crud import insert_long_url, set_short_code, get_url_by_short_code
from app.utils import convert_to_base62
from app.config import settings


router = APIRouter()


@router.post("/short_url")
async def generate_short_url(url_in: URLIn, session: AsyncSession = Depends(get_db)) -> URLOut:
    long_url_str: str = str(url_in.long_url)
    id: int = await insert_long_url(session, long_url_str)

    try:
        short_code: str = convert_to_base62(id)
    except ValueError:
        raise HTTPException(507, detail="Short code capacity exceeded")

    await set_short_code(session, id, short_code)
    await session.commit()

    short_url = f"{settings.BASE_URL}/{short_code}"
    return URLOut(short_url=short_url)


@router.get("/{short_code}")
async def redirect_to_long_url(short_code: str, session: AsyncSession = Depends(get_db)) -> RedirectResponse:
    long_url: str | None = await get_url_by_short_code(session=session, short_code=short_code)

    if long_url:
        return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")