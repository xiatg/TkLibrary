from sqlalchemy import Column, String, create_engine, Integer, Date
from sqlalchemy.ext.declarative import declarative_base

# Database Table Definition
Base = declarative_base()

class Book_Author(Base):
    __tablename__ = 'Book_Author'
    Accession_Number = Column(String(3), primary_key = True)
    Author = Column(String(100), primary_key = True)

class Borrow_And_Return_Record(Base):
    __tablename__ = 'Borrow_And_Return_Record'
    Accession_Number = Column(String(3), primary_key = True)
    memberid = Column(String(6), primary_key = True)
    Borrow_Date = Column(Date)
    Return_Date = Column(Date)
    Due_Date = Column(Date)

class LibBooks(Base):
    __tablename__ = 'LibBooks'
    Accession_Number = Column(String(3), primary_key = True)
    Title = Column(String(100))
    ISBN = Column(String(100))
    Publisher = Column(String(100))
    Year = Column(Integer)

class LibMember(Base):
    __tablename__ = 'LibMember'
    memberid = Column(String(6), primary_key = True)
    name = Column(String(100))
    faculty = Column(String(100))
    phone_number = Column(String(100))
    email_address = Column(String(100))
    outstanding_fee = Column(Integer)

class Reserve_Record(Base):
    __tablename__ = 'Reserve_Record'
    Accession_Number = Column(String(3), primary_key = True)
    memberid = Column(String(6), primary_key = True)
    Reserve_Date = Column(Date)