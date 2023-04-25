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


from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

class StateOperator:
    """For working with States"""

    async def gives_from_state(self, state, query):
        """Gives data from state"""
        data = await state.get_data()
        return data.get(query, None)

    async def takes_in_state(self, state, data):
        """Takes data in state . In (key=value) or in dictionary({key: value})"""
        await state.update_data(data)

    async def state(self, state):
        """Gives all datas from state"""
        data = await state.get_data()
        return data


# Create an instance of the StateOperator class
state_operator = StateOperator()

# # Get the state object for the chat_id
# state = await state_operator.fsm.get_state(chat=12345)
#
# # Define a dictionary of key-value pairs to add to the state
# new_data = {"name": "Misha", "age": 25}
#
# # Add the new data to the state
# await state_operator.takes_in_state(state, new_data)