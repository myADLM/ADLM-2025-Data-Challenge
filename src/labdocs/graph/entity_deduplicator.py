"""Entity and relationship deduplication using Levenshtein distance and LLM confirmation."""
import re
import json
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Tuple

from .config import DeduplicationConfig


class EntityDeduplicator:
    """
    Two-level entity deduplication:
    Level 1A: Exact canonical ID match
    Level 1B: Levenshtein distance on normalized names
    Level 3: LLM confirmation for uncertain cases
    """

    def __init__(self, graph_store, bedrock_llm=None, config: DeduplicationConfig = None):
        self.graph_store = graph_store
        self.bedrock_llm = bedrock_llm
        self.config = config or DeduplicationConfig()

    def deduplicate(self, extracted_entities: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Process extracted entities and deduplicate against existing graph.
        Returns deduplicated entity list with detailed dedup stats.
        """
        result = []
        dedup_stats = {
            "total_extracted": len(extracted_entities),
            "exact_matches": 0,
            "levenshtein_matches": 0,
            "llm_sent_to_confirm": 0,
            "llm_confirmed": 0,
            "llm_rejected": 0,
            "new_entities": 0,
            "had_candidates": 0
        }

        for entity in extracted_entities:
            entity_id = entity.get("@id")
            entity_title = entity.get("title", "")
            entity_type = entity.get("@type", "")

            # LEVEL 1A: Exact canonical ID match
            existing = self._find_exact_match(entity_id)
            if existing:
                merged = self._merge_entity_properties(existing, entity)
                result.append(merged)
                dedup_stats["exact_matches"] += 1
                continue

            # LEVEL 1B: Levenshtein distance on normalized names
            candidates = self._find_close_matches(entity_title, entity_type)
            if candidates:
                dedup_stats["had_candidates"] += 1
                best_match = candidates[0]
                if best_match["similarity_score"] >= self.config.levenshtein_match_threshold:
                    merged = self._merge_entity_properties(best_match["node"], entity)
                    result.append(merged)
                    dedup_stats["levenshtein_matches"] += 1
                    continue

                # LEVEL 3: LLM reconciliation for unmatched entities
                if self.config.use_llm_reconciliation and self.bedrock_llm:
                    dedup_stats["llm_sent_to_confirm"] += 1
                    llm_merged = self._llm_confirm_match(entity, candidates)
                    if llm_merged:
                        result.append(llm_merged)
                        dedup_stats["llm_confirmed"] += 1
                        continue
                    else:
                        dedup_stats["llm_rejected"] += 1

            # No match found - new entity
            result.append(entity)
            dedup_stats["new_entities"] += 1

        return result, dedup_stats

    def _find_exact_match(self, entity_id: str) -> Optional[Dict]:
        """Find entity in graph by exact canonical ID."""
        try:
            query = "MATCH (n {canonical_id: $id}) RETURN n"
            result = self.graph_store.query(query, {"id": entity_id})
            if result:
                return result[0].get("n")
        except Exception:
            pass
        return None

    def _find_close_matches(self, entity_title: str, entity_type: str) -> List[Dict]:
        """
        Find similar entities in graph using normalized Levenshtein distance.
        Returns list sorted by similarity score (highest first).
        """
        candidates = []

        try:
            # Query graph for all nodes of same type or all nodes if type not critical
            query = "MATCH (n) RETURN n"
            all_nodes = self.graph_store.query(query)

            normalized_input = self._normalize_string(entity_title)

            for node_data in all_nodes:
                node = node_data.get("n")
                if not node:
                    continue

                node_title = node.get("title", "")
                normalized_existing = self._normalize_string(node_title)

                similarity = self._levenshtein_similarity(
                    normalized_input,
                    normalized_existing
                )

                if similarity >= self.config.levenshtein_candidate_threshold:
                    candidates.append({
                        "node": node,
                        "node_id": node.get("canonical_id"),
                        "title": node_title,
                        "similarity_score": similarity
                    })

            candidates.sort(key=lambda x: x["similarity_score"], reverse=True)

        except Exception:
            pass

        return candidates

    @staticmethod
    def _normalize_string(s: str) -> str:
        """
        Normalize string for comparison:
        - Lowercase
        - Remove special characters
        - Collapse whitespace
        """
        s = s.lower()
        s = re.sub(r'[^a-z0-9\s]', '', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    @staticmethod
    def _levenshtein_similarity(s1: str, s2: str) -> float:
        """
        Levenshtein distance normalized to 0-1 similarity score.
        Uses SequenceMatcher which is more efficient than raw Levenshtein.
        """
        return SequenceMatcher(None, s1, s2).ratio()

    def _llm_confirm_match(self, new_entity: Dict, candidates: List[Dict]) -> Optional[Dict]:
        """
        Use Bedrock LLM to confirm if new_entity matches any candidate.
        Returns merged entity if confirmed with high confidence, else None.
        """
        if not self.bedrock_llm:
            return None

        candidate_summaries = []
        for c in candidates[:3]:  # Only use top 3 candidates
            candidate_summaries.append({
                "id": c.get("node_id"),
                "title": c.get("title"),
                "similarity": round(c.get("similarity_score", 0), 2)
            })

        prompt = f"""Determine if these are the same entity:

NEW ENTITY:
ID: {new_entity.get('@id')}
Title: {new_entity.get('title')}
Type: {new_entity.get('@type')}
Description: {new_entity.get('description', 'N/A')}

EXISTING CANDIDATES:
{json.dumps(candidate_summaries, indent=2)}

Rules:
- Same entity if they refer to the same real-world object (e.g., same instrument, same procedure)
- Consider variations in naming, abbreviations, and terminology
- Be conservative - only confirm if highly confident (>= 0.85)

Respond ONLY with valid JSON (no markdown):
{{"is_same": true/false, "confidence": 0.0-1.0, "reason": "brief explanation", "matched_id": "ID or null"}}
"""

        try:
            response = self.bedrock_llm.complete(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)

            # Parse JSON response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                confidence = result.get("confidence", 0)

                if result.get("is_same") and confidence >= self.config.llm_confirmation_threshold:
                    # Find matched entity and merge
                    matched_id = result.get("matched_id")
                    for c in candidates:
                        if c.get("node_id") == matched_id:
                            merged = self._merge_entity_properties(c["node"], new_entity)
                            merged["_llm_confidence"] = confidence
                            return merged

        except Exception:
            pass

        return None

    @staticmethod
    def _merge_entity_properties(existing: Dict, new: Dict) -> Dict:
        """
        Merge properties from new entity into existing entity.
        Preserves existing entity ID, enriches properties.
        """
        merged = existing.copy()

        # Update properties that might have been enriched
        if "description" in new and not merged.get("description"):
            merged["description"] = new["description"]

        if "source_text" in new:
            if "source_texts" not in merged:
                merged["source_texts"] = []
            merged["source_texts"].append(new["source_text"])

        # Track that this was merged
        merged["_merged"] = True
        merged["_original_id"] = new.get("@id")

        return merged

    def deduplicate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """
        Deduplicate relationships by checking if they already exist in graph.
        """
        result = []
        dedup_stats = {
            "existing": 0,
            "new": 0
        }

        for rel in relationships:
            source_id = rel.get("source_id")
            target_id = rel.get("target_id")
            rel_type = rel.get("type")

            # Check if relationship already exists
            if self._relationship_exists(source_id, target_id, rel_type):
                dedup_stats["existing"] += 1
                continue

            result.append(rel)
            dedup_stats["new"] += 1

        return result, dedup_stats

    def _relationship_exists(self, source_id: str, target_id: str, rel_type: str) -> bool:
        """Check if relationship already exists in graph."""
        try:
            query = f"""
            MATCH (n1 {{canonical_id: $source_id}})
            -[r:{rel_type}]->
            (n2 {{canonical_id: $target_id}})
            RETURN COUNT(r) as count
            """
            result = self.graph_store.query(
                query,
                {"source_id": source_id, "target_id": target_id}
            )
            if result and result[0].get("count", 0) > 0:
                return True
        except Exception:
            pass
        return False
