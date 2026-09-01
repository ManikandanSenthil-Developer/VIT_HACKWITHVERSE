export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user?: User;
}

export interface InvestorProfile {
  id: number;
  user_id: number;
  risk_tolerance: 'conservative' | 'moderate' | 'aggressive' | 'speculative';
  investment_horizon: 'short' | 'medium' | 'long';
  preferred_sectors: string;
  target_return: number;
  experience_level: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Watchlist {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  symbols: string;
  created_at: string;
  updated_at: string;
}

export interface Holding {
  id: number;
  portfolio_id: number;
  symbol: string;
  asset_type: string;
  quantity: number;
  buy_price: number;
  current_value: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Portfolio {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  total_value: number;
  cash_balance: number;
  currency: string;
  holdings: Holding[];
  created_at: string;
  updated_at: string;
}

// Dashboard Specific Types
export interface KpiMetric {
  title: string;
  value: string;
  subValue?: string;
  change: string;
  isPositive: boolean;
  period: string;
  iconName: 'DollarSign' | 'Users' | 'CreditCard' | 'TrendingUp';
  accentColor: 'purple' | 'orange' | 'emerald' | 'blue';
}

export interface RevenueForecastPoint {
  month: string;
  actual: number;
  predicted: number;
  baseline: number;
}

export interface AiAlert {
  id: string;
  type: 'opportunity' | 'risk' | 'anomaly' | 'rebalance';
  title: string;
  description: string;
  confidence: number;
  timestamp: string;
  symbol?: string;
  impact: 'high' | 'medium' | 'low';
}

export interface NetworkNode {
  id: string;
  name: string;
  type: string;
  status: 'Active' | 'Optimizing' | 'Standby' | 'Audited';
  latency: string;
  throughput: string;
  accuracy: string;
  lastUpdated: string;
}

// Phase 2: Market Data Types
export interface MarketResponseWrapper<T> {
  data: T;
  source: string;
  retrieved_at: string;
  fresh: boolean;
  cached: boolean;
  status_note?: string;
}

export interface MarketQuote {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  high_52w?: number;
  low_52w?: number;
  pe_ratio?: number;
  market_cap?: number;
  timestamp: string;
}

export interface PricePoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  adjusted_close: number;
  volume: number;
}

export interface HistoricalPriceData {
  symbol: string;
  period: string;
  count: number;
  prices: PricePoint[];
}

export interface CompanyProfile {
  symbol: string;
  name: string;
  exchange: string;
  sector?: string;
  industry?: string;
  description?: string;
  country?: string;
  website?: string;
  market_cap?: number;
}

export interface FundamentalData {
  symbol: string;
  period_type: string;
  fiscal_year?: number;
  fiscal_quarter?: number;
  report_date?: string;
  revenue?: number;
  net_income?: number;
  eps?: number;
  free_cash_flow?: number;
  pe_ratio?: number;
  pb_ratio?: number;
  debt_to_equity?: number;
  metrics_breakdown?: Record<string, any>;
}

// Phase 2: RAG Knowledge Engine Types
export interface RagCitation {
  document_id: number;
  document_title: string;
  company_symbol: string;
  document_type: string;
  source_url?: string;
  publication_date?: string;
  section?: string;
  page_number?: number;
}

export interface RagSearchResultItem {
  text: string;
  score: number;
  source: string;
  document: string;
  metadata: Record<string, any>;
  citation: RagCitation;
}

export interface RagSearchResponse {
  query: string;
  results_found: boolean;
  results: RagSearchResultItem[];
  message?: string;
  query_latency_ms: number;
}

export interface DocumentItem {
  id: number;
  title: string;
  company_symbol: string;
  document_type: string;
  source_url?: string;
  source_identifier?: string;
  publication_date?: string;
  retrieval_date: string;
  chunk_count: number;
  status: string;
  error_message?: string;
  created_at: string;
}

// Phase 3: Multi-Agent Intelligence Types
export interface AgentFinding {
  agent: string;
  finding: string;
  signal: 'BULLISH' | 'BEARISH' | 'NEUTRAL' | 'CAUTIOUS';
  confidence: number;
  evidence: string[];
  source_ids: string[];
  timestamp: string;
  limitations: string[];
  metrics?: Record<string, any>;
}

export interface SignalConflict {
  conflict_type: string;
  conflicting_agents: string[];
  conflicting_signals: Record<string, string>;
  description: string;
  severity: 'high' | 'medium' | 'low';
  evidence_summary: string[];
}

export interface ReasoningTrace {
  data_considered: string[];
  agents_consulted: string[];
  major_findings: string[];
  conflicts_detected: string[];
  evidence_used: string[];
  final_assessment: string;
  confidence: number;
  limitations: string[];
}

export interface Recommendation {
  assessment: string;
  confidence: number;
  key_reasons: string[];
  risks: string[];
  what_to_monitor: string[];
  sources: string[];
  personalization_note?: string;
}

export interface AnalysisResponse {
  request_id: string;
  status: 'completed' | 'partial_failure' | 'failed';
  symbol: string;
  query: string;
  summary: string;
  overall_assessment: string;
  confidence: number;
  agents: AgentFinding[];
  successful_agents: string[];
  failed_agents: Array<{ agent: string; reason: string }>;
  conflicts: SignalConflict[];
  recommendation: Recommendation;
  reasoning_trace: ReasoningTrace;
  sources: string[];
  freshness: {
    retrieved_at: string;
    execution_times_ms: Record<string, number>;
  };
  limitations: string[];
  execution_time_ms: number;
  disclosures: string[];
}

export interface AnalysisHistoryItem {
  id: number;
  request_id: string;
  symbol: string;
  query: string;
  analysis_type: string;
  overall_assessment: string;
  confidence: number;
  execution_time_ms: number;
  created_at: string;
}

export interface AgentStatusInfo {
  agent_id: string;
  name: string;
  role: string;
  status: 'online' | 'ready' | 'degraded';
  capabilities: string[];
}

// Phase 4: Risk Engine, Scenarios, and Proactive Monitoring Types
export interface PositionHealth {
  symbol: string;
  quantity: number;
  buy_price: number;
  current_price: number;
  current_value: number;
  unrealized_pnl: number;
  pnl_percent: number;
  weight_percent: number;
  sector: string;
}

export interface SectorExposure {
  sector: string;
  value: number;
  weight_percent: number;
}

export interface RiskScoreFactor {
  factor: string;
  weight: number;
  contribution: number;
  description: string;
}

export interface RiskScoreExplanation {
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  risk_score: number;
  reasons: string[];
  factor_contributions: RiskScoreFactor[];
}

export interface PortfolioHealthResponse {
  portfolio_id: number;
  name: string;
  total_value: number;
  cash_balance: number;
  invested_value: number;
  total_unrealized_pnl: number;
  total_return_percent: number;
  currency: string;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  risk_score: number;
  risk_explanation: RiskScoreExplanation;
  concentration_top_asset_weight: number;
  concentration_hhi: number;
  sector_breakdown: SectorExposure[];
  positions: PositionHealth[];
  largest_risk_exposure: string;
  annualized_volatility: number;
  max_historical_drawdown: number;
  watchlist_overlap: string[];
  data_freshness: Record<string, string>;
}

export interface ScenarioHoldingImpact {
  symbol: string;
  current_price: number;
  scenario_price: number;
  current_value: number;
  scenario_value: number;
  value_difference: number;
  difference_percent: number;
}

export interface ScenarioResponse {
  portfolio_id: number;
  scenario_name: string;
  shock_type: string;
  target: string;
  percentage_change: number;
  current_total_value: number;
  scenario_total_value: number;
  total_difference_usd: number;
  total_difference_percent: number;
  holdings_impact: ScenarioHoldingImpact[];
  disclaimer: string;
}

export interface ScenarioRequest {
  portfolio_id: number;
  shock_type?: string;
  target_symbol?: string;
  target_sector?: string;
  percentage_change: number;
  quantity_adjustment?: number;
}

export interface AlertItem {
  id: number;
  user_id: number;
  event_id?: number;
  symbol: string;
  priority: 'URGENT' | 'IMPORTANT' | 'FYI';
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title: string;
  explanation: string;
  agent_synthesis_json?: string;
  status: 'NEW' | 'SEEN' | 'ACKNOWLEDGED' | 'DISMISSED' | 'RESOLVED';
  feedback: 'HELPFUL' | 'NOT_HELPFUL' | 'UNSPECIFIED';
  created_at: string;
  seen_at?: string;
}

export interface DailyBriefResponse {
  date: string;
  portfolio_summary: string;
  portfolio_return_today_pct: number;
  key_developments: Array<{
    symbol: string;
    title: string;
    priority: string;
    severity: string;
    summary: string;
  }>;
  what_deserves_attention: string[];
  what_changed: string[];
  sources_analyzed: string[];
  disclaimer: string;
}

export interface MonitoringRunResponse {
  run_id: number;
  run_type: string;
  status: string;
  events_detected: number;
  alerts_created: number;
  execution_time_ms: number;
  created_at: string;
  error_message?: string;
}

// Phase 7: Investor Copilot & Comparative Research Types
export interface CopilotChatResponse {
  conversation_id: number;
  message_id: number;
  intent: string;
  summary: string;
  key_findings: string[];
  evidence: string[];
  risks: string[];
  counterarguments: string[];
  follow_ups: string[];
  tool_calls: string[];
  citations: string[];
}

export interface CopilotConversationItem {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface CopilotMessageItem {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  intent?: string;
  tool_calls: string[];
  citations: string[];
  created_at: string;
}

export interface CompanyComparisonResponse {
  symbol_a: string;
  symbol_b: string;
  is_peers: boolean;
  relative_insights: string[];
  company_a: {
    profile: { name: string; sector: string; industry: string };
    market: { price: number | string; change_percent: number | string; volume: number | string; market_cap: number | string };
    fundamentals: { fiscal_year: number | string; pe_ratio: number | string; pb_ratio: number | string; debt_to_equity: number | string; revenue: number | string; net_income: number | string; free_cash_flow: number | string };
    technical: { signal: string; confidence: number; summary: string };
    sentiment: { signal: string; confidence: number; summary: string };
    top_citation: string;
  };
  company_b: {
    profile: { name: string; sector: string; industry: string };
    market: { price: number | string; change_percent: number | string; volume: number | string; market_cap: number | string };
    fundamentals: { fiscal_year: number | string; pe_ratio: number | string; pb_ratio: number | string; debt_to_equity: number | string; revenue: number | string; net_income: number | string; free_cash_flow: number | string };
    technical: { signal: string; confidence: number; summary: string };
    sentiment: { signal: string; confidence: number; summary: string };
    top_citation: string;
  };
  disclaimer: string;
}

export interface ThesisResponse {
  id?: number;
  symbol: string;
  company_name: string;
  title: string;
  summary: string;
  bull_case: string[];
  bear_case: string[];
  counterarguments: string[];
  invalidation_conditions: string[];
  what_to_monitor: string[];
  evidence_citations: Array<{
    source: string;
    document_title: string;
    section: string;
    reliability_weight: number;
    recency_weight: number;
    excerpt: string;
  }>;
  created_at: string;
  disclaimer: string;
}

export interface DecisionJournalItem {
  id: number;
  symbol: string;
  thesis_title: string;
  reason: string;
  risk_assessment?: string;
  confidence: number;
  notes?: string;
  status: 'ACTIVE' | 'SUPPORTED' | 'PARTIALLY_SUPPORTED' | 'CONTRADICTED';
  date: string;
  last_reviewed_at?: string;
  review_notes?: string;
}

export interface ScreenerResultItem {
  symbol: string;
  name: string;
  sector: string;
  price: number | string;
  change_percent: number | string;
  pe_ratio: number | string;
  debt_to_equity: number | string;
  revenue: number | string;
  why_included: string;
}

export interface TimelineItem {
  type: 'ANALYSIS' | 'DOCUMENT' | 'MARKET_EVENT' | 'ALERT';
  timestamp: string;
  title: string;
  summary: string;
  confidence?: number;
  severity?: string;
  priority?: string;
  trust_level?: string;
  id: number;
}

// Phase 8: Ecosystem, Accessibility, Multilingual Voice, Provenance & Portability
export interface UserAccessibilityPreference {
  language: 'en' | 'ta' | 'hi';
  text_size: 'normal' | 'large' | 'extra_large';
  reduced_motion: boolean;
  high_contrast: boolean;
  voice_enabled: boolean;
  updated_at?: string;
}

export interface ImpactMetrics {
  users_onboarded: number;
  analyses_completed: number;
  alerts_generated: number;
  estimated_research_time_saved_hours: number;
  time_savings_metric_type: string;
  languages_supported_count: number;
  supported_languages: string[];
  voice_interactions_enabled: boolean;
  accessible_modes_available: string[];
  decision_support_boundary: string;
}

export interface ProviderHealthItem {
  name: string;
  provider_type: string;
  status: string;
  latency_ms: number;
  failure_rate_pct: number;
  last_heartbeat: string;
}

export interface EducationConcept {
  concept: string;
  title: string;
  simple_definition: string;
  example: string;
  why_it_matters: string;
  limitations: string;
  disclaimer: string;
}

export interface SourceConflictReport {
  has_conflict: boolean;
  status: string;
  symbol: string;
  metric: string;
  source_a: { name: string; value: number; hierarchy: string };
  source_b: { name: string; value: number; hierarchy: string };
  interpretation: string;
  confidence: number;
}

export interface CsvImportResult {
  portfolio_id: number;
  total_rows_evaluated: number;
  valid_count: number;
  rejected_count: number;
  valid_rows: Array<{ symbol: string; quantity: number; buy_price: number; current_value: number }>;
  rejected_rows: Array<{ line?: number; symbol?: string; reason: string }>;
  message: string;
}

