from typing import Any, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioUpdate,
    HoldingCreate,
    HoldingResponse,
    HoldingUpdate,
)
from app.services.audit.audit_service import audit_service

router = APIRouter()


@router.get("/", response_model=List[PortfolioResponse])
def get_user_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """List all portfolios belonging to current user."""
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).all()
    # Recalculate total value dynamically
    for p in portfolios:
        holdings_value = sum(h.current_value or (h.quantity * h.buy_price) for h in p.holdings)
        p.total_value = round(p.cash_balance + holdings_value, 2)
    return portfolios


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio_in: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a new portfolio."""
    portfolio = Portfolio(
        user_id=current_user.id,
        name=portfolio_in.name,
        description=portfolio_in.description,
        cash_balance=portfolio_in.cash_balance if portfolio_in.cash_balance is not None else 10000.0,
        currency=portfolio_in.currency or "USD",
        total_value=portfolio_in.cash_balance if portfolio_in.cash_balance is not None else 10000.0,
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)

    audit_service.log_event(
        db=db,
        action="PORTFOLIO_CHANGE",
        user_id=current_user.id,
        resource_type="Portfolio",
        resource_id=str(portfolio.id),
        details={"event": "create", "name": portfolio.name, "currency": portfolio.currency},
        status="SUCCESS",
    )
    return portfolio


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio_by_id(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get single portfolio with holdings."""
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
        .first()
    )
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    holdings_value = sum(h.current_value or (h.quantity * h.buy_price) for h in portfolio.holdings)
    portfolio.total_value = round(portfolio.cash_balance + holdings_value, 2)
    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: int,
    portfolio_in: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update a portfolio."""
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
        .first()
    )
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    update_data = portfolio_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(portfolio, field, value)

    db.commit()
    db.refresh(portfolio)
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete a portfolio."""
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
        .first()
    )
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    db.delete(portfolio)
    db.commit()

    audit_service.log_event(
        db=db,
        action="PORTFOLIO_CHANGE",
        user_id=current_user.id,
        resource_type="Portfolio",
        resource_id=str(portfolio_id),
        details={"event": "delete"},
        status="SUCCESS",
    )


