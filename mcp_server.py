"""MCP Server for Contextual Memory Pruning Importance Attributor."""
import sys
import json
import time
from client import ContextualMemoryPruningImportanceAttributor

attributor = ContextualMemoryPruningImportanceAttributor()

def handle_call_tool(params):
    name = params.get("name")
    args = params.get("arguments", {})
    if name != "prune_agentic_memory":
        raise ValueError(f"Unknown tool: {name}")

    action = args.get("action", "prune_contextual_memories")
    memories = args.get("memories", [])
    budget = int(args.get("target_token_budget", 500))
    hl = args.get("half_life_hours")

    if action == "attribute_memory_importance":
        scored = []
        for m in memories:
            sc = attributor.attribute_memory_importance(m, half_life_hours=hl)
            scored.append({"memory_id": m.get("id"), "score": sc})
        return {"scored_memories": scored}
    elif action == "prune_contextual_memories":
        return attributor.prune_contextual_memories(memories, target_token_budget=budget, half_life_hours=hl)
    else:
        raise ValueError(f"Invalid action: {action}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running self-test...")
        now = time.time()
        memories = [
            {"id": "m1", "content": "Critical user master key: SK-PROD-99120", "is_pinned": True, "timestamp": now - 100000},
            {"id": "m2", "content": "User asked what the weather was yesterday morning in Seattle.", "is_pinned": False, "timestamp": now - 150000, "access_count": 1},
            {"id": "m3", "content": "User preferred weekly summary delivered via WeChat Work.", "is_pinned": False, "timestamp": now - 3600, "access_count": 15}
        ]
        res = attributor.prune_contextual_memories(memories, target_token_budget=30)
        assert res["retained_memory_count"] >= 1
        # Pinned memory m1 must always be retained
        retained_ids = [m["id"] for m in res["retained_memories"]]
        assert "m1" in retained_ids
        print("Self-test PASSED!")
        sys.exit(0)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            msg_id = req.get("id")
            method = req.get("method")
            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "ContextualMemoryPruningImportanceAttributor", "version": "1.0.0"},
                        "capabilities": {"tools": {}}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [{
                            "name": "prune_agentic_memory",
                            "description": "Calculate episodic memory importance attribution scores, identify redundant or decayed context nodes, and prune memory buffers to target token constraints.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "enum": ["attribute_memory_importance", "prune_contextual_memories"]},
                                    "memories": {"type": "array"},
                                    "target_token_budget": {"type": "integer"}
                                },
                                "required": ["action"]
                            }
                        }]
                    }
                }
            elif method == "tools/call":
                res = handle_call_tool(req.get("params", {}))
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            print(json.dumps(resp), flush=True)
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
    main()
