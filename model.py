from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(String)
    item_url = Column(String)
    datetime = Column(String)


if __name__ == "__main__":
    engine = create_engine('sqlite:///products.db')
    Base.metadata.drop_all(engine) # очистка база данных
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
