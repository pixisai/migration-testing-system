from sqlalchemy import CheckConstraint, Column, Integer, MetaData, Numeric, String, Text
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = "user"

    id_ = Column("id", Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    second_name = Column(String(100), nullable=False)
    phone_id = Column("phone_id", Integer, nullable=True)


class Phone(Base):
    __tablename__ = "phone"
    id_ = Column("id", Integer, primary_key=True)
    pnone = Column(String(10), nullable=False)


class Car(Base):
    __tablename__ = "car"

    id_ = Column("id", Integer, primary_key=True)
    model = Column(String(100), nullable=False)


class Product(Base):
    __tablename__ = "products"
    product_no = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    price = Column(Numeric, CheckConstraint("price > (0)::numeric"), nullable=False)
