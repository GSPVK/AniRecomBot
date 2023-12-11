from aiogram import types

select_category = types.ReplyKeyboardMarkup(keyboard=[
    [
        types.KeyboardButton(text='SFW'),
        types.KeyboardButton(text='NSFW'),
        types.KeyboardButton(text='I WANT EVERYTHING!')
    ],
    [
        types.KeyboardButton(text='Go back')
    ]
], resize_keyboard=True, input_field_placeholder='Choose SUPER wisely...')

all_categories = types.ReplyKeyboardMarkup(keyboard=[
    [
        types.KeyboardButton(text='Select all'),
    ],
    [
        types.KeyboardButton(text='Back to categories'),
        types.KeyboardButton(text='Main Menu')
    ]
], resize_keyboard=True)

one_category = types.ReplyKeyboardMarkup(keyboard=[
    [
        types.KeyboardButton(text='Get picture'),
    ],
    [
        types.KeyboardButton(text='Back to categories'),
        types.KeyboardButton(text='Main Menu')
    ]
], resize_keyboard=True)

both_categories = types.ReplyKeyboardMarkup(keyboard=[
    [
        types.KeyboardButton(text='SFW'),
        types.KeyboardButton(text='NSFW'),
    ],
    [
        types.KeyboardButton(text='Back to categories'),
        types.KeyboardButton(text='Main Menu')
    ]
], resize_keyboard=True)
