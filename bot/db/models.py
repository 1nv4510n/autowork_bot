from enum import unique
from sqlalchemy import BigInteger, Column, String, Boolean, Integer

from bot.db.base import Base

class UsersEntry(Base):
    __tablename__ = "users"
    
    telegram_id = Column(BigInteger, nullable=False, unique=True, primary_key=True)
    full_name = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False)
    spreadsheet_url = Column(String, nullable=True)
    sheet_name = Column(String, nullable=True)
    total_lines = Column(Integer, nullable=False)
    
class ApplicationsEntry(Base):
    __tablename__ = "applications"
    
    telegram_id = Column(BigInteger, nullable=False, unique=True, primary_key=True)
    full_name = Column(String, nullable=False)
    
class OgrnListEntry(Base):
    __tablename__ = "ogrnlist"
    
    website = Column(String, nullable=False, unique=True, primary_key=True)
    ogrn = Column(String, nullable=True, unique=True)