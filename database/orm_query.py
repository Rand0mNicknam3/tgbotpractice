import math
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models import Banner, Cart, Category, Product, User, Chat_ids, Mailings, Branches


async def orm_banner_description_add(session: AsyncSession, data: dict):
    """
    Асинхронно добавляет описания баннеров в базу данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        data (dict): Словарь, содержащий имена баннеров и их описания.

    Возвращает:
        None
    """
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name,description=description) for name, description in data.items()])
    await session.commit()



async def orm_branches_all_images_create(session: AsyncSession, default_image: str):
    """
    Асинхронно обновляет URL-адрес изображения по умолчанию в базе данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для выполнения запроса.
        default_image (str): Новый URL-адрес изображения.

    Возвращает:
        None    
    """
    query = update(Branches).where(Branches.image == None).values(image=default_image)
    await session.execute(query)
    await session.commit()


async def orm_banner_all_images_create(session: AsyncSession, default_image: str):
    """
    Асинхронно обновляет URL-адрес изображения по умолчанию в базе данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для выполнения запроса.
        default_image (str): Новый URL-адрес изображения.

    Возвращает:
        None    
    """
    query = update(Banner).where(Banner.image == None).values(image=default_image)
    await session.execute(query)
    await session.commit()


async def orm_banner_change_image(session: AsyncSession, image: str, name: str):
    """
    Асинхронно обновляет изображение баннера в базе данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для выполнения запроса.
        image (str): Новый URL-адрес изображения.
        name (str): Имя баннера для обновления.

    Возвращает:
        None
    """
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()



async def orm_banner_get_all(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_banner_get(session: AsyncSession, name: str):
    """
    Асинхронно извлекает URL-адрес изображения баннера из базы данных по имени баннера.

    Аругементы:
        session (AsyncSession): Объект AsyncSession для выполнения запроса.
        name (str): Имя баннера, для которого необходимо извлечь URL-адрес изображения.

    Возвращает:
        str: URL-адрес изображения баннера, если баннер найден, в противном случае возвращает None.
    """
    query = select(Banner).where(Banner.name == name)
    result = await session.execute(query)
    return result.scalar()



async def orm_banner_get_all(session: AsyncSession):
    """
    Асинхронно извлекает все URL-адреса изображений баннеров из базы данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для выполнения запроса.

    Возвращает:
        list: Список URL-адресов изображений баннеров.
    """
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_categories_get(session: AsyncSession):
    """
    Асинхронно извлекает все категории из базы данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для выполнения запроса.

    Возвращает:
        list: Список категорий.
    """
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_categories_get_all(session: AsyncSession):
    """
    Асинхронно извлекает все категории из базы данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для выполнения запроса.

    Возвращает:
        list: Список категорий.
    """
    query = select(Category)
    result = await session.execute(query)
    return result

              
async def orm_categories_create(session: AsyncSession, categories: list):
    """
    Асинхронно добавляет категории в базу данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        categories (list): Список категорий для добавления.

    Возвращает:
        None
    """
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories])
    await session.commit()


async def orm_product_add(session: AsyncSession, data: dict):
    """
    Асинхронно добавляет продукт в базу данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        data (dict): Словарь, содержащий данные о продукте.

    Возвращает:
        None
    """
    someobj = Product(
        name = data['name'],
        description = data['description'],
        price = float(data['price']),
        image = data['image'],
        category_id = data['category'],

    )
    session.add(someobj)
    await session.commit()


