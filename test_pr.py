import json
with open('tests/test_surveyor.py') as f:
    pass

with open('/private/var/folders/r5/kr3sf1x962s2v1lm_v7y901w0000gn/T/pytest-of-aman/pytest-11/test_surveyor_negative_dead_co0/repo/module_graph.json') as f:
    data = json.load(f)
for n in data['nodes']:
    print(n['identity'], "PR:", n['pagerank_score'], "in:", n.get('in_degree', '?'), "sink:", n['is_sink_node'], "dead:", n['is_dead_code_candidate'])
