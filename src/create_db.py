from config import Config

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, BigInteger, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


connection_name = Config.db_connection
engine = create_engine(connection_name, echo=True)
Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    user_id = Column('user_id', BigInteger, primary_key=True, unique=True)
    role = Column('role', String(10))
    firstname = Column('first_name', String(64))
    surname = Column('surname', String(64))
    nickname = Column('nickname', String(64))
    buyers = relationship('Buyers', backref='user')

    lottery = Column('lottery', Boolean, default=False)


class Buyers(Base):
    __tablename__ = 'buyers'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    label = Column('label', String(64), primary_key=True, unique=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    ticket_photo_id = Column('ticket_photo_id', String(200), default=None)
    tickets = relationship("Tickets", backref='buyer')
    price = Column('price', Float)
    date_time = Column('date_time', DateTime)

    def __repr__(self):
        return self.id


class Tickets(Base):
    __tablename__ = 'tickets'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    label = Column(String(64), ForeignKey('buyers.label'))
    product_name = Column('product_name', String(32))
    product_count = Column('product_count', Integer)
    names = relationship("TicketNames", backref='ticket')
    not_distributed_tickets = Column('not_distributed_tickets', Integer)

    def __repr__(self):
        return self.id


class TicketNames(Base):
    __tablename__ = 'ticket_names'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    name = Column('name', String(64))
    check = Column('check', Boolean, default=False)

class PromoCodes(Base):
    __tablename__ = 'promocodes'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    code = Column('code', String(64))
    issued = Column('issued', Boolean, default=False)
    use = Column('use', Boolean, default=False)
    service = Column('service', Integer, default=0)
    discount = Column('discount', Integer, default=50)
# В строке service - количество для выдачи билетов

class Products(Base):
    __tablename__ = "products"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    product_id = Column('product_id', Integer, unique=True)
    name = Column('name', String(64))
    price = Column('price', Integer)
    count = Column('count', Integer)


Base.metadata.create_all(bind=engine)

