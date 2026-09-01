from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, verify_refresh_token
from app.models.user import User
from app.models.investor_profile import InvestorProfile
from app.models.portfolio import Portfolio
from app.models.watchlist import Watchlist
from app.schemas.user import UserCreate
from app.schemas.token import Token


class AuthService:
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @classmethod
    def register(cls, db: Session, user_in: UserCreate) -> User:
        db_user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_active=True,
            is_superuser=False,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Initialize default investor profile
        default_profile = InvestorProfile(
            user_id=db_user.id,
            risk_tolerance="moderate",
            investment_horizon="medium",
            preferred_sectors="Technology,Renewables,Biotech",
            target_return=14.5,
            experience_level="intermediate"
        )
        db.add(default_profile)

        # Initialize default primary portfolio
        default_portfolio = Portfolio(
            user_id=db_user.id,
            name="Alpha Growth Portfolio",
            description="Core multi-agent growth & hedge portfolio",
            cash_balance=25000.0,
            total_value=128450.0,
            currency="USD"
        )
        db.add(default_portfolio)

        # Initialize default watchlist
        default_watchlist = Watchlist(
            user_id=db_user.id,
            name="Tech & AI Leaders",
            description="High-growth equities tracked by MATS intelligence",
            symbols="NVDA,MSFT,AAPL,GOOGL,AMZN,TSLA,PLTR"
        )
        db.add(default_watchlist)

        db.commit()
        db.refresh(db_user)
        return db_user

    @classmethod
    def authenticate(cls, db: Session, email: str, password: str) -> Optional[User]:
        user = cls.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @classmethod
    def create_tokens_for_user(cls, user: User) -> Token:
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user
        )

    @classmethod
    def refresh_access_token(cls, db: Session, refresh_token: str) -> Optional[Token]:
        user_id_str = verify_refresh_token(refresh_token)
        if not user_id_str:
            return None
        
        user = cls.get_by_id(db, user_id=int(user_id_str))
        if not user or not user.is_active:
            return None
            
        new_access_token = create_access_token(subject=user.id)
        # Issue renewed refresh token as well for sliding expiration
        new_refresh_token = create_refresh_token(subject=user.id)
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            user=user
        )
