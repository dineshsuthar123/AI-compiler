import json, sys
import requests
code = '#include <stdio.h>\nint main(){ printf("Hello site!\\n"); return 0; }\n'
resp = requests.post('http://127.0.0.1:5000/api/compile', json={'code': code, 'optimization_level': 0, 'ai_enhanced': False}, timeout=10)
print(resp.status_code)
print(json.dumps(resp.json(), indent=2))
