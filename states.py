from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class ServiseSmoothState(StatesGroup):
    CHOOSE_LANGUAGE = State() # Define a state to choose language

    CHOOSE_OPTION = State() # Define a state to choose options for the chosen language

class FirstRegistration(StatesGroup):
    START_REG = State() # Here is I save the language_code
    F_NAME_REG = State()
    L_NAME_REG = State()
    TEL_REG = State()
    EMAIL_REG = State()
