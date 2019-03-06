from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


PRODUCTION_NAME = "volunteer"


class Database:

    Engine = None
    Base = declarative_base()

    @staticmethod
    def create_database(name: Optional[str]=None) -> None:
        if name is None:
            Database.Engine = create_engine('sqlite:///' + PRODUCTION_NAME + '.db')
        else:
            Database.Engine = create_engine('sqlite:///' + name + '.db')

        Database.Base.metadata.create_all(Database.Engine)

    @staticmethod
    def drop_all_test_database(name: Optional[str]=None) -> None:
        if name == PRODUCTION_NAME:
            raise ValueError("Can't drop production database.")
        User.__table__.drop(Database.Engine)

    @staticmethod
    def _get_orm_classes() -> List[type]:
        raise NotImplementedError()


Database.create_database()


class User(Database.Base):
    __tablename__ = "User"

    Id = Column(Integer, primary_key=True)
    Email = Column(String)
    PasswordHash = Column(String)

