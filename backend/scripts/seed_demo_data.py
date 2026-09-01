"""
MATS Deterministic Demo Dataset Seeder
Seeds companies, OHLCV historical prices, balance sheet fundamentals,
chunked regulatory filings, demo user portfolio, and watchlist.
"""
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add backend directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.investor_profile import InvestorProfile
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.watchlist import Watchlist
from app.models.market import Company, Security, PriceHistory, MarketSnapshot, FundamentalData
from app.models.document import Document, DocumentChunk
from app.models.monitoring import Alert, MarketEvent
from app.services.embeddings.embedding_service import embedding_service


def seed_demo_dataset():
    db = SessionLocal()
    print("==================================================")
    print("SEEDING DETERMINISTIC HACKATHON DEMO DATASET")
    print("==================================================")

    try:
        # 1. Demo User Account
        demo_email = "demo@mats.ai"
        user = db.query(User).filter(User.email == demo_email).first()
        if not user:
            print(f"[*] Creating demo user: {demo_email}")
            user = User(
                email=demo_email,
                hashed_password=get_password_hash("DemoUser123!"),
                full_name="Hackathon Demo Investor",
                is_active=True,
                is_superuser=False,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print(f"[*] Found existing demo user: {demo_email}")

        # 2. Investor Profile
        profile = db.query(InvestorProfile).filter(InvestorProfile.user_id == user.id).first()
        if not profile:
            profile = InvestorProfile(
                user_id=user.id,
                risk_tolerance="moderate",
                investment_horizon="medium",
                preferred_sectors="Technology,Healthcare,Consumer Cyclical",
                target_return=14.5,
                experience_level="intermediate",
            )
            db.add(profile)
            db.commit()
            print("[*] Created demo investor profile (Moderate / Intermediate).")

        # 3. Demo Portfolio
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
        if not portfolio:
            portfolio = Portfolio(
                user_id=user.id,
                name="Core Alpha Growth Portfolio",
                description="Diversified institutional tech and healthcare demonstration portfolio.",
                cash_balance=18500.0,
            )
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)
            print("[*] Created demo portfolio with $18,500 cash balance.")

        # Clean existing demo holdings to ensure known baseline
        db.query(Holding).filter(Holding.portfolio_id == portfolio.id).delete()
        db.commit()

        demo_holdings = [
            {"symbol": "NVDA", "quantity": 30.0, "buy_price": 118.50, "current_price": 128.40},
            {"symbol": "AAPL", "quantity": 40.0, "buy_price": 195.00, "current_price": 224.20},
            {"symbol": "MSFT", "quantity": 25.0, "buy_price": 412.00, "current_price": 448.50},
            {"symbol": "JNJ", "quantity": 35.0, "buy_price": 156.00, "current_price": 162.80},
        ]
        for h in demo_holdings:
            db.add(Holding(
                portfolio_id=portfolio.id,
                symbol=h["symbol"],
                quantity=h["quantity"],
                buy_price=h["buy_price"],
                current_value=h["quantity"] * h["current_price"],
            ))
        db.commit()
        print(f"[*] Seeded {len(demo_holdings)} demo holdings (NVDA, AAPL, MSFT, JNJ).")

        # 4. Demo Watchlist
        watchlist = db.query(Watchlist).filter(Watchlist.user_id == user.id).first()
        if not watchlist:
            watchlist = Watchlist(
                user_id=user.id,
                name="Priority Tech & AI Targets",
                symbols="NVDA,AAPL,MSFT,TSLA,JNJ",
            )
            db.add(watchlist)
            db.commit()
            print("[*] Created demo watchlist with priority target symbols.")

        # 5. Companies & Securities
        demo_companies = [
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors", "price": 128.40, "pe": 68.4, "beta": 1.65},
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics", "price": 224.20, "pe": 32.1, "beta": 1.05},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software - Infrastructure", "price": 448.50, "pe": 35.8, "beta": 1.12},
            {"symbol": "TSLA", "name": "Tesla, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers", "price": 218.80, "pe": 72.3, "beta": 2.15},
            {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Drug Manufacturers", "price": 162.80, "pe": 18.2, "beta": 0.55},
        ]

        for c in demo_companies:
            comp = db.query(Company).filter(Company.symbol == c["symbol"]).first()
            if not comp:
                comp = Company(
                    symbol=c["symbol"],
                    name=c["name"],
                    sector=c["sector"],
                    industry=c["industry"],
                    description=f"{c['name']} operates within {c['sector']} specializing in {c['industry']}.",
                )
                db.add(comp)
                db.commit()
                db.refresh(comp)

            # Security
            sec = db.query(Security).filter(Security.symbol == c["symbol"]).first()
            if not sec:
                sec = Security(
                    symbol=c["symbol"],
                    company_id=comp.id,
                    name=c["name"],
                    security_type="Common Stock",
                    currency="USD",
                    is_active=True,
                )
                db.add(sec)
                db.commit()
                db.refresh(sec)

            # Snapshot
            snap = db.query(MarketSnapshot).filter(MarketSnapshot.symbol == c["symbol"]).first()
            now = datetime.now(timezone.utc)
            if not snap:
                snap = MarketSnapshot(
                    security_id=sec.id,
                    symbol=c["symbol"],
                    price=c["price"],
                    change=2.40,
                    change_percent=1.90,
                    high_52w=c["price"] * 1.25,
                    low_52w=c["price"] * 0.70,
                    pe_ratio=c["pe"],
                    market_cap=3100000000000.0,
                    volume=38500000.0,
                    source="DEMO_CACHE",
                    is_fresh=True,
                    timestamp=now,
                )
                db.add(snap)
            else:
                snap.price = c["price"]
                snap.timestamp = now

            # Fundamentals
            fund = db.query(FundamentalData).filter(FundamentalData.company_id == comp.id).first()
            if not fund:
                fund = FundamentalData(
                    company_id=comp.id,
                    symbol=c["symbol"],
                    period_type="annual",
                    fiscal_year=2025,
                    revenue=120000000000.0,
                    net_income=45000000000.0,
                    eps=4.85,
                    free_cash_flow=35000000000.0,
                    pe_ratio=c["pe"],
                    pb_ratio=12.4,
                    debt_to_equity=0.42,
                    source="DEMO_FUNDAMENTALS",
                    retrieved_at=now,
                )
                db.add(fund)
            db.commit()

            # Seed 30-day Price History if absent
            existing_hist = db.query(PriceHistory).filter(PriceHistory.security_id == sec.id).count()
            if existing_hist < 10:
                base_p = c["price"]
                for d in range(30, 0, -1):
                    hist_time = now - timedelta(days=d)
                    delta = (d % 5 - 2) * 0.008
                    day_price = base_p * (1.0 - (d * 0.003) + delta)
                    db.add(PriceHistory(
                        security_id=sec.id,
                        symbol=c["symbol"],
                        timestamp=hist_time,
                        open=day_price * 0.99,
                        high=day_price * 1.015,
                        low=day_price * 0.985,
                        close=day_price,
                        adjusted_close=day_price,
                        volume=25000000.0 + (d * 500000),
                    ))
                db.commit()

        print(f"[*] Verified companies, snapshots, fundamentals and 30-day OHLCV history for all demo symbols.")

        # 6. Seed Regulatory SEC 10-K Filings for RAG
        rag_filings = [
            {
                "symbol": "NVDA",
                "title": "NVIDIA Corporation Form 10-K Annual Report",
                "source": "SEC EDGAR Form 10-K",
                "text": "NVIDIA Corporation is the pioneer of accelerated computing. Our platform strategy combines hardware, systems, software, algorithms, and libraries. In the compute segment, Datacenter revenue rose 217% driven by the NVIDIA Hopper architecture. Enterprise demand for generative AI training and accelerated inference has created strong order visibility through next fiscal year. Operating margins expanded to 65% with significant free cash flow expansion.",
            },
            {
                "symbol": "AAPL",
                "title": "Apple Inc. Form 10-K Annual Report",
                "source": "SEC EDGAR Form 10-K",
                "text": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories. Services segment revenue reached record highs, fueled by over 1 billion paid subscriptions across advertising, cloud services, and digital media. Gross margins remained resilient at 45.9%. The Company continued its capital return program, returning over $90 billion through dividends and share repurchases.",
            }
        ]

        for filing in rag_filings:
            existing_doc = db.query(Document).filter(Document.company_symbol == filing["symbol"]).first()
            if not existing_doc:
                doc = Document(
                    company_symbol=filing["symbol"],
                    title=filing["title"],
                    document_type="10-K",
                    source_url=f"https://www.sec.gov/edgar/{filing['symbol'].lower()}",
                    trust_level="OFFICIAL",
                    raw_content=filing["text"],
                    chunk_count=1,
                    status="processed",
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)

                # Generate dense semantic embedding
                vec = embedding_service.embed_text(filing["text"])
                import json
                chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=0,
                    text=filing["text"],
                    section="Item 7. Management Discussion and Analysis",
                    embedding=json.dumps(vec),
                )
                db.add(chunk)
                db.commit()
                print(f"[*] Ingested official 10-K document & semantic embedding for {filing['symbol']}.")

        print("==================================================")
        print("DEMO DATASET SEEDING COMPLETE: 100% SUCCESSFUL")
        print("Demo User: demo@mats.ai / DemoUser123!")
        print("==================================================")

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_dataset()
