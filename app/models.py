from sqlalchemy import Column, Integer, String, Boolean, Date
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    unsuccessful_attempts = Column(Integer, default=0)
    verification_code = Column(String, nullable=True)
    created_date = Column(Date)
