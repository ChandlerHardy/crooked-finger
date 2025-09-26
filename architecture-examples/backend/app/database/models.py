from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    portfolios = relationship("PortfolioModel", back_populates="user", cascade="all, delete-orphan")

class PortfolioModel(Base):
    __tablename__ = "portfolios"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    total_value = Column(Float, default=0.0)
    total_profit_loss = Column(Float, default=0.0)
    total_profit_loss_percentage = Column(Float, default=0.0)
    total_realized_profit_loss = Column(Float, default=0.0)  # Total realized P&L from all sales
    total_cost_basis = Column(Float, default=0.0)  # Total amount originally invested
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", back_populates="portfolios")
    assets = relationship("PortfolioAssetModel", back_populates="portfolio", cascade="all, delete-orphan")

class PortfolioAssetModel(Base):
    __tablename__ = "portfolio_assets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False)
    crypto_id = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    average_buy_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    profit_loss = Column(Float, nullable=False)
    profit_loss_percentage = Column(Float, nullable=False)
    
    # Relationships
    portfolio = relationship("PortfolioModel", back_populates="assets")
    transactions = relationship("AssetTransactionModel", back_populates="asset", cascade="all, delete-orphan")

class AssetTransactionModel(Base):
    __tablename__ = "asset_transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String, ForeignKey("portfolio_assets.id"), nullable=False)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False)  # Direct reference to portfolio
    crypto_id = Column(String, nullable=False)  # Store crypto info for historical reference
    symbol = Column(String, nullable=False)  # Store symbol for historical reference
    name = Column(String, nullable=False)  # Store name for historical reference
    transaction_type = Column(String, nullable=False)  # 'buy' or 'sell'
    amount = Column(Float, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    realized_profit_loss = Column(Float, default=0.0)  # Realized P&L for sell transactions
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    asset = relationship("PortfolioAssetModel", back_populates="transactions")
    portfolio = relationship("PortfolioModel")