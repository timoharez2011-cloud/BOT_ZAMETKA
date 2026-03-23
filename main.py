from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv
import os
import asyncio

import db



load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
class AddNoteStates(StatesGroup):
    title = State()
    text = State()
bot = Bot(token=TOKEN)
dp = Dispatcher()



@dp.message(CommandStart())
async def cmd_start(message: Message):
    await bot.send_message(text="""хай,я Bot_zametka!
/help для списка команд""",
        chat_id=message.chat.id,
    )



@dp.message(Command(commands=["note"]))
async def cmd_note(message: Message, state: FSMContext):
    await bot.send_message(
        text="введи название zametky:",
        chat_id=message.chat.id,
    )
    await state.clear()
    await state.set_state(AddNoteStates.title)



@dp.message(StateFilter(AddNoteStates.title))
async def state_title(message: Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(note_title=title)
    await state.set_state(AddNoteStates.text)
    await message.answer("введи текст zametky:")


@dp.message(StateFilter(AddNoteStates.text))
async def state_text(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    title = data.get("note_title")

    await state.clear()
    
    user_id = db.get_or_create_user(message.chat_id, message.from_user.username)

    note_id = db.create_note(user_id, title, text) 

    await message.answer("zametka создана")



@db.message(Command(commands=["list"]))
async def cmd_list(message: Message):
    user_id = db.get_or_create_user(message.chat.id, message.from_user.username)
    notes = db.get_notes(user_id)

    answer = "твои zametka:\n"
    if not notes:
        answer += "тут пусто"
        return
    for id,title,text in notes:
        answer += f"{id}. {title}: {text}\n"
    await message.answer(answer)


@dp.message(Command(commands=["archive_note"]))
async def cmd_arhive(message: Message):
    parts = message.text.split()
    if len(parts) != 2:
        return
    if not parts[1].isnumeric():
        return
    note_id = int(parts[1])

    ok = db.arhive_note(note_id)

    if ok:
        await message.answer("обнова есть")
    else:
        await message.answer("такой ZAMETKA нету")


@dp.message(Command(commands=["delete_note"]))
async def cmd_delete(message: Message):
    parts = message.text.split()
    if len(parts) != 2:
        return
    if not parts[1].isnumeric():
        return
    note_id = int(parts[1])

    ok = db.delete_note(note_id)

    if ok:
        await message.answer("ZAMETKA удалена")
    else:
        await message.answer("такой ZAMETKA нету")


@dp.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    await message.answer("""
команды:
/help - помощь
/note - zametka
/list - список
/archive - сохранить
/delete - удалить
""")


async def main():
    db.init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


