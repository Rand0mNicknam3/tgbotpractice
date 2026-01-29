from aiogram import F, types, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import (
    orm_banner_change_image,
    orm_categories_get,
    orm_product_get_by_category,
    orm_product_delete,
    orm_banner_get_all,
    orm_product_get,
    orm_product_update,
    orm_product_add,
    orm_ids_get,
)

from keyboards.inline import get_callback_buttons
from filters.customfilters import ChatTypeFilter, BossFilter
from utils.keyboardmaker import get_keyboard


admin_private_router = Router()
admin_private_router.message.filter(ChatTypeFilter(["private"]), BossFilter())


admin_keyboard = get_keyboard(
    'Добавить товар',
    'Ассортимент',
    'Добавить/Изменить баннер',
    'Общая рассылка',
    placeholder="Выберите действие",
    sizes=(2,),
)

@admin_private_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=admin_keyboard)


@admin_private_router.message(F.text == "Ассортимент")
async def admin_assortment(message: types.Message, session: AsyncSession):
    categories = await orm_categories_get(session)
    buttons = {category.name : f'category_{category.id}' for category in categories}
    await message.answer('Выберите категорию:', reply_markup=get_callback_buttons(buttons=buttons))


@admin_private_router.callback_query(F.data.startswith('category_'))
async def products_by_category(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split('_')[-1]
    allproducts = await orm_product_get_by_category(session, category_id=category_id)
    for product in allproducts:
        await callback.message.answer_photo(
            product.image,
            caption=f'<strong>{product.name}</strong>\n\n{product.description}\nСтоимость: {round(product.price, 2)}₽',
        reply_markup=get_callback_buttons(buttons={'Удалить': f'delete_{product.id}','Изменить': f'change_{product.id}',}, sizes=(2,)))
    await callback.answer()
    await callback.message.answer("А вот и списочек товаров!")


@admin_private_router.callback_query(F.data.startswith('delete_'))
async def delete_product(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split('_')[-1]
    await orm_product_delete(session, int(product_id))
    await callback.answer()
    await callback.message.answer("Товар был удален!")


#FSM BANNERS

class AddChangeBanner(StatesGroup):
    image = State()


@admin_private_router.message(StateFilter(None), F.text == 'Добавить/Изменить баннер')
async def askfor_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    banner_names =[banner.name for banner in await orm_banner_get_all(session)]
    await message.answer(f'Отправьте фотографию баннера,\nВ описании укажите какой именно баннер добавляете!\nТекущие баннеры: {banner_names}')
    await state.set_state(AddChangeBanner.image)


@admin_private_router.message(AddChangeBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    banner_name = message.caption.strip()
    allbanners = [banner.name for banner in await orm_banner_get_all(session)]
    if banner_name not in allbanners:
        await message.answer(f'Введите название баннера корректно, список баннеров: {allbanners}')
        return
    await orm_banner_change_image(session, image_id, banner_name)
    await message.answer('Дело сделано!')
    await state.clear()


@admin_private_router.message(AddChangeBanner.image)
async def add_banner2(message: types.Message, state: FSMContext):
    await message.answer("Отправьте ФОТО баннера, либо 'отмена'")


#FSM PRODUCTS


class AddChangeProduct(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()

    product_for_change = None

    texts = {
        "AddChangeProduct:name": "Введите название снова:",
        "AddChangeProduct:description": "Введите описание снова:",
        "AddChangeProduct:category": "Выберите категорию  снова:",
        "AddChangeProduct:price": "Введите стоимость снова(в пределах 99999.99):",
        "AddChangeProduct:image": "1kla$Legenda",
    }


@admin_private_router.message(StateFilter(None), F.text == 'Добавить товар')
async def askfor_product_name(message: types.Message, state: FSMContext):
    await message.answer("Отправьте название товара", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddChangeProduct.name)


@admin_private_router.message(StateFilter("*"), F.text.casefold() == "отмена")
@admin_private_router.message(StateFilter("*"), Command("отмена"))
async def cancel_adding(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddChangeProduct.product_for_change is None:
        AddChangeProduct.product_for_change = None
    await state.clear()
    await message.answer("Действия отменены!", reply_markup=admin_keyboard)

@admin_private_router.message(StateFilter("*"), or_f(Command("назад"), F.text.casefold() == "назад"))
async def step_back(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AddChangeProduct.name:
        await message.answer("ОТСТУПАТЬ НЕКУДА-ПОЗАДИ МОСКВА(для отмены напишите 'отмена')")
        return
    previous = None
    for step in AddChangeProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f'Вы вернулись к предыдущему шагу\n{AddChangeProduct.texts[previous.state]}')
            return
        previous = step


@admin_private_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_productCB(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    product_id = int(callback.data.split('_')[1])
    target_product = await orm_product_get(session, product_id)
    AddChangeProduct.product_for_change = target_product
    await callback.answer()
    await callback.message.answer(
        "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddChangeProduct.name)


@admin_private_router.message(AddChangeProduct.name, F.text)
async def add_product_name(message: types.Message, state: FSMContext):
    if message.text == '.' and AddChangeProduct.product_for_change:
        await state.update_data(name=AddChangeProduct.product_for_change.name)
    else:
        if len(message.text) >= 145 or len(message.text) <= 4:
            await message.answer('ОШИБКА! Название должно быть от 5 до 144 символов !')
            return
        await state.update_data(name=message.text)
    await message.answer('Введите описание товара')
    await state.set_state(AddChangeProduct.description)


@admin_private_router.message(AddChangeProduct.name)
async def catch_mistake(message: types.Message, state: FSMContext):
    await message.answer('Неверное введено название, попробуйте снова(в текстовом формате)')


@admin_private_router.message(AddChangeProduct.description, F.text)
async def add_descrption(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == '.' and AddChangeProduct.product_for_change:
        await state.update_data(description=AddChangeProduct.product_for_change.description)
    else:
        if len(message.text) < 3:
            await message.answer('Слишком короткое описание ;(')
            return
        await state.update_data(description=message.text)
    categories = await orm_categories_get(session)
    dictforbuttons = {category.name : str(category.id) for category in categories}
    await message.answer('Выберите категорию из представленных:', reply_markup=get_callback_buttons(buttons=dictforbuttons))
    await state.set_state(AddChangeProduct.category)


@admin_private_router.message(AddChangeProduct.description)
async def catch_mistake2(message: types.Message, state: FSMContext):
    await message.answer('ОШИБКА! Введите описание в текстовом формате')


@admin_private_router.callback_query(AddChangeProduct.category)
async def add_category(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    category_id = int(callback.data)
    if category_id in [category.id for category in await orm_categories_get(session)]:
        await state.update_data(category=category_id)
        await callback.message.answer('Введите стоимость(в пределах 99999.99)')
        await state.set_state(AddChangeProduct.price)
    else:
        await callback.answer('тыкните по кнопке с категорией как следует!')


@admin_private_router.message(AddChangeProduct.category)
async def catch_mistake3(message: types.Message, state: FSMContext):
    await message.answer('Тыкайте по кнопкам в панели!')


@admin_private_router.message(AddChangeProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    if message.text == '.' and AddChangeProduct.product_for_change:
        await state.update_data(price=AddChangeProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer('Введите валидное значение стоимости')
            return
        await state.update_data(price=message.text)
    await message.answer('Загрузите изображение')
    await state.set_state(AddChangeProduct.image)


@admin_private_router.message(AddChangeProduct.price)
async def catch_mistake4(message: types.Message, state: FSMContext):
    await message.answer('Вы ввели недоступное значение, попробуйте снова')


@admin_private_router.message(AddChangeProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == '.' and AddChangeProduct.product_for_change:
        await state.update_data(image=AddChangeProduct.product_for_change.image)
    elif message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await message.answer('Это не изображение, попробуйте снова')
        return
    data = await state.get_data()
    try:
        if AddChangeProduct.product_for_change:
            await orm_product_update(session, AddChangeProduct.product_for_change.id, data=data)
            await message.answer('Товар успешно изменен !', reply_markup=admin_keyboard)
        else:
            await orm_product_add(session, data=data)
            await message.answer('Товар успешно добавлен !', reply_markup=admin_keyboard)
        await state.clear()
    except Exception as e:
        await message.answer(f'Произошла ошибка: {e} ! ! ! ')
    AddChangeProduct.product_for_change = None

@admin_private_router.message(AddChangeProduct.image)
async def catch_mistake5(message: types.Message, state: FSMContext):
    await message.answer('Это не изображение, попробуйте снова')



class SendMailings(StatesGroup):
    mail_text = State()


@admin_private_router.message(StateFilter(None), F.text == 'Общая рассылка')
async def mailings(message: types.Message, state: FSMContext):
    await message.answer('Напишите текст рассылки')
    await state.set_state(SendMailings.mail_text)


@admin_private_router.message(SendMailings.mail_text)
async def send_mailings(message: types.Message, state: FSMContext, session: AsyncSession):
    custs_ids = await orm_ids_get(session)
    for cust_id in custs_ids:
        await message.bot.send_message(chat_id=cust_id.chat_id, text=message.text)
    await message.answer('Рассылка успешно отправлена!')
    await state.clear()