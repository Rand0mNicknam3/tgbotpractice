from aiogram.types import InputMediaPhoto

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_banner_get,
    orm_categories_get,
    orm_product_get_all_by_category,
    orm_cart_add,
    orm_cart_product_reduce,
    orm_cart_product_delete,
    orm_cart_by_user,
    orm_branches_get_all,
    orm_branch_get_by_name,
    )

from keyboards.inline import (
    get_user_main_buttons,
    get_user_catalog_buttons,
    get_product_buttons,
    get_user_cart_buttons,
    get_user_order_buttons,
    get_user_pickup_buttons,
    get_user_pickupfrom_buttons,
)
from utils.paginator import Paginator
from utils.keyboardmaker import get_keyboard


async def main_menu(session: AsyncSession, level: int, menu_name: str):
    banner = await orm_banner_get(session, name=menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    keyboards = get_user_main_buttons(level=level)
    return image, keyboards


async def catalog(session: AsyncSession, level: int, menu_name: str):
    banner = await orm_banner_get(session, name=menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    categories = await orm_categories_get(session)
    keyboards = get_user_catalog_buttons(level=level+1, categories=categories)
    return image, keyboards


def pages(paginator: Paginator):
    buttons = dict()
    if paginator.has_previous():
        buttons[' Пред.'] = 'previous'
    if paginator.has_next():
        buttons['След. '] = 'next'
    return buttons


async def products(session: AsyncSession, level: int, category: int, page: int):
    products = await orm_product_get_all_by_category(session, category_id=category)
    paginator = Paginator(products, page=page)
    product = paginator.get_page()[0]
    image = InputMediaPhoto(media=product.image, caption=f"<strong>{product.name}</strong>\n\
                            {product.description}\n\
                            Стоимость: {round(product.price, 2)}\n\
                                 <strong>Товар {paginator.page} из {paginator.pages}</strong>")
    pagination_buttons = pages(paginator)
    buttons = get_product_buttons(
        level=level,
        category=category,
        page=page,
        pagination_buttons=pagination_buttons,
        product_id=product.id
    )
    return image, buttons


async def carts(
        session: AsyncSession,
        level: int,
        menu_name: str,
        page: int,
        user_id: int,
        product_id: int,
):
    if menu_name == 'increment':
        await orm_cart_add(session, user_id=user_id, product_id=product_id)
    elif menu_name == 'decrement':
        is_cart = await orm_cart_product_reduce(session, user_id=user_id, product_id=product_id)
        if not is_cart and page > 1:
            page -=1 
    elif menu_name == 'delete':
        await orm_cart_product_delete(session, user_id=user_id, product_id=product_id)
        if page > 1:
            page -= 1
    
    carts = await orm_cart_by_user(session, user_id=user_id)
    if not carts:
        banner = await orm_banner_get(session, name='cart')
        image = InputMediaPhoto(media=banner.image, caption=f'<b>{banner.description}</b>')
        keyboards = get_user_cart_buttons(
            level = level,
            page = None,
            pagingation_buttons = None,
            product_id = None
            )
    else:
        paginator = Paginator(carts, page=page)
        cart = paginator.get_page()[0]
        cart_price = round(cart.quantity * cart.product.price, 2)
        total_price = round(sum(cart.quantity * cart.product.price for cart in carts), 2)
        image = InputMediaPhoto(media=cart.product.image, caption=f"<strong>{cart.product.name}</strong>\n\
                                {cart.product.price}$ x {cart.quantity} = {cart_price}$\
                                 \nТовар {paginator.page} из {paginator.pages} в корзине.\n\
                                 Общая стоимость товаров в корзине {total_price}")

        pagination_buttons = pages(paginator)
        keyboards = get_user_cart_buttons(
            level = level,
            page = page,
            pagingation_buttons = pagination_buttons,
            product_id = cart.product.id
        )

    return image, keyboards

#реплай клавиатура для регистрации

registration_kb = get_keyboard(
    'Поделиться номером',
    'Ввести номер вручную',
    'Назад',
    request_contact=0,
)
    

async def register(session: AsyncSession, level: int, menu_name: str):
    banner = await orm_banner_get(session, name=menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    return image, registration_kb


async def makeorder(session: AsyncSession, level: int, menu_name: str, user_id: int):
    banner = await orm_banner_get(session, name=menu_name)
    if menu_name == 'order':
        order = await orm_cart_by_user(session, user_id=user_id)
        caption = ''
        overall = 0
        for position in order:
           overall += round(position.product.price * position.quantity, 2)
           caption += f'{position.product.name} {position.quantity}шт. {round(position.product.price*position.quantity, 2)}руб\n'
        caption += f'<strong>Общая стоимость: {overall}руб</strong>'
        image = InputMediaPhoto(media=banner.image, caption=caption)
        keyboard = get_user_order_buttons(
            level = level,
            menu_name = menu_name,
         )

    elif menu_name == 'pickup':
        image = InputMediaPhoto(media=banner.image, caption='Выберите пункт выдачи')
        keyboard = get_user_pickup_buttons(
            level = level,
            menu_name = menu_name,
            branches= await orm_branches_get_all(session)
        )


    elif menu_name.startswith('pickfrom_'):
        branch_name = menu_name.split('_')[-1]
        branch = await orm_branch_get_by_name(session, name=branch_name)
        keyboard = get_user_pickupfrom_buttons(level=level, menu_name=menu_name, branch_name=branch.name)
        image = InputMediaPhoto(
            media=branch.image, 
            caption=f'💪<strong>{branch.name}</strong>💪\n\
            😱Прямо по адресу {branch.address}!\n\
            ✨{branch.description}✨')
    return image, keyboard
        

async def get_menu_content(
        session: AsyncSession,
        level: int,
        menu_name: str,
        category: int | None = None,
        page: int | None = None,
        product_id: int | None = None,
        user_id: int | None = None,
):
    if  level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)
    elif level == 3:
        return await carts(session, level, menu_name, page, user_id, product_id)
    elif level == 4:
        return await register(session, level, menu_name)
    elif level == 5:
        return await makeorder(session, level, menu_name, user_id)