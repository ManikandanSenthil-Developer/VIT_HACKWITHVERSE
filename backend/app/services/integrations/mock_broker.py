from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.ecosystem import BrokerConnection


class MockBrokerAdapter:
    """
    Simulated external brokerage adapter (paper trading sandbox).
    Demonstrates external portfolio synchronization without order routing capabilities.
    Strictly read-only; trade placement is prevented at the code level.
    """

    MOCK_HOLDINGS = [
        {"symbol": "NVDA", "quantity": 25.0, "buy_price": 116.50, "current_value": 3212.50},
        {"symbol": "MSFT", "quantity": 18.0, "buy_price": 408.00, "current_value": 8064.00},
        {"symbol": "AAPL", "quantity": 30.0, "buy_price": 192.00, "current_value": 6840.00},
        {"symbol": "AMZN", "quantity": 20.0, "buy_price": 178.00, "current_value": 3720.00},
    ]

    @classmethod
    def sync_broker_portfolio(
        cls,
        db: Session,
        user_id: int,
        account_id: str = "ACC-DEMO-9942",
        broker_name: str = "Demo Broker (Paper Sandbox)",
    ) -> Dict[str, Any]:
        """
        Synchronizes portfolio holdings from mock brokerage into MATS.
        All data is explicitly tagged as mock/demo data.
        """
        # 1. Update or create broker connection
        conn = (
            db.query(BrokerConnection)
            .filter(BrokerConnection.user_id == user_id, BrokerConnection.account_id == account_id)
            .first()
        )
        if not conn:
            conn = BrokerConnection(
                user_id=user_id,
                broker_name=broker_name,
                account_id=account_id,
                is_active=True,
                is_read_only=True,
                last_synced_at=datetime.now(timezone.utc),
            )
            db.add(conn)
        else:
            conn.last_synced_at = datetime.now(timezone.utc)
            conn.is_active = True

        # 2. Sync to a dedicated Broker-linked portfolio
        port = (
            db.query(Portfolio)
            .filter(Portfolio.user_id == user_id, Portfolio.name.like("%Broker%"))
            .first()
        )
        if not port:
            port = Portfolio(
                user_id=user_id,
                name="Synced Brokerage Portfolio (DEMO DATA)",
                cash_balance=24500.0,
            )
            db.add(port)
            db.commit()
            db.refresh(port)
        else:
            # Clear old synced holdings
            db.query(Holding).filter(Holding.portfolio_id == port.id).delete()
            db.commit()

        # Add simulated holdings
        for h in cls.MOCK_HOLDINGS:
            db.add(
                Holding(
                    portfolio_id=port.id,
                    symbol=h["symbol"],
                    quantity=h["quantity"],
                    buy_price=h["buy_price"],
                    current_value=h["current_value"],
                )
            )

        db.commit()
        db.refresh(conn)

        return {
            "status": "SUCCESS",
            "connection_id": conn.id,
            "broker_name": conn.broker_name,
            "account_id": conn.account_id,
            "is_read_only": True,
            "synced_holdings_count": len(cls.MOCK_HOLDINGS),
            "portfolio_id": port.id,
            "last_synced_at": conn.last_synced_at.isoformat(),
            "disclaimer": "DEMO DATA ONLY: Synced via read-only mock adapter for demonstration purposes.",
        }

    @classmethod
    def execute_order(cls, *args, **kwargs):
        """
        Firmly prohibits order execution across the system.
        """
        raise PermissionError(
            "Trade execution prohibited by MATS Decision Support Governance Policy. "
            "MATS is strictly non-custodial and never transmits broker orders."
        )


mock_broker_adapter = MockBrokerAdapter()
