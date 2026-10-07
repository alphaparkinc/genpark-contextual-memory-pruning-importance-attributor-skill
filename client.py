"""
Contextual Memory Pruning & Importance Attributor (Zero External Dependencies)
Calculates multi-dimensional salience attribution and executes deterministic token budget pruning.
"""
import time
import math
import hashlib
import json
import re
from typing import Dict, Any, List, Optional

class ContextualMemoryPruningImportanceAttributor:
    def __init__(self, default_half_life_hours: float = 48.0):
        self.default_half_life = default_half_life_hours

    def estimate_tokens(self, text: str) -> int:
        return max(1, int(len(text) / 3.8))

    def attribute_memory_importance(
        self,
        memory: Dict[str, Any],
        current_time: Optional[float] = None,
        half_life_hours: Optional[float] = None
    ) -> float:
        """
        Calculates composite importance score in [0.0, 1.0]:
        Score = w_pin * is_pinned + w_rec * decay + w_access * access_factor + w_entity * entity_weight
        """
        now = current_time or time.time()
        hl = half_life_hours or self.default_half_life

        # 1. Pinned override
        is_pinned = bool(memory.get("is_pinned", False))
        if is_pinned:
            return 1.0

        # 2. Recency exponential decay: exp(-ln(2) * dt / half_life)
        created_at = float(memory.get("timestamp", now))
        age_hours = max(0.0, (now - created_at) / 3600.0)
        recency_score = math.exp(-0.693147 * (age_hours / max(0.1, hl)))

        # 3. Access frequency factor
        access_count = int(memory.get("access_count", 1))
        access_score = min(1.0, math.log1p(access_count) / math.log1p(20))

        # 4. Critical entity density
        content = str(memory.get("content", ""))
        has_entities = bool(re.search(r"\b[A-Z0-9_-]{5,}\b|\$[0-9]+|\b(?:password|credential|email|id|contract)\b", content, re.IGNORECASE))
        entity_score = 0.8 if has_entities else 0.3

        # Weighted combination
        composite = (0.45 * recency_score) + (0.35 * access_score) + (0.20 * entity_score)
        return round(min(1.0, max(0.01, composite)), 3)

    def prune_contextual_memories(
        self,
        memories: List[Dict[str, Any]],
        target_token_budget: int = 1000,
        half_life_hours: Optional[float] = None
    ) -> Dict[str, Any]:
        """Ranks memory nodes by importance and prunes low-salience nodes to meet token budget."""
        now = time.time()
        scored_memories = []
        total_initial_tokens = 0

        for m in memories:
            tokens = self.estimate_tokens(m.get("content", ""))
            total_initial_tokens += tokens
            score = self.attribute_memory_importance(m, current_time=now, half_life_hours=half_life_hours)
            item = dict(m)
            item["estimated_tokens"] = tokens
            item["importance_score"] = score
            scored_memories.append(item)

        # Sort descending by importance score
        scored_memories.sort(key=lambda x: (x.get("is_pinned", False), x["importance_score"]), reverse=True)

        retained = []
        pruned = []
        accumulated_tokens = 0

        for m in scored_memories:
            toks = m["estimated_tokens"]
            if accumulated_tokens + toks <= target_token_budget or m.get("is_pinned", False):
                retained.append(m)
                accumulated_tokens += toks
            else:
                pruned.append(m)

        token_savings_pct = round(((total_initial_tokens - accumulated_tokens) / max(1, total_initial_tokens)) * 100.0, 1)

        return {
            "initial_memory_count": len(memories),
            "retained_memory_count": len(retained),
            "pruned_memory_count": len(pruned),
            "initial_tokens": total_initial_tokens,
            "retained_tokens": accumulated_tokens,
            "target_token_budget": target_token_budget,
            "token_savings_pct": max(0.0, token_savings_pct),
            "retained_memories": retained,
            "pruned_memory_ids": [p.get("id") or p.get("memory_id") for p in pruned]
        }