async def orm_product_get_by_category(session: AsyncSession, category_id: int):
    """
    Асинхронно извлекает продукты из базы данных по идентификатору категории.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для выполнения запроса.
        category_id (int): Идентификатор категории.

    Возвращает:
        list: Список продуктов.
    """

    query = select(Product).where(Product.category_id == int(category_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_product_get(session: AsyncSession, product_id: int):
    """
    Асинхронно извлекает продукт из базы данных по его идентификатору.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для выполнения запроса.
        product_id (int): Идентификатор продукта.

    Возвращает:
        Product: Объект Product, если продукт найден, в противном случае возвращает None.
    """
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalar()

async def orm_product_get_all(session: AsyncSession):
    """
    Асинхронно извлекает все продукты из базы данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для выполнения запроса.

    Возвращает:
        list: Список продуктов.
    """

    query = select(Product)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_product_get_all_by_category(session: AsyncSession, category_id: int):
    """
    Асинхронно извлекает все продукты из базы данных по идентификатору категории.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для выполнения запроса.
        category_id (int): Идентификатор категории.

    Возвращает:
        list: Список продуктов.
    """
    query = select(Product).where(Product.category_id == category_id)
    result = await session.execute(query)
    return result.scalars().all()



async def orm_product_update(session: AsyncSession, product_id: int, data: dict):
    """
    Асинхронно обновляет данные продукта в базе данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        product_id (int): Идентификатор продукта.
        data (dict): Словарь с обновляемыми данными.

    Возвращает:
        None
    """
    query = (
        update(Product)
        .where(Product.id == product_id)
        .values(
            name=data['name'],
            description=data['description'],
            price=float(data['price']),
            category_id=int(data['category']),
            image=data['image'],
        )
    )
    await session.execute(query)
    await session.commit()


async def orm_product_delete(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()


async def orm_user_add(
        session: AsyncSession,
        user_id: int,
        first_name: str | None = None,
        last_name: str  | None = None, 
        phone: str | None = None,
        ):
    """
    Асинхронно добавляет пользователя в базу данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        user_id (int): Идентификатор пользователя.
        first_name (str): Имя пользователя. По умолчанию None.
        last_name (str): Фамилия пользователя. По умолчанию None.
        phone (str): Номер телефона пользователя. По умолчанию None.

    Возвращает:
        None
    """
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(
                user_id = user_id,
                first_name = first_name,
                last_name = last_name,
                phone = phone,
            )
        )
        await session.commit()
    else:
        print('Такой пользователь уже существует')


async def orm_cart_add(session: AsyncSession, user_id: int, product_id: int):
    """
    Асинхронно добавляет продукт в корзину пользователя.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        user_id (int): Идентификатор пользователя.
        product_id (int): Идентификатор продукта.

    Возвращает:
        Cart: Объект Cart, если продукт добавлен в корзину, в противном случае возвращает None.
    """
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()
    if cart:
        cart.quantity += 1
        await session.commit()
        return cart
    else:
        session.add(Cart(
            user_id = user_id,
            product_id = product_id,
            quantity = 1
        ))
        await session.commit()


async def orm_cart_delete(session: AsyncSession, user_id: int, product_id: int):
    """
    Асинхронно удаляет продукт из корзины пользователя.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        user_id (int): Идентификатор пользователя.
        product_id (int): Идентификатор продукта.

    Возвращает:
        None
    """
    query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    await session.execute(query)
    await session.commit()


async def orm_cart_by_user(session: AsyncSession, user_id: int):
    """
    Асинхронно возвращает список продуктов в корзине пользователя.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        user_id (int): Идентификатор пользователя.

    Возвращает:
        list: Список продуктов в корзине пользователя.
    """
    query = select(Cart).filter(Cart.user_id == user_id).options(joinedload(Cart.product))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_cart_product_delete(session: AsyncSession, user_id: int, product_id: int):
    """
    Асинхронно удаляет продукт из корзины пользователя.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        user_id (int): Идентификатор пользователя.
        product_id (int): Идентификатор продукта.

    Возвращает:
        None
    """
    query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    await session.execute(query)
    await session.commit()  



async def orm_cart_product_reduce(session: AsyncSession, user_id: int, product_id: int):
    """
    Асинхронно уменьшает количество продукта в корзине пользователя.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        user_id (int): Идентификатор пользователя.
        product_id (int): Идентификатор продукта.

    Возвращает:
        bool: True, если количество продукта уменьшено, False в противном случае.
    """
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()
    if not cart:
        return
    if cart.quantity > 1:
        cart.quantity -= 1
        await session.commit()
        return True
    else:
        await orm_cart_product_delete(session, user_id, product_id)
        await session.commit()
        return False

async def orm_id_save(session: AsyncSession, chat_id: int):
    """
    Асинхронно сохраняет идентификатор чата в базу данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        chat_id (int): Идентификатор чата.

    Возвращает:
        None
    """
    query = select(Chat_ids).where(Chat_ids.chat_id == chat_id)
    result = await session.execute(query)
    result = result.scalar()
    if not result:
        session.add(Chat_ids(chat_id=chat_id))
    else:
        pass
    await session.commit()

async def orm_get_mailings(session: AsyncSession):
    """
    Асинхронно возвращает список рассылок.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.

    Возвращает:
        list: Список рассылок.
    """
    query = select(Mailings)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_mailings_add(session: AsyncSession, data: dict):
    """
    Асинхронно добавляет рассылку в базу данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        data (dict): Словарь с данными рассылки.

    Возвращает:
        None
    """
    query = select(Mailings)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all(Mailings(name=name) for name in data.values())
    await session.commit()


async def orm_ids_get(session: AsyncSession):
    """
    Асинхронно возвращает список идентификаторов чатов.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.

    Возвращает:
        list: Список идентификаторов чатов.
    """
    query = select(Chat_ids)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_banner_delete_all(session: AsyncSession):
    """
    Асинхронно удаляет все баннеры из базы данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.

    Возвращает:
        None
    """
    query = delete(Banner)
    await session.execute(query)
    await session.commit()


async def orm_user_reg_add(session: AsyncSession, user_id: int, first_name: str, last_name: str, phone: str):
    """
    Асинхронно добавляет пользователя в базу данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        user_id (int): Идентификатор пользователя.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        phone (str): Номер телефона пользователя.

    Возвращает:
        None
    """
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first():
        query = update(User).where(User.user_id == user_id).values(phone=phone)
    else:
        session.add(User(user_id = user_id,
            first_name = first_name,
            last_name = last_name,
            phone = phone,
        ))
    await session.commit()



async def orm_branches_add_all(session: AsyncSession, data: list[dict,dict]):
    """
    Асинхронно добавляет все филиалы в базу данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        data (dict): Словарь с данными филиалов.

    Возвращает:
        None
    """
    query = select(Branches)
    result = await session.execute(query)
    if result.first():
        return
    for pos in data:
        session.add(Branches(name=pos['name'], address=pos['address'], phone=pos['phone'],branch_id=pos['branch_id'],description=pos['description']))
        await session.commit()


async def orm_branches_get_all(session: AsyncSession):
    """
    Асинхронно возвращает список филиалов.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.

    Возвращает:
        list: Список филиалов.
    """
    query = select(Branches)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_branch_get_by_name(session: AsyncSession, name: str):
    """
    Асинхронно возвращает филиал по имени.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.
        name (str): Имя филиала.

    Возвращает:
        dict: Словарь с данными филиала.
    """
    query = select(Branches).where(Branches.name == name)
    result = await session.execute(query)
    return result.scalars().first()

async def orm_delete_branches_info(session: AsyncSession):
    query = delete(Branches)
    await session.execute(query)
    await session.commit()
    """
    Асинхронно удаляет все филиалы из базы данных.

    Аргументы:
        session (AsyncSession): Объект AsyncSession для обмена данными с базой данных.

    Возвращает:
        None
    """