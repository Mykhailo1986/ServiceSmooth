from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class ServiseSmoothState(StatesGroup):
    CHOOSE_LANGUAGE = State() # Define a state to choose language

    CHOOSE_OPTION = State() # Define a state to choose options for the chosen language


