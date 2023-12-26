from src.config import Config
from datetime import datetime

import random

from sqlalchemy import create_engine, and_
from sqlalchemy.sql.expression import literal
from sqlalchemy.orm import sessionmaker, load_only
from src.create_db import Users, Products, Tickets, TicketNames, Buyers, PromoCodes
from src.calculations.words import create_label_promocode


def row_exists(s, table, table_column, search):  # session, name_table, where table.column, what search
    return s.query(literal(True)).filter(s.query(table).filter(table_column == search).exists()).scalar()

def row_first(s, table, table_column, search):
    return s.query(table).filter(table_column == search).first()

def row_one(s, table, table_column, search):
    return s.query(table).filter(table_column == search).one()

def row_all(s, table, table_column, search):
    return s.query(table).filter(table_column == search).all()


def session_end(s):
    s.commit()
    s.close()


class DataBase:
    def __init__(self):
        connection_name = Config.db_connection
        engine = create_engine(connection_name,
                               echo=False,
                               pool_size=20,
                               max_overflow=20,
                               pool_recycle=3600,
                               pool_pre_ping=True)
        engine.dialect.supports_unicode_statements = True

        self.session = sessionmaker(bind=engine)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close_all()

    """Таблица users"""
    async def exist_user(self, user_id):
        s = self.session()
        output = row_exists(s, Users, Users.user_id, user_id)
        session_end(s)
        return output

    async def add_users(self, user_id, firstname, surname, nickname):
        s = self.session()
        new_user = Users(firstname=firstname, surname=surname, nickname=nickname, user_id=user_id, role='user')
        s.add(new_user)
        session_end(s)

    async def get_permission_status(self, user_id):
        s = self.session()
        data = row_one(s, Users, Users.user_id, user_id)
        output = data.role
        session_end(s)
        return output

    async def get_users_for_role(self, role):
        s = self.session()
        output = ''
        data = row_all(s, Users, Users.role, role)
        for row in data:
            output += f'{row.user_id} с именем "{row.firstname}"\n'
        output = output[:-1]
        session_end(s)
        return output

    async def update_role_of_user(self, user_id, role):
        s = self.session()
        s.query(Users). \
            filter(Users.user_id == f'{user_id}'). \
            update({'role': role})
        session_end(s)

    async def get_list_users(self):
        s = self.session()
        data = s.query(Users).all()
        output = []
        for row in data:
            output.append(int(row.user_id))
        session_end(s)
        return output

    """ Таблица buyer """
    async def add_user_to_buyers(self, user_id, label, price):
        s = self.session()
        user = row_first(s, Users, Users.user_id, user_id)
        new_buyer = Buyers(label=label, user=user, price=price, date_time=datetime.now())
        s.add(new_buyer)
        session_end(s)

    async def get_list_buyers(self):
        s = self.session()
        data = s.query(Buyers).all()
        output = []
        for row in data:
            output.append(int(row.user_id))
        session_end(s)
        return output

    async def get_labels_from_buyers(self, user_id):
        s = self.session()
        output = []
        data = row_all(s, Buyers, Buyers.user_id, user_id)
        for row in data:
            output.append(row.label)
        session_end(s)
        return output

    async def get_last_label_from_buyers(self, user_id):
        s = self.session()
        try:
            #TODO доделать запрос, чтоб шёл к тому, что у юзера нет ticket_photo_id
            data = s.query(Buyers).filter(Buyers.user_id == f'{user_id}').order_by(Buyers.id.desc()).first()
            label = data.label
        except Exception as e:
            label = None
        session_end(s)
        return label

    async def update_photo_id(self, ticket_photo_id, label):
        s = self.session()
        s.query(Buyers). \
            filter(Buyers.label == f'{label}'). \
            update({'ticket_photo_id': ticket_photo_id})
        session_end(s)

    async def check_exist_label_in_table(self, label):
        s = self.session()
        output = row_exists(s, Buyers, Buyers.label, label)
        session_end(s)
        return output

    async def count_buyers(self):
        s = self.session()
        output = s.query(Buyers).count()
        session_end(s)
        return output

    async def join_to_lottery(self, user_id):
        s = self.session()
        s.query(Users). \
            filter(Users.user_id == f'{user_id}'). \
            update({'lottery': True})
        session_end(s)

    async def stop_the_lottery(self):
        s = self.session()
        data = row_all(s, Users, Users.lottery, True)
        user_id_list = []
        for row in data:
            user_id_list.append(row.user_id)
        random.shuffle(user_id_list)
        session_end(s)
        return user_id_list[0:2]



    """ Таблица tickets """
    async def add_ticket(self, basket, label):
        s = self.session()
        buyer = row_first(s, Buyers, Buyers.label, label)
        for row in basket:
            if row[1] > 0:
                x = 1
                if row[0] == '4+1':
                    x = 5
                new_ticket = Tickets(buyer=buyer, product_name=row[0], product_count=row[1]*x,
                                     not_distributed_tickets=row[1]*x)
                s.add(new_ticket)
        session_end(s)

    async def add_one_ticket(self, basket, label):
        s = self.session()
        buyer = row_first(s, Buyers, Buyers.label, label)
        for row in basket:
            new_ticket = Tickets(buyer=buyer, product_name=row[0], product_count=row[1],
                                 not_distributed_tickets=0)
            s.add(new_ticket)
        session_end(s)

    async def get_count_from_tickets(self, product_name, label):
        s = self.session()
        data = s.query(Tickets).filter(
            and_(Tickets.label == f'{label}', Tickets.product_name == f'{product_name}')).first()
        output = data.not_distributed_tickets
        session_end(s)
        return output

    async def update_count_in_buyers(self, count, product_name, label):
        s = self.session()
        s.query(Tickets). \
            filter(and_(Tickets.label == f'{label}', Tickets.product_name == f'{product_name}')). \
            update({'not_distributed_tickets': count})
        session_end(s)

    async def get_count_types_of_products(self, label):
        s = self.session()
        output = s.query(Tickets). \
            filter(and_(Tickets.label == f'{label}', Tickets.not_distributed_tickets > 0)).count()
        session_end(s)
        return output

    async def get_product_name_first(self, label):
        s = self.session()
        data = s.query(Tickets).filter(and_(Tickets.label == label, Tickets.not_distributed_tickets > 0)).first()
        output = data.product_name
        session_end(s)
        return output

    async def get_product_name_all(self, label):
        s = self.session()
        output = []
        data = row_all(s, Tickets, Tickets.label, label)
        for row in data:
            output.append(row.product_name)
        session_end(s)
        return output

    async def get_photo_id(self, label):
        s = self.session()
        data = row_one(s, Buyers, Buyers.label, label)
        output = data.ticket_photo_id
        session_end(s)
        return output

    async def get_ticket_id(self, label, product_name):
        s = self.session()
        data = s.query(Tickets). \
            filter(and_(Tickets.label == f"{label}", Tickets.product_name == product_name)).one()
        output = data.id
        session_end(s)
        return output

    async def check_exist_non_distributed_tickets(self, user_id):
        try:
            labels = await self.get_labels_from_buyers(user_id)
            for label in labels:
                output = await self.get_count_types_of_products(label)
                if output > 0:
                    return True
        except Exception:
            return False
        return False

    async def count_by_types_tickets(self):
        s = self.session()

        # Суммируем количество товара
        data_1Ticket = s.query(Tickets).filter(Tickets.product_name == '1Ticket').with_entities(Tickets.product_count).all()
        data_1Ticket = sum(count for count, in data_1Ticket)

        data_4_1 = s.query(Tickets).filter(Tickets.product_name == '4+1').with_entities(Tickets.product_count).all()
        data_4_1 = sum(count for count, in data_4_1)

        session_end(s)
        return data_4_1, data_1Ticket



    """Таблица TicketNames"""
    async def add_ticket_name(self, ticket_id, name):
        s = self.session()
        ticket = row_first(s, Tickets, Tickets.id, ticket_id)
        new_name = TicketNames(ticket=ticket, name=name)
        s.add(new_name)
        session_end(s)

    async def check_exist_ticket(self, label):
        s = self.session()
        output = row_exists(s, Tickets, Tickets.label, label)
        session_end(s)
        return output

    async def get_ticket_names(self, label):
        s = self.session()
        output = []
        tickets = row_all(s, Tickets, Tickets.label, label)
        for ticket in tickets:
            ticket_id = ticket.id
            data = row_all(s, TicketNames, TicketNames.ticket_id, ticket_id)
            for row in data:
                output.append(row.name)
        session_end(s)
        return output

    async def get_ticket_names_for_checker(self, label):
        s = self.session()
        output = []
        tickets = row_all(s, Tickets, Tickets.label, label)
        for ticket in tickets:
            ticket_id = ticket.id
            data = s.query(TicketNames).\
                filter(and_(TicketNames.ticket_id == f'{ticket_id}', TicketNames.check == False)).all()
            for row in data:
                output.append(row.name)
        session_end(s)
        return output

    async def update_ticket_name_check(self, label, name):
        s = self.session()
        tickets = row_all(s, Tickets, Tickets.label, label)
        for ticket in tickets:
            ticket_id = ticket.id
            check = s.query(TicketNames)\
                .filter(and_(TicketNames.ticket_id == f'{ticket_id}', TicketNames.name == f'{name}')).first()
            if check:
                s.query(TicketNames)\
                    .filter(and_(TicketNames.ticket_id == f'{ticket_id}', TicketNames.name == f'{name}'))\
                    .update({'check': True})
                break
        session_end(s)


    """ Таблица product """
    async def get_count_in_stock(self, name):
        s = self.session()
        data = row_one(s, Products, Products.name, name)
        output = data.count
        session_end(s)
        return output

    async def get_price_in_stock(self, name):
        s = self.session()
        data = row_one(s, Products, Products.name, name)
        output = data.price
        session_end(s)
        return output

    async def get_names_of_product(self):
        s = self.session()
        data = s.query(Products).all()
        output = []
        for i in data:
            output.append(i.name)
        session_end(s)
        return output

    async def update_count_in_stock(self, count, name):
        s = self.session()
        s.query(Products). \
            filter(Products.name == f'{name}'). \
            update({'count': count})
        session_end(s)

    async def update_price_in_stock(self, price, name):
        s = self.session()
        s.query(Products). \
            filter(Products.name == f'{name}'). \
            update({'price': price})
        session_end(s)

    """Таблица PromoCodes"""
    async def check_exists_promocode(self, code):
        s = self.session()
        check = row_exists(s, PromoCodes, PromoCodes.code, code)
        if check:
            data = s.query(PromoCodes).filter(PromoCodes.code == f'{code}').one()
            use = data.use
            service = data.service
            session_end(s)
            if use == 0:
                if service > 0:
                    return 'service'
                else:
                    return 'ok'
        session_end(s)
        return 'not'

    async def get_discount(self, code):
        s = self.session()
        data = row_one(s, PromoCodes, PromoCodes.code, code)
        output = data.discount
        session_end(s)
        return output

    async def get_service_count(self, code):
        s = self.session()
        data = row_one(s, PromoCodes, PromoCodes.code, code)
        output = data.service
        session_end(s)
        return output

    async def use_promocode(self, code):
        s = self.session()
        s.query(PromoCodes). \
            filter(PromoCodes.code == f'{code}'). \
            update({'use': 1})
        session_end(s)

    async def generate_promocodes(self, price, count):
        s = self.session()
        for i in range(count):
            while True:
                label = create_label_promocode()
                check = await self.check_exists_promocode(label)
                if check == 'not':
                    if price == 0:
                        service = 1
                    else:
                        service = 0
                    add_promocodes = PromoCodes(code=label, issued=0, use=0, service=service, discount=price)
                    s.add(add_promocodes)
                    break
        session_end(s)

