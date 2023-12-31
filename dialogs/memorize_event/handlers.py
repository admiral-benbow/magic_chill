from time import strptime, strftime
from datetime import date, timedelta
import os

from aiogram import types
from aiogram import F

from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import TextInput, MessageInput

from loader import bot, dp
from database.bot_db import BotDB
from dialogs.states import MemorizeEvent


# Starting a Memorize-dialog scenario
@dp.message(F.text == "Memorize an event ✍️️")
async def start_memorizing(message: types.Message, dialog_manager: DialogManager) -> None:
    """Function for starting the MEMORIZING-scenario"""
    await dialog_manager.start(state=MemorizeEvent.date, mode=StartMode.RESET_STACK)


# The 'date' part of Memo-dialog handlers:
async def date_to_places(callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager,
                         *args) -> None:
    """Switching to the Places phase of the Memo-dialog"""
    today = date.today().strftime('%Y-%m-%d')
    dialog_manager.dialog_data["date"] = today

    await dialog_manager.switch_to(MemorizeEvent.places)


async def yesterday_to_places(callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager,
                              *args) -> None:
    """Switching to the Places phase af the Memo-dialog"""
    yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    dialog_manager.dialog_data["date"] = yesterday

    await dialog_manager.switch_to(MemorizeEvent.places)


def date_validation(user_date: str, date_format='%d %m %y') -> None:
    """
    Function to check if the user date is correct
    If it fails, ValueError is raised (in the result of 'strptime' function) and aiogram_dialog type_factory handles it
    """
    valid_date = strptime(user_date, date_format)


async def date_success(message: types.Message, enter: TextInput, dialog_manager: DialogManager, *args) -> None:
    """If the date_input is valid, the func moves to the next part (places) of Memo-dialog"""

    date_from_user = strptime(message.text, "%d %m %y")  # Getting a date from user and converting it for SQlite
    converted_date = strftime("%Y-%m-%d", date_from_user)
    dialog_manager.dialog_data["date"] = converted_date

    await message.answer(text="Great, moving on!")
    await dialog_manager.next()


async def date_failure(message: types.Message, enter: TextInput, dialog_manager: DialogManager, *args) -> None:
    """If the date_input is invalid, the user has to input date again"""
    await message.answer(text="The format of date is incorrect. Please try again")


# The 'places' part of Memo-dialog handlers:
async def places_to_friends(callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager,
                            *args) -> None:
    """Switching to the Friends phase of the Memo-dialog (after choosing any given place)"""
    if callback.data != "another_place":
        dialog_manager.dialog_data["place"] = callback.data.lstrip("places_kb:")
    await dialog_manager.switch_to(MemorizeEvent.friends)


async def place_success(message: types.Message, enter: TextInput, dialog_manager: DialogManager, *args) -> None:
    """Takes another place from the user's input"""
    place_input_widget = dialog_manager.find("place_input_text")
    user_place = place_input_widget.get_value()
    dialog_manager.dialog_data["place"] = user_place

    await message.answer(text="What an interesting place!")
    await dialog_manager.next()


# The 'friends' part of Memo-dialog handlers:
async def friends_to_state(callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager, *args) -> None:
    """
    Function for retrieving data from Widget(Window) - MultiSelector of Friends part of Memo-dialog
    """
    multi_friends_widget = dialog_manager.find("multi_friends")
    multi_friends_data = multi_friends_widget.get_checked()
    dialog_manager.dialog_data["friends"] = multi_friends_data

    await dialog_manager.switch_to(MemorizeEvent.state)


async def friends_to_input(callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager, *args) -> None:
    """
    Switching to text input from choosing friends of Multiselect
    """
    multi_friends_widget = dialog_manager.find("multi_friends")
    multi_friends_data = multi_friends_widget.get_checked()
    dialog_manager.dialog_data["friends"] = multi_friends_data

    await dialog_manager.next()


async def friends_input_success(message: types.Message, enter: TextInput, dialog_manager: DialogManager, *args) -> None:
    """On Friends TextInput success (should be always, though)"""
    friends_input_widget = dialog_manager.find("friends_input_text")
    other_friends = friends_input_widget.get_value().split(";")

    dialog_manager.dialog_data["friends"].extend(other_friends)

    await message.answer("Beautiful people! Let's continue")
    await dialog_manager.next()


