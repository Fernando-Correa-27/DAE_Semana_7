import django
import os
import sys
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Intentión 1: posts_per_author
with open("blog/management/commands/agent.py", "r") as f:
    content = f.read()
    # Simulate the command execution
    from blog.agent.registry import execute
    result = execute({"action": "posts_per_author", "args": {}})
    print("Intent 1 (posts_per_author):")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()

# Intentión 2: comments_of_post
result = execute({"action": "comments_of_post", "args": {"post_id": 1}})
print("Intent 2 (comments_of_post, post_id=1):")
print(json.dumps(result, ensure_ascii=False, indent=2))
print()

# Intentión 3: delete_comments_of_post
result = execute({"action": "delete_comments_of_post", "args": {"post_id": 1}})
print("Intent 3 (delete_comments_of_post, post_id=1):")
print(json.dumps(result, ensure_ascii=False, indent=2))
print()

# Intentión 4: run_sql (unknown action)
result = execute({"action": "run_sql", "args": {}})
print("Intent 4 (run_sql - unknown action):")
print(json.dumps(result, ensure_ascii=False, indent=2))
