from sqlalchemy.ext.asyncio import AsyncSession
from app.models import URLMapper
from sqlalchemy import select


async def insert_long_url(session: AsyncSession, long_url: str) -> int:
    row = URLMapper(long_url=long_url)
    session.add(row)
    await session.flush()
    return row.id


async def set_short_code(session: AsyncSession, id: int, short_code: str) -> None:
    result = await session.execute(select(URLMapper).where(URLMapper.id==id)) 
    row = result.scalar_one() 
    row.short_code = short_code 
    await session.flush()


async def get_url_by_short_code(session: AsyncSession, short_code: str) -> str | None:
    result = await session.execute(select(URLMapper).where(URLMapper.short_code==short_code))
    row = result.scalar_one_or_none()
    if not row:
        return
    return row.long_url