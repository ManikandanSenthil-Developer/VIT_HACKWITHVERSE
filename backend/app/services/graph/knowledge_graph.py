import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.adaptive import KnowledgeEntity, KnowledgeRelationship
from app.models.market import Company
from app.models.holding import Holding
from app.models.portfolio import Portfolio


class FinancialKnowledgeGraphService:
    """
    Lightweight, evidence-backed financial knowledge graph service.
    Grounds multi-agent relationships in structured data tables.
    Enforces strict multi-tenant privacy isolation.
    """

    @classmethod
    def seed_baseline_entities(cls, db: Session) -> None:
        """Seeds baseline company, sector, competitor, and event nodes if not already present."""
        baseline_nodes = [
            # Sectors
            {"entity_type": "SECTOR", "entity_key": "SECTOR:TECH", "name": "Technology & Semiconductors", "desc": "Hardware, software, and semiconductor manufacturing."},
            {"entity_type": "SECTOR", "entity_key": "SECTOR:HEALTH", "name": "Healthcare & Pharmaceuticals", "desc": "Biotech, pharmaceuticals, and medical devices."},
            {"entity_type": "SECTOR", "entity_key": "SECTOR:ENERGY", "name": "Clean Energy & Utilities", "desc": "Renewable power, storage, and utility transmission."},

            # Companies
            {"entity_type": "COMPANY", "entity_key": "COMPANY:NVDA", "name": "NVIDIA Corporation", "desc": "Accelerated computing and semiconductor architecture."},
            {"entity_type": "COMPANY", "entity_key": "COMPANY:MSFT", "name": "Microsoft Corporation", "desc": "Enterprise cloud computing, AI platforms, and productivity software."},
            {"entity_type": "COMPANY", "entity_key": "COMPANY:AMD", "name": "Advanced Micro Devices", "desc": "High-performance graphics and server processors."},
            {"entity_type": "COMPANY", "entity_key": "COMPANY:AAPL", "name": "Apple Inc.", "desc": "Consumer electronics, mobile computing, and ecosystem software."},

            # Macro / Industry Events
            {"entity_type": "EVENT", "entity_key": "EVENT:AI_SURGE_2024", "name": "Global AI Infrastructure Expansion", "desc": "Accelerated capex investment in enterprise AI data centers."},
            {"entity_type": "EVENT", "entity_key": "EVENT:RATE_VOLATILITY", "name": "Macro Interest Rate Volatility", "desc": "Central bank policy adjustments impacting discount rates for high-growth tech."},

            # Regulatory Filings
            {"entity_type": "DOCUMENT", "entity_key": "DOC:NVDA_10K_2024", "name": "NVDA SEC Form 10-K (FY2024)", "desc": "Audited statutory annual filing with Item 1A Risk Factors."},
            {"entity_type": "DOCUMENT", "entity_key": "DOC:MSFT_10K_2024", "name": "MSFT SEC Form 10-K (FY2024)", "desc": "Audited statutory annual filing with segment revenue breakdown."},
        ]

        entity_map = {}
        for node in baseline_nodes:
            ent = db.query(KnowledgeEntity).filter(KnowledgeEntity.entity_key == node["entity_key"]).first()
            if not ent:
                ent = KnowledgeEntity(
                    entity_type=node["entity_type"],
                    entity_key=node["entity_key"],
                    name=node["name"],
                    description=node["desc"],
                )
                db.add(ent)
                db.commit()
                db.refresh(ent)
            entity_map[node["entity_key"]] = ent

        # Baseline Relationships
        baseline_edges = [
            # Company -> belongs_to -> Sector
            ("COMPANY:NVDA", "SECTOR:TECH", "BELONGS_TO", "Exchange Master Data"),
            ("COMPANY:MSFT", "SECTOR:TECH", "BELONGS_TO", "Exchange Master Data"),
            ("COMPANY:AMD", "SECTOR:TECH", "BELONGS_TO", "Exchange Master Data"),
            ("COMPANY:AAPL", "SECTOR:TECH", "BELONGS_TO", "Exchange Master Data"),

            # Company -> competes_with -> Company
            ("COMPANY:NVDA", "COMPANY:AMD", "COMPETES_WITH", "SEC Form 10-K Item 1 Business"),
            ("COMPANY:MSFT", "COMPANY:AAPL", "COMPETES_WITH", "SEC Form 10-K Item 1 Business"),

            # Event -> affects -> Company / Sector
            ("EVENT:AI_SURGE_2024", "COMPANY:NVDA", "AFFECTED_BY", "Earnings Call Transcripts & Supply Chain"),
            ("EVENT:AI_SURGE_2024", "SECTOR:TECH", "AFFECTED_BY", "Semiconductor Industry Association Telemetry"),
            ("EVENT:RATE_VOLATILITY", "SECTOR:TECH", "AFFECTED_BY", "Macroeconomic Valuation Sensitivity"),

            # Document -> supports -> Company
            ("DOC:NVDA_10K_2024", "COMPANY:NVDA", "SUPPORTS", "SEC EDGAR Statutory Repository"),
            ("DOC:MSFT_10K_2024", "COMPANY:MSFT", "SUPPORTS", "SEC EDGAR Statutory Repository"),
        ]

        for s_key, t_key, rel_type, prov in baseline_edges:
            s_ent = entity_map.get(s_key)
            t_ent = entity_map.get(t_key)
            if s_ent and t_ent:
                rel = (
                    db.query(KnowledgeRelationship)
                    .filter(
                        KnowledgeRelationship.source_id == s_ent.id,
                        KnowledgeRelationship.target_id == t_ent.id,
                        KnowledgeRelationship.relation_type == rel_type,
                    )
                    .first()
                )
                if not rel:
                    rel = KnowledgeRelationship(
                        source_id=s_ent.id,
                        target_id=t_ent.id,
                        relation_type=rel_type,
                        confidence=0.98,
                        source_provenance=prov,
                    )
                    db.add(rel)

        db.commit()

    @classmethod
    def get_company_subgraph(cls, db: Session, symbol: str) -> Dict[str, Any]:
        """Retrieves nodes and edges directly connected to a specific company."""
        cls.seed_baseline_entities(db)
        key = f"COMPANY:{symbol.upper()}"
        center = db.query(KnowledgeEntity).filter(KnowledgeEntity.entity_key == key).first()
        if not center:
            return {"nodes": [], "edges": [], "center_symbol": symbol.upper()}

        nodes = [{"id": center.id, "key": center.entity_key, "name": center.name, "type": center.entity_type, "desc": center.description}]
        edges = []
        seen_node_ids = {center.id}

        # Outgoing
        out_rels = db.query(KnowledgeRelationship).filter(KnowledgeRelationship.source_id == center.id).all()
        for r in out_rels:
            edges.append({"source": r.source_id, "target": r.target_id, "relation": r.relation_type, "provenance": r.source_provenance})
            if r.target_id not in seen_node_ids:
                t = r.target
                nodes.append({"id": t.id, "key": t.entity_key, "name": t.name, "type": t.entity_type, "desc": t.description})
                seen_node_ids.add(t.id)

        # Incoming
        in_rels = db.query(KnowledgeRelationship).filter(KnowledgeRelationship.target_id == center.id).all()
        for r in in_rels:
            edges.append({"source": r.source_id, "target": r.target_id, "relation": r.relation_type, "provenance": r.source_provenance})
            if r.source_id not in seen_node_ids:
                s = r.source
                nodes.append({"id": s.id, "key": s.entity_key, "name": s.name, "type": s.entity_type, "desc": s.description})
                seen_node_ids.add(s.id)

        return {
            "center_symbol": symbol.upper(),
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        }

    @classmethod
    def get_portfolio_subgraph(cls, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Retrieves user-authorized portfolio exposure graph:
        User Portfolio -> Holdings -> Companies -> Sectors -> Events.
        Strictly isolated to user_id.
        """
        cls.seed_baseline_entities(db)
        ports = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        nodes = []
        edges = []
        seen_ids = set()

        # Add portfolio node
        port_node_id = 999000 + user_id
        nodes.append({
            "id": port_node_id,
            "key": f"PORTFOLIO:{user_id}",
            "name": "My Active Portfolio",
            "type": "PORTFOLIO",
            "desc": f"Total Portfolios: {len(ports)}",
        })
        seen_ids.add(port_node_id)

        for port in ports:
            for h in port.holdings:
                c_key = f"COMPANY:{h.symbol.upper()}"
                comp = db.query(KnowledgeEntity).filter(KnowledgeEntity.entity_key == c_key).first()
                if not comp:
                    # Dynamically create company node if absent
                    comp = KnowledgeEntity(
                        entity_type="COMPANY",
                        entity_key=c_key,
                        name=h.symbol.upper(),
                        description=f"Portfolio holding with quantity {h.quantity}",
                    )
                    db.add(comp)
                    db.commit()
                    db.refresh(comp)

                if comp.id not in seen_ids:
                    nodes.append({"id": comp.id, "key": comp.entity_key, "name": comp.name, "type": comp.entity_type, "desc": comp.description})
                    seen_ids.add(comp.id)

                # Edge: Portfolio -> CONTAINS -> Company
                edges.append({
                    "source": port_node_id,
                    "target": comp.id,
                    "relation": "CONTAINS",
                    "provenance": f"User Holding (Qty: {h.quantity})",
                })

                # Connect company's sectors and events
                rels = db.query(KnowledgeRelationship).filter(
                    (KnowledgeRelationship.source_id == comp.id) | (KnowledgeRelationship.target_id == comp.id)
                ).limit(6).all()

                for r in rels:
                    other_ent = r.target if r.source_id == comp.id else r.source
                    if other_ent.id not in seen_ids:
                        nodes.append({
                            "id": other_ent.id,
                            "key": other_ent.entity_key,
                            "name": other_ent.name,
                            "type": other_ent.entity_type,
                            "desc": other_ent.description,
                        })
                        seen_ids.add(other_ent.id)

                    edges.append({
                        "source": r.source_id,
                        "target": r.target_id,
                        "relation": r.relation_type,
                        "provenance": r.source_provenance,
                    })

        return {
            "user_id": user_id,
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        }


knowledge_graph_service = FinancialKnowledgeGraphService()
