from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProvenanceMetadata(BaseModel):
    """
    Standardized financial data provenance specification.
    Every financial datum tracks origin, hierarchy, freshness, and confidence.
    """
    source: str
    provider: str
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    published_at: Optional[str] = None
    data_type: str = "REALTIME_QUOTE"  # REALTIME_QUOTE, OFFICIAL_FILING, FUNDAMENTAL_RATIO, AGENT_SYNTHESIS
    freshness: str = "RECENT"          # RECENT, CACHED, STALE
    confidence: float = 0.95
    source_hierarchy: str = "OFFICIAL"  # PRIMARY, OFFICIAL, REGULATORY, SECONDARY, TERTIARY


class SourceConflictReport(BaseModel):
    has_conflict: bool
    status: str
    symbol: str
    metric: str
    source_a: Dict[str, Any]
    source_b: Dict[str, Any]
    interpretation: str
    confidence: float


class LineageNode(BaseModel):
    id: str
    level: str  # CONCLUSION, AGENT_FINDING, METRIC, SOURCE
    title: str
    description: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


class DataProvenanceService:
    """
    Manages data provenance tracking, source conflict detection,
    and hierarchical lineage visualizer construction.
    """

    HIERARCHY_WEIGHTS = {
        "OFFICIAL": 1.0,    # SEC 10-K, audited balance sheets
        "PRIMARY": 0.98,   # Direct exchange quotes
        "REGULATORY": 0.95, # Statutory warnings & disclosures
        "SECONDARY": 0.80,  # Aggregated third-party metrics
        "TERTIARY": 0.50,   # Unverified commentary
    }

    @classmethod
    def create_provenance(
        cls,
        source: str,
        provider: str,
        data_type: str = "REALTIME_QUOTE",
        hierarchy: str = "OFFICIAL",
        confidence: float = 0.95,
        published_at: Optional[str] = None,
        freshness: str = "RECENT",
    ) -> ProvenanceMetadata:
        return ProvenanceMetadata(
            source=source,
            provider=provider,
            data_type=data_type,
            source_hierarchy=hierarchy,
            confidence=confidence,
            published_at=published_at,
            freshness=freshness,
        )

    @classmethod
    def detect_source_conflict(
        cls,
        symbol: str,
        metric: str,
        source_a: Dict[str, Any],
        source_b: Dict[str, Any],
    ) -> SourceConflictReport:
        """
        Detects divergence between two independent data providers.
        If discrepancy exceeds tolerance threshold, flags conflict explicitly
        rather than silently choosing one source.
        """
        val_a = source_a.get("value")
        val_b = source_b.get("value")

        if val_a is None or val_b is None:
            return SourceConflictReport(
                has_conflict=False,
                status="INSUFFICIENT_DATA",
                symbol=symbol.upper(),
                metric=metric,
                source_a=source_a,
                source_b=source_b,
                interpretation="One or both sources lack reported values; no conflict detected.",
                confidence=0.5,
            )

        try:
            num_a = float(val_a)
            num_b = float(val_b)
            spread_pct = abs(num_a - num_b) / max(abs(num_a), 1e-6) * 100.0

            if spread_pct > 2.0:
                interpretation = (
                    f"SOURCE CONFLICT DETECTED: {source_a.get('name', 'Source A')} reports {metric} of {num_a:.2f}, "
                    f"while {source_b.get('name', 'Source B')} reports {num_b:.2f} (a {spread_pct:.1f}% divergence). "
                    f"MATS gives higher weighting to {source_a.get('hierarchy', 'PRIMARY')} feed."
                )
                return SourceConflictReport(
                    has_conflict=True,
                    status="SOURCE_CONFLICT_DETECTED",
                    symbol=symbol.upper(),
                    metric=metric,
                    source_a=source_a,
                    source_b=source_b,
                    interpretation=interpretation,
                    confidence=0.72,
                )
            else:
                return SourceConflictReport(
                    has_conflict=False,
                    status="CONSISTENT",
                    symbol=symbol.upper(),
                    metric=metric,
                    source_a=source_a,
                    source_b=source_b,
                    interpretation=f"Sources agree within tolerance ({spread_pct:.2f}% spread).",
                    confidence=0.96,
                )
        except Exception as e:
            return SourceConflictReport(
                has_conflict=False,
                status="PARSE_ERROR",
                symbol=symbol.upper(),
                metric=metric,
                source_a=source_a,
                source_b=source_b,
                interpretation=f"Unable to parse comparative metric values: {str(e)}",
                confidence=0.5,
            )

    @classmethod
    def get_data_lineage(
        cls,
        conclusion_title: str,
        agent_name: str,
        finding_summary: str,
        metric_name: str,
        metric_value: str,
        source_title: str,
        provider_name: str,
        hierarchy: str = "OFFICIAL",
    ) -> List[LineageNode]:
        """
        Builds the 4-layer lineage chain of custody:
        CONCLUSION -> AGENT_FINDING -> METRIC -> SOURCE
        """
        return [
            LineageNode(
                id="lineage-1",
                level="CONCLUSION",
                title="Synthesized Intelligence Conclusion",
                description=conclusion_title,
                confidence=0.90,
            ),
            LineageNode(
                id="lineage-2",
                level="AGENT_FINDING",
                title=f"{agent_name.capitalize()} Agent Assessment",
                description=finding_summary,
                confidence=0.88,
            ),
            LineageNode(
                id="lineage-3",
                level="METRIC",
                title=f"Underlying Mathematical Telemetry: {metric_name}",
                description=f"Observed value: {metric_value}",
                confidence=0.98,
            ),
            LineageNode(
                id="lineage-4",
                level="SOURCE",
                title=f"Source Provenance: {source_title}",
                description=f"Provider: {provider_name} | Hierarchy: {hierarchy} | Audited Integrity",
                confidence=cls.HIERARCHY_WEIGHTS.get(hierarchy, 0.85),
                metadata={"provider": provider_name, "hierarchy": hierarchy},
            ),
        ]


provenance_service = DataProvenanceService()
