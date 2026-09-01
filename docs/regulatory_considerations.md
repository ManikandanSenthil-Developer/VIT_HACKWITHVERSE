# MATS — Regulatory Considerations & Compliance Architecture

## 1. Executive Summary & Regulatory Perimeter
The **Multi-Agent Autonomous Financial Intelligence System (MATS)** is strictly architected as a **Non-Custodial, Autonomous Financial Decision-Support & Research Platform** designed for retail investors. 

MATS explicitly operates outside the regulatory perimeter of discretionary portfolio management (PMS), investment advisory (RIA), and registered broker-dealer execution services under jurisdictions including the **US Securities and Exchange Commission (SEC)**, the **Financial Industry Regulatory Authority (FINRA)**, and the **Securities and Exchange Board of India (SEBI)**.

---

## 2. Core Boundary Guarantees

### A. Strict Prohibition of Direct Trade Execution
- **Zero Order Routing**: MATS contains **no capabilities** to place, transmit, route, or execute buy/sell orders with brokerages or exchanges.
- **Mock Brokerage Boundary**: Any broker connections (e.g. `MockBrokerAdapter`) operate in an isolated paper sandbox with `is_read_only = True` hard-coded. Any attempt to call trade endpoints throws an un-bypassable `PermissionError`.
- **Non-Custodial**: MATS never holds, touches, or transfers client funds or securities.

### B. Decision-Support & Research Nature
- All insights, comparative metrics, bull/bear theses, and risk attributions are provided for **educational and informational purposes only**.
- Automated agent outputs do not constitute personalized investment recommendations or solicitation of securities.
- The platform enforces an omnipresent disclaimer across all user touchpoints.

### C. Protection of Financial Figures in Multilingual Translations
- Translations into Indic languages (Tamil, Hindi) strictly preserve currency symbols (`₹`, `$`, `€`), percentages (`%`), dates, and numerical values.
- Financial terminology is presented bilingually (e.g. `அபாய நிலை (Risk Level)`, `அதிர்வுத்தன்மை (Volatility)`) to prevent misleading or ambiguous retail translations.

---

## 3. Data Lineage & Provenance Governance
Under institutional audit standards, retail investors must know the exact origin of financial data:
1. **Source Hierarchy**:
   - `OFFICIAL`: Formally audited statutory annual filings (SEC Form 10-K).
   - `PRIMARY`: Authoritative real-time exchange quote telemetry.
   - `REGULATORY`: Enforcement actions and statutory circulars.
   - `SECONDARY`: Third-party financial aggregators and market analysts.
2. **Conflict Disclosure**:
   - If two market providers diverge by $> 2.0\%$, MATS does not silently average or pick one. It explicitly issues a `SOURCE CONFLICT DETECTED` notice disclosing both values.

---

## 4. Privacy, Portability & Right to Erasure
- **GDPR & DPDP Compliance**: Retail users maintain complete sovereignty over their data.
- **Data Portability**: Users can export all portfolio records, watchlists, research theses, and alerts in standard JSON or CSV at any time via `GET /api/v1/ecosystem/export`.
- **Complete Erasure**: Account deletion (`DELETE /api/v1/user/me`) triggers cascading purge across all user portfolios, watchlists, copilot sessions, and alerts.
