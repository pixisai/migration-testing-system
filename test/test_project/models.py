from sqlalchemy import Column, Integer, MetaData, String
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