# The 'state' part of Memo-dialog handlers
async def state_to_memes(callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager, *args) -> None:
    dialog_manager.dialog_data["state"] = callback.data
    await dialog_manager.next()


# The 'memes' part of Memo-dialog handlers
async def memes_success(message: types.Message, enter: TextInput, dialog_manager: DialogManager, *args) -> None:
    """Input of memes of the event from user - and saving theme to the database"""

    memes_widget = dialog_manager.find("memes_input_text")  # Getting data from user's input
    memes_data = memes_widget.get_value()
    dialog_manager.dialog_data["memes"] = memes_data

    dialog_manager.dialog_data["friends"] = "; ".join(
        dialog_manager.dialog_data.get("friends")
    )
    data = dialog_manager.dialog_data.values()

    with BotDB() as db:
        db.insert_memo_values(message.from_user.id,
                              db.get_new_event_number(message.from_user.id),
                              *data)

    await message.answer("Как кекно\nВсё запомнил!")
    await dialog_manager.next()


# The 'photos' part of Memo-dialog handlers
async def photos_input_got(message: types.Message, enter: MessageInput, dialog_manager: DialogManager, *args) -> None:
    """Input of photos from user and saving them into the database"""

    user_photo = message.photo[-1]
    with BotDB() as db:
        db.add_new_photo(user_id=message.from_user.id,
                         date=dialog_manager.dialog_data["date"],
                         new_photo_id=user_photo.file_id)

        # сделать названия файлов
        uniq_event_id = db.get_exact_event_id(user_id=message.from_user.id,
                                              date=dialog_manager.dialog_data["date"])

    destination_dir = os.path.abspath(os.path.join(os.getcwd(), 'chill_photos'))
    print(destination_dir)

    await bot.download(file=user_photo,
                       destination=fr"{destination_dir}{os.path.sep}{uniq_event_id}_0.jpg")

    await message.answer("Got the photo!")
    await dialog_manager.switch_to(MemorizeEvent.ask_more_photos)


async def memorizing_photo_no(callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager,
                              *args) -> None:
    """If a user doesn't want to add photos, memorizing scenario is ending"""
    await callback.message.answer("You can add photos later anyway\n"
                                  "All in the system, now have a great day and a great life! 🦄")
    await dialog_manager.done()


async def memorizing_more_photo_yes(callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager,
                                    *args) -> None:
    """User agrees to add more photos"""
    await dialog_manager.switch_to(MemorizeEvent.add_more_photos)


async def input_more_photos(message: types.Message, enter: TextInput, dialog_manager: DialogManager, *args) -> None:
    """User decides to add more photos to the event"""

    user_photo = message.photo[-1]
    with BotDB() as db:
        db.add_new_photo(user_id=message.from_user.id,
                         date=dialog_manager.dialog_data["date"],
                         new_photo_id=user_photo.file_id)

        # сделать названия файлов
        uniq_event_id = db.get_exact_event_id(user_id=message.from_user.id,
                                              date=dialog_manager.dialog_data["date"])

        memorized_photos = db.get_photo(user_id=message.from_user.id,
                                        date=dialog_manager.dialog_data["date"])
        if memorized_photos:
            photo_cnt = len(memorized_photos) - 1
        else:
            photo_cnt = 0

    destination_dir = os.path.abspath(os.path.join(os.getcwd(), 'chill_photos'))
    await bot.download(file=user_photo,
                       destination=fr"{destination_dir}{os.path.sep}{uniq_event_id}_{photo_cnt}.jpg")

    await message.answer("Got your new photo")
    await dialog_manager.switch_to(MemorizeEvent.ask_more_photos)


async def memorizing_more_photo_no(callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager,
                                   *args) -> None:
    """User doesn't want to add more photos"""
    await callback.message.answer("Remember everything now!\n"
                                  "Have a great day and a great life! 🦄")
    await dialog_manager.done()


# Transition-handlers
async def next_state(callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager, *args) -> None:
    await dialog_manager.next()


async def date_dialog_done(callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager, *args) -> None:
    await callback.message.answer("Ok, the memorizing process has been aborted\nTo use me again type /start")
    await dialog_manager.done()
