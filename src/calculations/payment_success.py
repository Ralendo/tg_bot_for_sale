async def bought_tickets(basket, db):
    # Вычитаем из доступного количества билетов купленные
    for row in basket:
        product_count = await db.get_count_in_stock(row[0])
        product_count -= row[1]
        await db.update_count_in_stock(product_count, row[0])
