# app/database/models.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, Numeric, Boolean, JSON, String, Index
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(Text, unique=True, nullable=False, index=True)
    email = Column(Text, unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    full_name = Column(Text, default='')
    role = Column(Text, default='user')
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')>"


class CartItem(Base):
    __tablename__ = 'cart_items'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Text, nullable=False)
    quantity = Column(Integer, default=1)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship
    user = relationship("User", back_populates="cart_items")
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, user_id={self.user_id}, product_id='{self.product_id}', quantity={self.quantity})>"


class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text)
    price = Column(Numeric(10, 2), default=0)
    category = Column(Text, index=True)
    image_url = Column(Text)
    for_conditions = Column(Text)  # comma-separated
    ingredients = Column(Text)
    usage = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', category='{self.category}')>"

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    total_price = Column(Numeric(10, 2), default=0)
    status = Column(Text, default='pending')
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, total_price={self.total_price}, status='{self.status}')>"

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    product_id = Column(Text, nullable=False)
    product_name = Column(Text)
    quantity = Column(Integer, default=1)

    # Relationship
    order = relationship("Order", back_populates="items")

    def __repr__(self):
        return (f"<OrderItem(id={self.id}, order_id={self.order_id}, "
                f"product_id='{self.product_id}', product_name='{self.product_name}', "
                f"quantity={self.quantity}, price={self.price})>")


class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), index=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="chat_session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession(id='{self.id}', user_id={self.user_id}, title='{self.title}')>"


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(String(50), primary_key=True, index=True)
    chat_id = Column(String(50), ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    is_bot = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    products = Column(JSON, nullable=True)
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages")
    user = relationship("User", back_populates="chat_messages")
    
    def __repr__(self):
        return f"<ChatMessage(id='{self.id}', chat_id='{self.chat_id}', is_bot={self.is_bot})>"
