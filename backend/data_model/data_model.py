from typing import Optional, List, Any
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists


PRODUCTION_NAME = "volunteer"


class Database:

    Engine = None
    Base = declarative_base()
    Session = None

    @staticmethod
    def create_database(name: Optional[str]=None) -> None:
        db_name = None
        db_exists = False

        if name is None:
            db_name = 'sqlite:///' + PRODUCTION_NAME + '.db'
        else:
            db_name = 'sqlite:///' + name + '.db'

        if database_exists(db_name):
            db_exists = True

        Database.Engine = create_engine(db_name)
        Database.Base.metadata.create_all(Database.Engine)
        Database.Session = sessionmaker(bind=Database.Engine)

        if not db_exists:
            Database._initialize_org_types()

    @staticmethod
    def _initialize_types() -> None:
        Database._initialize_org_types()
        Database._initialize_visibility_types()

    @staticmethod
    def _initialize_org_types() -> None:
        org_types = []
        org_types.append(OrganizationType(Id=1, Name="Contributing"))
        org_types.append(OrganizationType(Id=2, Name="Consuming"))
        org_types.append(OrganizationType(Id=3, Name="Hybrid"))
        Database._add_all_types(org_types)

    @staticmethod
    def _initialize_visibility_types() -> None:
        visibility_types = []
        visibility_types.append(Visibility(Id=1, Name="Public"))
        visibility_types.append(Visibility(Id=2, Name="Private"))
        Database._add_all_types(visibility_types)

    @staticmethod
    def _add_all_types(types: List[Any]) -> None:
        try:
            session = Database.Session()
            session.add_all(types)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def drop_all_test_database(name: Optional[str]=None) -> None:
        if name == PRODUCTION_NAME:
            raise ValueError("Can't drop production database.")
        User.__table__.drop(Database.Engine)
        Organization.__table__.drop(Database.Engine)
        OrganizationType.__table__.drop(Database.Engine)
        RewardTransaction.__table__.drop(Database.Engine)
        ActivityTransaction.__table__.drop(Database.Engine)
        RefreshEvent.__table__.drop(Database.Engine)
        Activity.__table__.drop(Database.Engine)
        Reward.__table__.drop(Database.Engine)
        OrganizationRegistrationRequest.__table__.drop(Database.Engine)
        Visibility.__table__.drop(Database.Engine)

    @staticmethod
    def _get_orm_classes() -> List[type]:
        raise NotImplementedError()

class User(Database.Base):
    __tablename__ = "User"

    Id = Column(Integer, primary_key=True)
    Email = Column(String, nullable=False, index=True)
    PasswordHash = Column(String, nullable=False)
    FirstName = Column(String, nullable=True)
    LastName = Column(String, nullable=False)
    PhoneNumber = Column(String, nullable=False)


class Organization(Database.Base):
    __tablename__ = "Organization"

    Id = Column(Integer, primary_key=True)
    OwnerId = Column(Integer, ForeignKey('User.Id'), nullable=False)
    Type = Column(Integer, ForeignKey('OrganizationType.Id'), nullable=False)
    PointsToDistribute = Column(Integer, nullable=False)
    PointsToConsume = Column(Integer, nullable=False)
    LastRefreshInstant = Column(DateTime, nullable=False)
    RefreshIntervalInDays = Column(Integer, nullable=False)
    RefreshAmount = Column(Integer, nullable=False)


class OrganizationType(Database.Base):
    __tablename__ = "OrganizationType"

    Id = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)


class RewardTransaction(Database.Base):
    __tablename__ = "RewardTransaction"

    Id = Column(Integer, primary_key=True)
    UserId = Column(Integer, ForeignKey('User.Id'), nullable=False, index=True)
    Points = Column(Integer, nullable=False)
    OrganizationId = Column(Integer, ForeignKey('Organization.Id'), nullable=False, index=True)
    Instant = Column(DateTime, nullable=False)
    Reward = Column(Integer, ForeignKey('Reward.Id'), nullable=False)


class ActivityTransaction(Database.Base):
    __tablename__ = "ActivityTransaction"

    Id = Column(Integer, primary_key=True)
    UserId = Column(Integer, ForeignKey('User.Id'), nullable=False, index=True)
    Points = Column(Integer, nullable=False)
    OrganizationId = Column(Integer, ForeignKey('Organization.Id'), nullable=False, index=True)
    Instant = Column(DateTime, nullable=False)
    Activity = Column(Integer, ForeignKey('Activity.Id'), nullable=True)


class RefreshEvent(Database.Base):
    __tablename__ = "RefreshEvent"

    Id = Column(Integer, primary_key=True)
    Points = Column(Integer, nullable=False)
    Type = Column(Integer, nullable=False)
    OrganizationId = Column(Integer, ForeignKey('Organization.Id'), nullable=False)
    Instant = Column(DateTime, nullable=False)


class Activity(Database.Base):
    __tablename__ = "Activity"

    Id = Column(Integer, primary_key=True)
    PointsPerHour = Column(Integer, nullable=False)
    PointsPerCompletion = Column(Integer, nullable=False)
    OneTime = Column(Boolean, nullable=False)
    Visibility = Column(Integer, ForeignKey('Visibility.Id'), nullable=False)
    AssociatedOrganization = Column(Integer, ForeignKey('Organization.Id'), nullable=True)
    Description = Column(String, nullable=False)


class Reward(Database.Base):
    __tablename__ = "Reward"

    Id = Column(Integer, primary_key=True)
    OneTime = Column(Boolean, nullable=False)
    PointsPerReward = Column(Integer, nullable=False)
    Visibility = Column(Integer, ForeignKey('Visibility.Id'), nullable=False)
    AssociatedOrganization = Column(Integer, ForeignKey('Organization.Id'), nullable=True)
    Description = Column(String, nullable=False)


class OrganizationRegistrationRequest(Database.Base):
    __tablename__ = "OrganizationRegistrationRequest"

    Id = Column(Integer, primary_key=True)
    SubmittingUserId = Column(Integer, ForeignKey('User.Id'), nullable=False, index=True)
    OrganizationName = Column(String, nullable=False, index=True)
    Message = Column(String, nullable=False)
    ContactPhoneNumber = Column(String, nullable=False)
    ContactEmail = Column(String, nullable=False)
    OrganizationURL = Column(String, nullable=False)


class Visibility(Database.Base):
    __tablename__ = "Visibility"

    Id = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)

Database.create_database()
