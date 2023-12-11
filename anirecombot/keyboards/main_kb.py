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
