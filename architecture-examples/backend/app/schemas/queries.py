import strawberry
from typing import List, Optional
from datetime import datetime
from fastapi import Request
from app.schemas.types import CryptoCurrency, Portfolio, PortfolioAsset, AssetTransaction, PriceData
from app.services.crypto_cache import CryptoCacheService
from app.services.database_service import DatabaseService
from app.utils.auth import get_current_user_from_token
from app.database.connection import get_db
from app.core.config import settings

# Initialize cached crypto service
crypto_cache_service = CryptoCacheService(settings.redis_url)

@strawberry.type
class Query:
    @strawberry.field
    async def cryptocurrencies(self, limit: int = 100) -> List[CryptoCurrency]:
        """Get list of cryptocurrencies with market data"""
        try:
            data = await crypto_cache_service.get_cryptocurrencies()

            # Apply limit if provided
            if limit and limit > 0:
                data = data[:limit]

            cryptocurrencies = []
            for item in data:
                crypto = CryptoCurrency(
                    id=item["id"],
                    symbol=item["symbol"],
                    name=item["name"],
                    current_price=float(item.get("current_price", 0)),
                    market_cap=float(item.get("market_cap", 0)),
                    market_cap_rank=int(item.get("market_cap_rank", 0)),
                    fully_diluted_valuation=float(item.get("fully_diluted_valuation", 0)) if item.get("fully_diluted_valuation") else None,
                    total_volume=float(item.get("total_volume", 0)),
                    high_24h=float(item.get("high_24h", 0)),
                    low_24h=float(item.get("low_24h", 0)),
                    price_change_24h=float(item.get("price_change_24h", 0)),
                    price_change_percentage_24h=float(item.get("price_change_percentage_24h", 0)),
                    market_cap_change_24h=float(item.get("market_cap_change_24h", 0)),
                    market_cap_change_percentage_24h=float(item.get("market_cap_change_percentage_24h", 0)),
                    circulating_supply=float(item.get("circulating_supply", 0)),
                    total_supply=float(item.get("total_supply", 0)) if item.get("total_supply") else None,
                    max_supply=float(item.get("max_supply", 0)) if item.get("max_supply") else None,
                    ath=float(item.get("ath", 0)),
                    ath_change_percentage=float(item.get("ath_change_percentage", 0)),
                    ath_date=datetime.fromisoformat(item.get("ath_date", "2021-01-01T00:00:00.000Z").replace("Z", "+00:00")),
                    atl=float(item.get("atl", 0)),
                    atl_change_percentage=float(item.get("atl_change_percentage", 0)),
                    atl_date=datetime.fromisoformat(item.get("atl_date", "2021-01-01T00:00:00.000Z").replace("Z", "+00:00")),
                    last_updated=datetime.fromisoformat(item.get("last_updated", "2021-01-01T00:00:00.000Z").replace("Z", "+00:00"))
                )
                cryptocurrencies.append(crypto)
            
            return cryptocurrencies
        except Exception as e:
            print(f"Error fetching cryptocurrencies: {e}")
            return []
    
    @strawberry.field
    async def cryptocurrency(self, id: str) -> Optional[CryptoCurrency]:
        """Get specific cryptocurrency by ID"""
        try:
            data = await crypto_cache_service.get_cryptocurrency_by_id(id)
            if not data:
                return None
                
            market_data = data.get("market_data", {})
            
            return CryptoCurrency(
                id=data["id"],
                symbol=data["symbol"],
                name=data["name"],
                current_price=float(market_data.get("current_price", {}).get("usd", 0)),
                market_cap=float(market_data.get("market_cap", {}).get("usd", 0)),
                market_cap_rank=int(market_data.get("market_cap_rank", 0)),
                fully_diluted_valuation=float(market_data.get("fully_diluted_valuation", {}).get("usd", 0)) if market_data.get("fully_diluted_valuation", {}).get("usd") else None,
                total_volume=float(market_data.get("total_volume", {}).get("usd", 0)),
                high_24h=float(market_data.get("high_24h", {}).get("usd", 0)),
                low_24h=float(market_data.get("low_24h", {}).get("usd", 0)),
                price_change_24h=float(market_data.get("price_change_24h", 0)),
                price_change_percentage_24h=float(market_data.get("price_change_percentage_24h", 0)),
                market_cap_change_24h=float(market_data.get("market_cap_change_24h", 0)),
                market_cap_change_percentage_24h=float(market_data.get("market_cap_change_percentage_24h", 0)),
                circulating_supply=float(market_data.get("circulating_supply", 0)),
                total_supply=float(market_data.get("total_supply", 0)) if market_data.get("total_supply") else None,
                max_supply=float(market_data.get("max_supply", 0)) if market_data.get("max_supply") else None,
                ath=float(market_data.get("ath", {}).get("usd", 0)),
                ath_change_percentage=float(market_data.get("ath_change_percentage", {}).get("usd", 0)),
                ath_date=datetime.fromisoformat(market_data.get("ath_date", {}).get("usd", "2021-01-01T00:00:00.000Z").replace("Z", "+00:00")),
                atl=float(market_data.get("atl", {}).get("usd", 0)),
                atl_change_percentage=float(market_data.get("atl_change_percentage", {}).get("usd", 0)),
                atl_date=datetime.fromisoformat(market_data.get("atl_date", {}).get("usd", "2021-01-01T00:00:00.000Z").replace("Z", "+00:00")),
                last_updated=datetime.fromisoformat(data.get("last_updated", "2021-01-01T00:00:00.000Z").replace("Z", "+00:00"))
            )
        except Exception as e:
            print(f"Error fetching cryptocurrency {id}: {e}")
            return None
    
    @strawberry.field
    async def portfolios(self, info) -> List[Portfolio]:
        """Get user portfolios (requires authentication)"""
        # Extract JWT token from request headers
        request = info.context["request"]
        authorization = request.headers.get("authorization", "")
        
        if not authorization.startswith("Bearer "):
            # Return empty list for unauthenticated users
            return []
        
        token = authorization.split(" ")[1]
        
        # Get current user from token
        db = next(get_db())
        try:
            current_user = get_current_user_from_token(token, db)
            if not current_user:
                return []
            
            # Get portfolios for this user
            with DatabaseService() as db_service:
                portfolio_models = db_service.get_portfolios_by_user(current_user.id)
                portfolios = []
                
                for portfolio_model in portfolio_models:
                    # Convert only active assets (amount > 0) to GraphQL types for main display
                    active_assets = db_service.get_active_portfolio_assets(portfolio_model.id)
                    assets = []
                    for asset_model in active_assets:
                        # Get transactions for this asset
                        transaction_models = db_service.get_asset_transactions(asset_model.id)
                        transactions = [
                            AssetTransaction(
                                id=t.id,
                                transaction_type=t.transaction_type,
                                amount=t.amount,
                                price_per_unit=t.price_per_unit,
                                total_value=t.total_value,
                                realized_profit_loss=t.realized_profit_loss,
                                timestamp=t.timestamp,
                                notes=t.notes
                            ) for t in transaction_models
                        ]
                        
                        asset = PortfolioAsset(
                            id=asset_model.id,
                            crypto_id=asset_model.crypto_id,
                            symbol=asset_model.symbol,
                            name=asset_model.name,
                            amount=asset_model.amount,
                            average_buy_price=asset_model.average_buy_price,
                            current_price=asset_model.current_price,
                            total_value=asset_model.total_value,
                            profit_loss=asset_model.profit_loss,
                            profit_loss_percentage=asset_model.profit_loss_percentage,
                            transactions=transactions
                        )
                        assets.append(asset)
                    
                    portfolio = Portfolio(
                        id=portfolio_model.id,
                        name=portfolio_model.name,
                        description=portfolio_model.description,
                        total_value=portfolio_model.total_value,
                        total_profit_loss=portfolio_model.total_profit_loss,
                        total_profit_loss_percentage=portfolio_model.total_profit_loss_percentage,
                        total_realized_profit_loss=portfolio_model.total_realized_profit_loss,
                        total_cost_basis=portfolio_model.total_cost_basis,
                        assets=assets,
                        created_at=portfolio_model.created_at,
                        updated_at=portfolio_model.updated_at
                    )
                    portfolios.append(portfolio)
                
                return portfolios
        finally:
            db.close()
    
    @strawberry.field
    async def portfolio(self, id: str) -> Optional[Portfolio]:
        """Get specific portfolio by ID"""
        with DatabaseService() as db_service:
            portfolio_model = db_service.get_portfolio(id)
            if not portfolio_model:
                return None
            
            # Convert only active assets (amount > 0) to GraphQL types for main display
            active_assets = db_service.get_active_portfolio_assets(portfolio_model.id)
            assets = []
            for asset_model in active_assets:
                # Get transactions for this asset
                transaction_models = db_service.get_asset_transactions(asset_model.id)
                transactions = [
                    AssetTransaction(
                        id=t.id,
                        transaction_type=t.transaction_type,
                        amount=t.amount,
                        price_per_unit=t.price_per_unit,
                        total_value=t.total_value,
                        realized_profit_loss=t.realized_profit_loss,
                        timestamp=t.timestamp,
                        notes=t.notes
                    ) for t in transaction_models
                ]
                
                asset = PortfolioAsset(
                    id=asset_model.id,
                    crypto_id=asset_model.crypto_id,
                    symbol=asset_model.symbol,
                    name=asset_model.name,
                    amount=asset_model.amount,
                    average_buy_price=asset_model.average_buy_price,
                    current_price=asset_model.current_price,
                    total_value=asset_model.total_value,
                    profit_loss=asset_model.profit_loss,
                    profit_loss_percentage=asset_model.profit_loss_percentage,
                    transactions=transactions
                )
                assets.append(asset)
            
            return Portfolio(
                id=portfolio_model.id,
                name=portfolio_model.name,
                description=portfolio_model.description,
                total_value=portfolio_model.total_value,
                total_profit_loss=portfolio_model.total_profit_loss,
                total_profit_loss_percentage=portfolio_model.total_profit_loss_percentage,
                total_realized_profit_loss=portfolio_model.total_realized_profit_loss,
                assets=assets,
                created_at=portfolio_model.created_at,
                updated_at=portfolio_model.updated_at
            )
    
    @strawberry.field
    async def priceHistory(
        self, 
        crypto_id: str = strawberry.argument(name="cryptoId"), 
        days: int = 30
    ) -> List[PriceData]:
        """Get price history for a cryptocurrency"""
        try:
            data = await crypto_api_service.get_price_history(crypto_id, days)
            return [
                PriceData(timestamp=str(item["timestamp"]), price=item["price"])
                for item in data
            ]
        except Exception as e:
            print(f"Error fetching price history for {crypto_id}: {e}")
            return []
    
    @strawberry.field
    async def portfolio_transactions(
        self, 
        portfolio_id: str = strawberry.argument(name="portfolioId")
    ) -> List[AssetTransaction]:
        """Get all transactions for a portfolio (including historical transactions)"""
        with DatabaseService() as db_service:
            transaction_models = db_service.get_portfolio_transactions(portfolio_id)
            
            transactions = []
            for t in transaction_models:
                transaction = AssetTransaction(
                    id=t.id,
                    transaction_type=t.transaction_type,
                    amount=t.amount,
                    price_per_unit=t.price_per_unit,
                    total_value=t.total_value,
                    realized_profit_loss=t.realized_profit_loss,
                    timestamp=t.timestamp,
                    notes=t.notes,
                    crypto_id=t.crypto_id,
                    symbol=t.symbol,
                    name=t.name
                )
                transactions.append(transaction)
            
            return transactions