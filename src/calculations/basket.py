# Проверка, что есть хотя бы один выбранный товар
def basket_check_null(basket):
    check = False
    for row in basket:
        if row[1] > 0:
            check = True
            break
    return check

async def total_basket(basket, db):
    total_price = 0
    for row in basket:
        current_price = await db.get_price_in_stock(row[0])
        total_price += current_price * row[1]
    return total_price

