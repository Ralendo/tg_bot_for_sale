import string
import random


# Обновление слова "Билет" в магазине
def update_word(count):
    f1 = 'билет'
    f2 = 'билета'
    f5 = 'билетов'

    if count == 0:
        return '...'

    n = abs(count) % 100
    if 19 >= n >= 11:
        return f5

    n1 = n % 10
    if n1 == 1:
        return f1

    if 5 > n1 > 1:
        return f2

    return f5

# Вспомогательная под update_word_total
def update_word_total_helper(f1, f2, word):
    return f"{f1} {word} {f2}"

def update_word_total(row):
    if row[0] == '1Ticket':
        if row[1] == 1:
            return update_word_total_helper(row[1], update_word(row[1]), 'обычный')
        elif row[1] > 1:
            return update_word_total_helper(row[1], update_word(row[1]), 'обычных')
    elif row[0] == 'VIP':
        return update_word_total_helper(row[1], update_word(row[1]), 'VIP-')
    elif row[0] == '4+1':
        return update_word_total_helper(row[1], update_word(row[1]), '"4+1"')

def basket_content(basket, discount, pull_price):
    temp = ''
    i = -1
    for row in basket:
        i += 1
        if row[1] > 0:
            if temp == '':
                temp = '\nСейчас у тебя в корзине:'
            temp += f'\n• {update_word_total(row)} на сумму <b>{pull_price[i]} ₽</b>'
    if discount > 0:
        temp += f'\nАктивирован промокод: <b>- {discount} ₽</b>!'
    return temp

def create_label():
    # Создаём label для транзакции
    letter_and_numbers = string.ascii_lowercase + string.digits
    random_string = ''.join(random.sample(letter_and_numbers, 20))
    return random_string

def create_free_label(name):
    # Создаём label для проходок
    letter_and_numbers = string.ascii_lowercase + string.digits
    random_string = ''.join(random.sample(letter_and_numbers, 20))
    random_string = str(name) + random_string
    return random_string

def create_label_promocode():
    # Создаём label для промокодов:
    letter_and_numbers = string.ascii_lowercase + string.digits
    random_string = ''.join(random.sample(letter_and_numbers, 12))
    return random_string


# Словарь названий продуктов
def return_declension_of_product_name(word):
    name_of_products = {
        '1Ticket': 'Обычный',
        'VIP': 'ВИП',
        '4+1': '4+1'
    }
    return name_of_products[word]
