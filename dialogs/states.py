from aiogram.filters.state import State, StatesGroup


class MemorizeEvent(StatesGroup):
    """
    FSM-class for Memorizing an event (a meeting with friends)---scenario
    For aiogram-dialogs also
    """
    date = State()
    date_input = State()

    places = State()
    places_input = State()

    friends = State()
    friends_input = State()

    state = State()
    memes = State()

    photos = State()
    photos_input = State()
    ask_more_photos = State()
    add_more_photos = State()


class RememberEvent(StatesGroup):
    """
    FSM-class for remembering an event -> to look into written events
    """
    choose_state = State()
    event_dates = State()
    the_event = State()

    change_event = State()
    memes_input = State()
    ppl_input = State()
    places_input = State()

    photos_input = State()
    ask_more_photos = State()

    event_delete_assure = State()


class Ricquotes(StatesGroup):
    """
    FSM-class for accessing and using of the 'Quotes of'-scenario
    -> Ricquotes: both -memorizing- & -remembering-
    """
    start_memorizing = State()
