from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class ServiseSmoothState(StatesGroup):
    CHOOSE_LANGUAGE = State()  # Define a state to choose language
    CHOOSE_OPTION = State()  # Define a state to choose options for the chosen language
    CHOOSE_lOOK =State()


class FirstRegistration(StatesGroup):
    START_REG = State()  # Here is I save the language_code
    F_NAME_REG = State()
    L_NAME_REG = State()
    TEL_REG = State()
    EMAIL_REG = State()
    END_REG = State()

class Booking(StatesGroup):
    START_BOOK = State()  # Here is I save the language_code
    SEL_Spec = State()
    SEL_Place = State()
    SEL_Proc = State()
    SEL_Date = State()
    SEL_Time = State()
    END_BOOK = State()