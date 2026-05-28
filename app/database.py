from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./biashara.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Business(Base):
    __tablename__ = "businesses"
    id         = Column(Integer, primary_key=True)
    phone      = Column(String, unique=True, index=True)
    name       = Column(String, default="My Business")
    created_at = Column(DateTime, default=datetime.utcnow)
    sales      = relationship("Sale", back_populates="business")
    expenses   = relationship("Expense", back_populates="business")
    customers  = relationship("Customer", back_populates="business")
    inventory = relationship("Inventory", back_populates="business")

class Sale(Base):
    __tablename__ = "sales"
    id          = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    item        = Column(String)
    amount      = Column(Float)
    customer    = Column(String, nullable=True)
    is_credit   = Column(Integer, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow)
    business    = relationship("Business", back_populates="sales")

class Expense(Base):
    __tablename__ = "expenses"
    id          = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    description = Column(String)
    amount      = Column(Float)
    created_at  = Column(DateTime, default=datetime.utcnow)
    business    = relationship("Business", back_populates="expenses")

class Customer(Base):
    __tablename__ = "customers"
    id          = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    name        = Column(String)
    phone       = Column(String, nullable=True)
    balance     = Column(Float, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow)
    business    = relationship("Business", back_populates="customers")
    

class Inventory(Base):
    __tablename__ = "inventory"
    id          = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    item        = Column(String, index=True)
    quantity    = Column(Float, default=0)
    unit        = Column(String, default="units")
    min_level   = Column(Float, default=5)
    updated_at  = Column(DateTime, default=datetime.utcnow)
    business    = relationship("Business", back_populates="inventory")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

def get_or_create_business(db, phone: str):
    business = db.query(Business).filter(Business.phone == phone).first()
    if not business:
        business = Business(phone=phone)
        db.add(business)
        db.commit()
        db.refresh(business)
    return business