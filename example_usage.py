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
