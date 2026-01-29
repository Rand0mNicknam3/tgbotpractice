import re

from aiogram import F, types, Router
from aiogram.filters import CommandStart, or_f, StateFilter, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import (
    orm_cart_add,
    orm_cart_delete,
    orm_cart_product_reduce,
    orm_cart_product_delete,
    orm_cart_by_user,
    orm_user_reg_add,
    orm_user_add,
    orm_id_save,
)

# from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from keyboards.inline import MenuCallBack, get_user_main_buttons
from utils.keyboardmaker import get_keyboard


user_private_router = Router()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
    await orm_id_save(session, chat_id=message.chat.id)
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


async def add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = callback.from_user
    await orm_user_add(
        session,
        user_id=callback.from_user.id,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
        phone=None,
    )
    await orm_cart_add(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer('Товар добавлен в корзину')

class Regstate(StatesGroup):
    numberone = State()
    numbertwo = State()


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery, state: FSMContext, callback_data: MenuCallBack, session: AsyncSession):
    if callback_data.menu_name == 'add_to_cart':
        await add_to_cart(callback, callback_data, session)
        return
    
    media, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
    )
    if callback_data.menu_name == 'registration':
        await state.set_state(Regstate.numberone)
        await callback.message.answer(text=media.caption, reply_markup=reply_markup)
        return
    
    
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


@user_private_router.message(Regstate.numberone, F.text == "Ввести номер вручную")
async def user_number(message: types.Message, state: FSMContext):
    await state.set_state(Regstate.numbertwo)
    await message.answer('Введите свой номер в формате +7XXXXXXXXXX (или напишите "назад" чтобы вернуться)', reply_markup=types.ReplyKeyboardRemove())



@user_private_router.message(or_f(Regstate.numberone, Regstate.numbertwo), F.text.casefold() == "назад")
async def back_registration(message: types.Message, state: FSMContext, session: AsyncSession):
    if await state.get_state() == Regstate.numberone:
        media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
        await state.clear()
        await message.answer('Домой...',reply_markup=types.ReplyKeyboardRemove())
        await message.answer_photo(photo=media.media, caption=media.caption, reply_markup=reply_markup)
    else:
        await state.set_state(Regstate.numberone)
        media, reply_markup = await get_menu_content(session, level=4, menu_name="registration")
        await message.answer_photo(photo=media.media, caption=media.caption, reply_markup=reply_markup)


@user_private_router.message(Regstate.numberone, F.text)
async def catch_mistakes1(message: types.Message):
    await message.answer('Выберите опцию из меню')


@user_private_router.message(Regstate.numbertwo, F.text)
async def user_byhand(message: types.Message, state: FSMContext, session: AsyncSession):
    pattern = r"\+7\d{10}"
    if re.match(pattern, message.text):
        await orm_user_reg_add(session, user_id=message.from_user.id, first_name=message.from_user.first_name, last_name=message.from_user.last_name, phone=message.text)
        await state.clear()
        media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
        await message.answer('Номер успешно подтвержден')
        await message.answer_photo(photo=media.media, caption=media.caption, reply_markup=reply_markup)
    else:
        await message.answer('Номер введен некорректно, попробуйте еще раз или введите "назад"\n\
                            Обратите внимание на формат "+79005553535"', reply_markup=types.ReplyKeyboardRemove())
        


@user_private_router.message(Regstate.numberone, F.contact)
async def bot_number(message: types.Message, state: FSMContext):
    if message.contact.user_id == message.from_user.id:
        phone = message.contact.phone_number
        await state.update_data(phone=phone)
        await state.update_data(auto=True)
        keyboard = get_keyboard('Назад', 'Ввести номер вручную', 'Подтвердить номер')
        await message.answer(f'Отлично! Ваш номер - {phone}, если это не так - выберите "Ввести номер вручную"', reply_markup=keyboard)
    else:
        keyboard = get_keyboard('Назад','Ввести номер вручную')
        await message.answer('Мы принимаем только ВАШИ контакты, выберите опцию:')


@user_private_router.message(Regstate.numberone, F.text == "Подтвердить номер")
async def confirm_number(message: types.Message, state: FSMContext, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
    if 'auto' in await state.get_data():
        await state.update_data(
            first_name = message.from_user.first_name,
            last_name = message.from_user.last_name,
            user_id = message.from_user.id,
        )
        data = await state.get_data()
        data.pop('auto')
        await orm_user_reg_add(
            session,
            user_id=data['user_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
        )
        await state.clear()
        await message.answer('Номер успешно подтвержден', reply_markup=types.ReplyKeyboardRemove())
        await message.answer_photo(photo=media.media, caption=media.caption, reply_markup=reply_markup)
    else:
        await message.answer('С добрыми намерениями сюда люди не попадают, пора домой...', reply_markup=types.ReplyKeyboardRemove())
        await message.answer_photo(photo=media.media, caption=media.caption, reply_markup=reply_markup)


class AddUserAddress(StatesGroup):
    address = State()
    comment = State()
    confpayment = State()

@user_private_router.message(or_f(AddUserAddress.address, AddUserAddress.comment, AddUserAddress.confpayment), F.text.casefold() == "назад")
async def step_back_address(message: types.Message, state: FSMContext, session: AsyncSession):
    current_state = await state.get_state()
    if current_state == AddUserAddress.address:
        media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
        await state.clear()
        await message.answer('Домой...',reply_markup=types.ReplyKeyboardRemove())
        await message.answer_photo(photo=media.media, caption=media.caption, reply_markup=reply_markup)
    previous = None
    for step in AddUserAddress.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f'Вы вернулись к предыдущему шагу !\n')
            return
        previous = step

        
@user_private_router.callback_query(F.data.startswith("Delivery_"))
async def askfor_address(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(AddUserAddress.address)
    await callback.answer('',reply_markup=types.ReplyKeyboardRemove())
    await callback.message.answer('Введите введите адрес в текстовом формате (укажите все необходимые для курьера данные!)')


@user_private_router.message(AddUserAddress.address, F.text)
async def add_address(message: types.Message, state: FSMContext, session: AsyncSession):
    if len(message.text) > 200:
        await message.answer('Слишком длинный адрес, попробуйте еще раз')
        return
    else:
        await state.update_data(address=message.text)
        await state.set_state(AddUserAddress.comment)
        await message.answer('Оставьте комметарий для курьера (как вас найти, куда подъехать и тд.)')




@user_private_router.message(AddUserAddress.address)
async def add_address(message: types.Message, state: FSMContext, session: AsyncSession):
    await message.answer('Адрес нужен в текстовом формате, например "улица Петра Смородина, д. 13, кв.6"')


@user_private_router.message(AddUserAddress.comment, F.text)
async def add_address(message: types.Message, state: FSMContext, session: AsyncSession):
    if len(message.text) > 200:
        await message.answer('Слишком длинный адрес, попробуйте еще раз')
        return
    else:
        await state.update_data(comment=message.text)
        await state.set_state(AddUserAddress.confpayment)
        await message.answer('Осталось лишь оплатить :)')
