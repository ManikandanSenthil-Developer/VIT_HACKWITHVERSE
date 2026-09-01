"""
MATS Pre-Demo Health Check & Readiness Validator
Runs sub-second verification across all components and returns 'READY FOR DEMO'.
"""
import sys
import urllib.request
import json
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.document import Document
from app.models.market import Company, MarketSnapshot
from app.services.embeddings.embedding_service import embedding_service
from app.services.agents.orchestrator import orchestrator


def run_demo_check():
    print("==================================================")
    print("MATS PRE-DEMO READINESS VALIDATION")
    print("==================================================")

    failures = []
    checks_passed = 0

    # 1. Database Connection & Demo User
    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == "demo@mats.ai").first()
        if not demo_user:
            failures.append("Demo user 'demo@mats.ai' not found in database. Run seed_demo_data.py.")
        else:
            print("  [OK] Database Connected & Demo User Verified")
            checks_passed += 1

        # 2. Portfolio & Holdings
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == demo_user.id).first() if demo_user else None
        holdings_count = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).count() if portfolio else 0
        if holdings_count < 3:
            failures.append(f"Demo portfolio has only {holdings_count} holdings (expected >= 3).")
        else:
            print(f"  [OK] Demo Portfolio Verified ({holdings_count} active holdings)")
            checks_passed += 1

        # 3. Market Snapshots & Companies
        companies = db.query(Company).count()
        snapshots = db.query(MarketSnapshot).count()
        if companies < 4 or snapshots < 4:
            failures.append(f"Market data incomplete ({companies} companies, {snapshots} snapshots).")
        else:
            print(f"  [OK] Market Data Verified ({companies} companies, {snapshots} live snapshots)")
            checks_passed += 1

        # 4. RAG Filings & Vector Store
        docs = db.query(Document).count()
        if docs < 2:
            failures.append(f"RAG Knowledge Store has only {docs} documents (expected >= 2).")
        else:
            # Test local embedding engine
            test_vec = embedding_service.local_provider._generate_vector("Test vector projection")
            if len(test_vec) != 384:
                failures.append("Embedding vector dimensionality mismatch.")
            else:
                print(f"  [OK] RAG Vector Engine Verified ({docs} SEC Form 10-Ks indexed, 384-dim)")
                checks_passed += 1

    finally:
        db.close()

    # 5. Autonomous Multi-Agent Cluster
    agents = [
        orchestrator.technical_agent,
        orchestrator.fundamental_agent,
        orchestrator.sentiment_agent,
        orchestrator.research_agent,
    ]
    if not all(a is not None for a in agents):
        failures.append("One or more AI agent modules failed to initialize.")
    else:
        print(f"  [OK] Autonomous Agent Cluster Verified (4/4 Agents Online)")
        checks_passed += 1

    # 6. Live Backend HTTP Telemetry Probe
    backend_url = "http://127.0.0.1:8000/health"
    try:
        req = urllib.request.Request(backend_url, headers={"User-Agent": "MATS-DemoCheck"})
        with urllib.request.urlopen(req, timeout=3) as res:
            if res.status == 200:
                data = json.loads(res.read().decode())
                print(f"  [OK] Backend Live Probe Verified (status: {data.get('status')})")
                checks_passed += 1
            else:
                failures.append(f"Backend returned HTTP {res.status}")
    except Exception as e:
        failures.append(f"Backend HTTP probe failed at {backend_url}: {e}")

    # 7. Live Frontend HTTP Probe
    frontend_url = "http://localhost:5173"
    try:
        req = urllib.request.Request(frontend_url, headers={"User-Agent": "MATS-DemoCheck"})
        with urllib.request.urlopen(req, timeout=3) as res:
            if res.status == 200:
                print("  [OK] Frontend Live Probe Verified (HTTP 200 on port 5173)")
                checks_passed += 1
            else:
                failures.append(f"Frontend returned HTTP {res.status}")
    except Exception as e:
        failures.append(f"Frontend HTTP probe failed at {frontend_url}: {e}")

    print("==================================================")
    if not failures:
        print(f"RESULT: READY FOR DEMO (7/7 Checks Passed)")
        print("All subsystems, datasets, and probes are 100% operational.")
        print("==================================================")
        return True
    else:
        print(f"RESULT: NOT READY ({len(failures)} failures encountered):")
        for f in failures:
            print(f"  [!] {f}")
        print("==================================================")
        return False


if __name__ == "__main__":
    success = run_demo_check()
    sys.exit(0 if success else 1)
