from aiogram import types

main = types.ReplyKeyboardMarkup(keyboard=[
    [
        types.KeyboardButton(text='Quote'),
        types.KeyboardButton(text='PicRandom'),
        types.KeyboardButton(text='B..Baka!')
    ],
    [
        types.KeyboardButton(text='Anime Recommendations')
    ]
], resize_keyboard=True, input_field_placeholder='Choose wisely...')

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
