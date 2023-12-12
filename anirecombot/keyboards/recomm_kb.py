from aiogram import types

scroll_recs = types.ReplyKeyboardMarkup(keyboard=[
    [
        types.KeyboardButton(text='Next'),
        types.KeyboardButton(text='Main Menu'),
        types.KeyboardButton(text='Update recs')
    ],
], resize_keyboard=True)

go_back = types.ReplyKeyboardMarkup(keyboard=[
    [
        types.KeyboardButton(text='Go back')
    ],
], resize_keyboard=True)

go_back_while_generating = types.ReplyKeyboardMarkup(keyboard=[
    [
        types.KeyboardButton(text='Go back')
    ],
], resize_keyboard=True, input_field_placeholder='Our waifus are working on it!')
