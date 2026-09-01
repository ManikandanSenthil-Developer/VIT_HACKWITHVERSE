# MATS Hackathon Demo Day Checklist

Use this checklist 15 minutes before presenting to hackathon judges.

---

## 1. Environment & Hardware Verification
- [ ] Laptop connected to power.
- [ ] Screen resolution set to standard 1080p (1920x1080) for presentation displays.
- [ ] Browser zoom level set to 100%.
- [ ] Dark mode enabled in OS settings.

## 2. Platform Readiness Probe
Run the automated pre-demo validation script:
```powershell
& ".\scripts\demo-check.ps1"
```
**Expected Output**:
`RESULT: READY FOR DEMO (7/7 Checks Passed)`

## 3. Browser Tabs Prepared
- [ ] **Tab 1**: `http://localhost:5173/dashboard` (Authenticated as `demo@mats.ai`)
- [ ] **Tab 2**: `http://localhost:5173/portfolio` (Viewing the Core Alpha Growth Portfolio)
- [ ] **Tab 3**: `http://127.0.0.1:8000/docs` (Interactive FastAPI Swagger Documentation)

## 4. 60-Second Presentation Narrative
1. **The Problem (10s)**: Retail investors drown in fragmented charts and sensational news, without explainable risk context or multi-perspective diligence.
2. **The Innovation (20s)**: MATS uses an autonomous cluster of specialized agents (Technical Momentum, Fundamental Valuation, Sentiment Anomaly, and SEC 10-K RAG) that cross-examine signals rather than a generic single prompt.
3. **The Live Action (20s)**:
   - Run **Scenario 2** (TSLA conflict): Show judges that MATS preserves disagreement rather than averaging it out.
   - Run **Scenario 3** (Portfolio risk alert): Show how a drop in a heavily-weighted holding automatically upgrades alert severity and triggers agent analysis.
4. **The Trust Factor (10s)**: Click **"Trust & Safety"** and **"Export Report"** to show official SEC Form 10-K citations, zero fabrication, and the decision-support boundary.