# Holdings endpoints
@router.post("/{portfolio_id}/holdings", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
def add_holding(
    portfolio_id: int,
    holding_in: HoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Add a new holding position into a portfolio."""
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
        .first()
    )
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    current_val = holding_in.current_value or (holding_in.quantity * holding_in.buy_price)
    holding = Holding(
        portfolio_id=portfolio.id,
        symbol=holding_in.symbol.upper(),
        asset_type=holding_in.asset_type or "Stock",
        quantity=holding_in.quantity,
        buy_price=holding_in.buy_price,
        current_value=current_val,
        notes=holding_in.notes,
    )
    db.add(holding)
    db.commit()
    db.refresh(holding)

    audit_service.log_event(
        db=db,
        action="PORTFOLIO_CHANGE",
        user_id=current_user.id,
        resource_type="Holding",
        resource_id=str(holding.id),
        details={"event": "add_holding", "symbol": holding.symbol, "portfolio_id": portfolio_id},
        status="SUCCESS",
    )
    return holding


@router.put("/{portfolio_id}/holdings/{holding_id}", response_model=HoldingResponse)
def update_holding(
    portfolio_id: int,
    holding_id: int,
    holding_in: HoldingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update a holding inside a portfolio."""
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
        .first()
    )
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    holding = (
        db.query(Holding)
        .filter(Holding.id == holding_id, Holding.portfolio_id == portfolio.id)
        .first()
    )
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    update_data = holding_in.model_dump(exclude_unset=True)
    if "symbol" in update_data and update_data["symbol"]:
        update_data["symbol"] = update_data["symbol"].upper()

    for field, value in update_data.items():
        setattr(holding, field, value)

    if not holding.current_value:
        holding.current_value = holding.quantity * holding.buy_price

    db.commit()
    db.refresh(holding)
    return holding


@router.delete("/{portfolio_id}/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(
    portfolio_id: int,
    holding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Remove a holding from a portfolio."""
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
        .first()
    )
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    holding = (
        db.query(Holding)
        .filter(Holding.id == holding_id, Holding.portfolio_id == portfolio.id)
        .first()
    )
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    db.delete(holding)
    db.commit()


class CsvImportRequest(BaseModel):
    csv_content: str = Field(..., description="CSV content string with headers: symbol,quantity,average_price")


@router.post("/{portfolio_id}/import-csv")
def import_portfolio_csv(
    portfolio_id: int,
    payload: CsvImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Import portfolio holdings from a structured CSV.
    Validates each row individually: does not silently import malformed rows.
    """
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
        .first()
    )
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    lines = [line.strip() for line in payload.csv_content.strip().splitlines() if line.strip()]
    if not lines:
        raise HTTPException(status_code=400, detail="CSV content is empty.")

    # Check header
    header = [h.strip().lower() for h in lines[0].split(",")]
    if "symbol" not in header or "quantity" not in header:
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV format. Required headers: 'symbol', 'quantity', 'average_price' (or 'buy_price').",
        )

    sym_idx = header.index("symbol")
    qty_idx = header.index("quantity")
    price_idx = header.index("average_price") if "average_price" in header else (header.index("buy_price") if "buy_price" in header else -1)

    valid_rows = []
    rejected_rows = []

    for line_num, line in enumerate(lines[1:], start=2):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < max(sym_idx, qty_idx, price_idx) + 1:
            rejected_rows.append({"line": line_num, "raw": line, "reason": "Insufficient columns."})
            continue

        raw_sym = parts[sym_idx].upper()
        raw_qty = parts[qty_idx]
        raw_price = parts[price_idx] if price_idx != -1 else "100.0"

        # Symbol validation
        if not raw_sym or len(raw_sym) > 15 or not raw_sym.isalnum():
            rejected_rows.append({"line": line_num, "symbol": raw_sym, "reason": "Invalid or missing ticker symbol."})
            continue

        # Quantity validation
        try:
            qty = float(raw_qty)
            if qty <= 0:
                rejected_rows.append({"line": line_num, "symbol": raw_sym, "reason": "Quantity must be greater than zero."})
                continue
        except ValueError:
            rejected_rows.append({"line": line_num, "symbol": raw_sym, "reason": "Malformed numerical quantity."})
            continue

        # Price validation
        try:
            price = float(raw_price)
            if price <= 0:
                rejected_rows.append({"line": line_num, "symbol": raw_sym, "reason": "Price must be greater than zero."})
                continue
        except ValueError:
            rejected_rows.append({"line": line_num, "symbol": raw_sym, "reason": "Malformed numerical price."})
            continue

        # Valid row: create holding
        holding = Holding(
            portfolio_id=portfolio.id,
            symbol=raw_sym,
            quantity=qty,
            buy_price=price,
            current_value=round(qty * price, 2),
        )
        db.add(holding)
        valid_rows.append({"symbol": raw_sym, "quantity": qty, "buy_price": price, "current_value": round(qty * price, 2)})

    db.commit()

    audit_service.log_event(
        db=db,
        action="PORTFOLIO_CSV_IMPORT",
        user_id=current_user.id,
        resource_type="portfolio",
        resource_id=str(portfolio.id),
        details={"valid_count": len(valid_rows), "rejected_count": len(rejected_rows)},
    )

    return {
        "portfolio_id": portfolio.id,
        "total_rows_evaluated": len(lines) - 1,
        "valid_count": len(valid_rows),
        "rejected_count": len(rejected_rows),
        "valid_rows": valid_rows,
        "rejected_rows": rejected_rows,
        "message": f"Successfully imported {len(valid_rows)} holdings. {len(rejected_rows)} rows rejected.",
    }
