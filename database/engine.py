import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Based
from database.orm_query import orm_banner_description_add, orm_categories_create, orm_banner_all_images_create, orm_banner_delete_all, orm_branches_add_all, orm_delete_branches_info, orm_branches_all_images_create

from common.texts_for_db import categories, description_for_info_pages, currentbranches

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")

databaseurl = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

engine = create_async_engine(databaseurl, echo=True)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Based.metadata.create_all)
        
    async with session_maker() as session:
        await orm_delete_branches_info(session)
        await orm_branches_add_all(session, data=currentbranches)
        # await orm_banner_delete_all(session) # необходимо использовать при добавлении нового баннера
        await orm_categories_create(session, categories)
        await orm_banner_description_add(session, description_for_info_pages)
        await orm_banner_all_images_create(session, 'https://img.freepik.com/free-photo/traditional-russian-pelmeni-dumplings-with-meat_114579-35051.jpg')
        await orm_branches_all_images_create(session, 'https://fastly.4sqi.net/img/general/1398x536/43700824_WZcpm4WrwgH4A7s6BBgcA42GV4lzHalVtAfA5ngwSYo.jpg')


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Based.metadata.drop_all)