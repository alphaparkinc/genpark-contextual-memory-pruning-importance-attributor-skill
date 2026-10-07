# genpark-contextual-memory-pruning-importance-attributor-skill

[![GenPark AI](https://img.shields.io/badge/GenPark-AI%20Skill-blue.svg)](https://genpark.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-0%20(Pure%20Stdlib)-brightgreen.svg)](requirements.txt)
[![MCP Compliant](https://img.shields.io/badge/MCP-JSON--RPC%202.0-purple.svg)](mcp_server.py)

Autonomous Long-Horizon Agentic Memory Pruning & Importance Attributor. Evaluates multi-turn episodic memory buffers, calculates multi-factor salience scores (recency decay, user priority pinning, emotional valence, and entity graph connectivity), and deterministically prunes low-utility noise to respect model context limits.

---

## 🌟 Key Features

- **100% Zero External Dependencies**: Runs entirely on the Python 3.9+ standard library.
- **Model Context Protocol (MCP) Standard**: Native support for JSON-RPC 2.0 `initialize`, `tools/list`, and `tools/call`.
- **Industrial-Grade Determinism**: Rigorous exception isolation, predictable algorithmic complexity, and type annotations.
- **Dual Deployment Ecosystem**: Verified across `alphaparkinc` and `Alpha-Park` organizations with multi-account validation.

---

## 🚀 Quick Start

### 1. Direct Python SDK Usage

```python
"""Example usage for ContextualMemoryPruningImportanceAttributor."""
import sys
import json
import time
from client import ContextualMemoryPruningImportanceAttributor

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=== Long-Horizon Contextual Memory Pruning Demo ===")
    attributor = ContextualMemoryPruningImportanceAttributor()
    now = time.time()

    memory_pool = [
        {
            "id": "mem_01",
            "content": "User account ID: ACC-99412, Stripe Customer ID: CUST-STRIPE-7788",
            "timestamp": now - 7200,
            "access_count": 28,
            "is_pinned": True
        },
        {
            "id": "mem_02",
            "content": "User mentioned liking black coffee with oat milk on Monday morning.",
            "timestamp": now - 86400 * 5,
            "access_count": 2,
            "is_pinned": False
        },
        {
            "id": "mem_03",
            "content": "Autonomous deployment target: Tencent Cloud CVM cluster cvm-sh-prod-02.",
            "timestamp": now - 1800,
            "access_count": 14,
            "is_pinned": False
        },
        {
            "id": "mem_04",
            "content": "Random greeting: 'Hey agent how are you today doing fine'.",
            "timestamp": now - 86400 * 10,
            "access_count": 1,
            "is_pinned": False
        }
    ]

    print("\n--- 1. Evaluating Multi-Factor Importance Attribution ---")
    for m in memory_pool:
        score = attributor.attribute_memory_importance(m)
        print(f"[{m['id']}] Score: {score:.3f} | Pinned: {m.get('is_pinned', False)} | Text: '{m['content'][:45]}...'")

    print("\n--- 2. Pruning Memories to Strict Token Budget (40 Tokens) ---")
    pruned_res = attributor.prune_contextual_memories(memory_pool, target_token_budget=40)
    print(f"Initial Tokens: {pruned_res['initial_tokens']} -> Retained Tokens: {pruned_res['retained_tokens']}")
    print(f"Savings: {pruned_res['token_savings_pct']}% | Retained Nodes: {pruned_res['retained_memory_count']}/{pruned_res['initial_memory_count']}")
    print("Retained Memory IDs:", [m["id"] for m in pruned_res["retained_memories"]])
    print("Pruned Memory IDs:", pruned_res["pruned_memory_ids"])

if __name__ == "__main__":
    main()

```

### 2. Run as Model Context Protocol (MCP) Server

Start standard JSON-RPC 2.0 server over `stdio`:

```bash
python mcp_server.py
```

Execute embedded test harness:

```bash
python mcp_server.py --test
```

---

## 🛠️ MCP Tool Specification

Inspect [`skill.json`](skill.json) for parameter schemas and tool definitions compatible with Anthropic Claude, Meta Muse, and OpenAI Function Calling formats.

---

## 📜 License

Licensed under the [MIT License](LICENSE). Copyright © 2026 GenPark AI.
