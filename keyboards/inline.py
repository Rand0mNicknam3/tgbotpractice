from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_callback_buttons(*, buttons: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for name, id in buttons.items():
        keyboard.add(InlineKeyboardButton(text=name, callback_data=id))
    return keyboard.adjust(*sizes).as_markup()


class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None


def get_user_main_buttons(*,level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    buttons = {
        "Товары": "catalog",
        "Корзина": "cart",
        'О нас': "about",
        "Оплата": "payment",
        "Доставка": "shipping",
        "Регистрация": "registration",
    }
    for text, menu_name in buttons.items():
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text,callback_data=MenuCallBack(level = level + 1, menu_name = menu_name).pack()))
        elif menu_name == 'cart':
            keyboard.add(InlineKeyboardButton(text=text,callback_data=MenuCallBack(level = 3, menu_name=menu_name).pack()))
        elif menu_name == 'registration':
            keyboard.add(InlineKeyboardButton(text=text,callback_data=MenuCallBack(level = 4, menu_name = menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,callback_data=MenuCallBack(level = level, menu_name = menu_name).pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_user_catalog_buttons(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for cat in categories:
        keyboard.add(InlineKeyboardButton(text=cat.name, callback_data=MenuCallBack(level = 2, menu_name = cat.name, category=cat.id).pack()))
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data=MenuCallBack(level = 0, menu_name = "main").pack()))
    keyboard.add(InlineKeyboardButton(text="В корзину", callback_data=MenuCallBack(level = 3, menu_name = "cart").pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_product_buttons(
        *,
        level: int,
        category: int,
        page: int,
        pagination_buttons: dict[str:str],
        product_id: int,
        sizes: tuple[int] = (2,)
):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Корзина', callback_data=MenuCallBack(level = 3, menu_name = "cart").pack()))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level = level - 1, menu_name = "catalog").pack()))
    keyboard.add(InlineKeyboardButton(text='Купить', callback_data=MenuCallBack(level = level, menu_name = "add_to_cart", product_id=product_id).pack()))

    keyboard.adjust(*sizes)

    row = []


    for text, menu_name in pagination_buttons.items():
        if menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,callback_data=MenuCallBack(
                level = level,
                menu_name = menu_name,
                category = category,
                page = page - 1,).pack()
                ))
        elif menu_name == "next":
            row.append(InlineKeyboardButton(text=text, callback_data=MenuCallBack(
                level = level,
                menu_name = menu_name,
                category= category,
                page = page + 1,).pack()
                ))
    return keyboard.row(*row).as_markup()


def get_user_cart_buttons(
        *,
        level: int,
        page: int,
        pagingation_buttons: dict[str:str],
        product_id: int,
        sizes: tuple[int] = (3,)
        ):
    keyboard = InlineKeyboardBuilder()
    if page:
        keyboard.add(InlineKeyboardButton(text='+1', callback_data=MenuCallBack(
            level = level,
            menu_name='increment',
            product_id=product_id,
            page=page,
        ).pack()))
        keyboard.add(InlineKeyboardButton(text='-1', callback_data=MenuCallBack(
            level = level,
            menu_name='decrement',
            product_id=product_id,
            page=page,
        ).pack()))
        keyboard.add(InlineKeyboardButton(text='Удалить', callback_data=MenuCallBack(
            level = level,
            menu_name='delete',
            product_id=product_id,
            page=page,
        ).pack()))
        keyboard.adjust(*sizes)
    
        row = []
        for text, menu_name in pagingation_buttons.items():
            if menu_name == 'previous':
                row.append(InlineKeyboardButton(text=text, callback_data=MenuCallBack(
                    level = level,
                    menu_name=menu_name,
                    page=page-1
                ).pack()))
            elif menu_name == 'next':
                row.append(InlineKeyboardButton(text=text, callback_data=MenuCallBack(
                    level = level,
                    menu_name=menu_name,
                    page=page+1,
                ).pack()))
        keyboard.row(*row)
        secondrow = [
                InlineKeyboardButton(text='На главную', callback_data=MenuCallBack(
                    level = 0,
                    menu_name='main'
                ).pack()),
                InlineKeyboardButton(text='Купить', callback_data=MenuCallBack(
                    level = 5,
                    menu_name = 'order'
                ).pack())
            ]
        keyboard.row(*secondrow)
        return keyboard.as_markup()
    else:
        row_for_fun = []
        row_for_fun.append(InlineKeyboardButton(text='На главную', callback_data=MenuCallBack(
            level = 0,
            menu_name='main'
        ).pack()))
        return keyboard.row(*row_for_fun).as_markup()
    

def get_user_order_buttons(*, level: int, menu_name: str, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    buttons = [
        [InlineKeyboardButton(text="Самовывоз", callback_data=MenuCallBack(
            level = level,
            menu_name = 'pickup',
        ).pack())],
        [
            InlineKeyboardButton(text="Доставка", callback_data='Delivery_address'),
            InlineKeyboardButton(text="Назад", callback_data=MenuCallBack(
                level = 3,
                menu_name = 'cart',
            ).pack()),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_user_pickup_buttons(*, level: int, menu_name: str, sizes: tuple[int] = (2,), branches: list):
    keyboard = InlineKeyboardBuilder()
    for branch in branches:
        keyboard.add(InlineKeyboardButton(text=f'{branch.name}({branch.address})', callback_data=MenuCallBack(
            level = level,
            menu_name = f'pickfrom_' + branch.name,
        ).pack()))
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data=MenuCallBack(
        level = level,
        menu_name = 'order',
    ).pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_user_pickupfrom_buttons(*, level: int, branch_name: str, menu_name: str, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data=MenuCallBack(
        level = level,
        menu_name = 'pickup',
    ).pack()))
    keyboard.add(InlineKeyboardButton(text='Оплатить', callback_data=MenuCallBack(
        level = 0,
        menu_name = 'payment', 
    ).pack()))
    return keyboard.adjust(*sizes).as_markup()