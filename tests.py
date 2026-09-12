import requests
import time
import sys

BASE_URL = "http://localhost:8001/api/v1"

def print_result(name, passed, extra=""):
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    status = "PASS" if passed else "FAIL"
    print(f"{color}[{status}] {name}{reset} {extra}")

print("Starting SpiderNet API Tests...\n")

tests_run = 0
tests_passed = 0

try:
    # 1. Health check
    res = requests.get("http://localhost:8001/")
    passed = res.status_code == 200 and "status" in res.json()
    print_result("Test 1: Server Health Check", passed)
    tests_run += 1
    tests_passed += 1 if passed else 0

    # 2-6. Search Queries
    test_queries = [
        ("9313090380", 1),
        ("9313090380", 2),
        ("9313090380", 3),
        ("9313090380", 1),
        ("9313090380", 2)
    ]
    
    nodes_found = []
    edges_found = []

    for i, (q, d) in enumerate(test_queries, start=2):
        res = requests.get(f"{BASE_URL}/graph/search?query={q}&depth={d}")
        if res.status_code == 200:
            data = res.json()
            nodes = data['meta']['total_nodes']
            edges = data['meta']['total_edges']
            passed = nodes > 0
            if passed and q == "9313090380" and d == 1:
                nodes_found = data['elements']['nodes']
                edges_found = data['elements']['edges']
            print_result(f"Test {i}: Search '{q}' (Depth {d})", passed, f"- Found {nodes} nodes, {edges} edges")
        else:
            print_result(f"Test {i}: Search '{q}' (Depth {d})", False, f"- Error {res.status_code}")
            passed = False
        tests_run += 1
        tests_passed += 1 if passed else 0

    # 7-11. Analytics (Chokepoints)
    # We will send the nodes and edges from Test 2 to the chokepoint API
    if nodes_found:
        payload = {"nodes": nodes_found, "edges": edges_found}
        for i in range(7, 12):
            res = requests.post(f"{BASE_URL}/graph/analyze/chokepoints", json=payload)
            passed = res.status_code == 200
            
            # Check if risk_level is updated in response
            if passed:
                resp_nodes = res.json().get('elements', {}).get('nodes', [])
                critical_count = sum(1 for n in resp_nodes if n.get('data', {}).get('risk_level') == 'CRITICAL')
                print_result(f"Test {i}: Analyze Chokepoints (Run {i-6})", passed, f"- Flagged {critical_count} critical nodes")
            else:
                print_result(f"Test {i}: Analyze Chokepoints (Run {i-6})", False, f"- Error {res.status_code}")
            
            tests_run += 1
            tests_passed += 1 if passed else 0
    else:
        print("Skipping analytics tests because search failed to return nodes.")

    # 12-15. Expansion
    if nodes_found:
        target_node = nodes_found[0]['data']['id']
        visible_ids = [n['data']['id'] for n in nodes_found]
        for i in range(12, 16):
            payload = {"node_id": target_node, "current_visible_ids": visible_ids, "limit": 10}
            res = requests.post(f"{BASE_URL}/graph/expand", json=payload)
            passed = res.status_code == 200
            if passed:
                added_nodes = res.json().get('meta', {}).get('total_nodes', 0)
                print_result(f"Test {i}: Expand Node '{target_node}' (Run {i-11})", passed, f"- Added {added_nodes} new nodes")
            else:
                print_result(f"Test {i}: Expand Node '{target_node}'", False, f"- Error {res.status_code}: {res.text}")
            tests_run += 1
            tests_passed += 1 if passed else 0

except Exception as e:
    print(f"\nTest execution failed: {e}")

print(f"\n==============================")
print(f"Tests Run: {tests_run}")
print(f"Tests Passed: {tests_passed}")
print(f"==============================")
if tests_run == tests_passed and tests_run >= 15:
    sys.exit(0)
else:
    sys.exit(1)
