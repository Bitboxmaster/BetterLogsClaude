#!/usr/bin/env python3
"""Claude Code JSONL to Markdown converter."""

import json, sys, os, re
from datetime import datetime

# ─── Config ───
CONF = os.path.expanduser('~/.claude/logs.conf')
def read_conf(key):
    """Read a value from logs.conf"""
    if not os.path.exists(CONF):
        return None
    with open(CONF) as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            if k.strip() == key:
                return os.path.expanduser(v.strip())
    return None

if len(sys.argv) < 2:
    print("Usage: python convert.py <file.jsonl> [output_dir]")
    sys.exit(1)

file = sys.argv[1]
out_dir = sys.argv[2] if len(sys.argv) > 2 else read_conf('LOGS_DIR') or os.path.dirname(file)

messages = []
first_user_msg = ''
first_ts = ''

with open(file) as f:
    for line in f:
        msg = json.loads(line)
        if msg.get('type') not in ('user', 'assistant'):
            continue

        inner = msg.get('message', {})
        role = inner.get('role', '')
        content = inner.get('content', '')

        if isinstance(content, list):
            # Extract only text blocks, skip thinking/tool_use etc
            texts = [c.get('text', '') for c in content
                     if isinstance(c, dict) and c.get('type') == 'text']
            content = '\n'.join(texts)

        content = content.strip()
        if not content:
            continue

        # Skip system messages (slash commands, local command output)
        if '<local-command' in content or '<command-name>' in content or '<local-command-stdout>' in content:
            continue

        ts = msg.get('timestamp', '')
        time_str = ''
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                time_str = f' ({dt.strftime("%H:%M:%S")})'
                if not first_ts and role == 'user':
                    first_ts = dt.strftime('%Y-%m-%d')
            except Exception:
                pass

        if not first_user_msg and role == 'user':
            first_user_msg = content

        messages.append((role, content, time_str))

if not messages:
    print(f'⚠️  No messages in {file}')
    sys.exit(0)

# Generate filename from date + first user question
date_str = first_ts or datetime.now().strftime('%Y-%m-%d')
title = first_user_msg[:60].strip()

# Remove characters not allowed in filenames
title = re.sub(r'[\\/:*?"<>|\n\r]', '', title)
title = title.strip('. ')

if not title:
    title = 'untitled'

filename = f'{date_str} {title}.md'
out_path = os.path.join(out_dir, filename)

# If file exists — overwrite (same session, new messages)
if os.path.exists(out_path):
    action = '🔄 updated'
else:
    action = '✅ created'

with open(out_path, 'w') as o:
    o.write(f'# {title}\n')
    o.write(f'**Date:** {date_str}\n\n---\n\n')
    for role, content, time_str in messages:
        prefix = '## 👤 You' if role == 'user' else '## 🤖 Claude'
        o.write(f'{prefix}{time_str}\n\n{content}\n\n---\n\n')

print(f'{action} {out_path} — {len(messages)} messages')
