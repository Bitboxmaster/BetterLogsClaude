# BetterLogsClaude

Auto-save Claude Code sessions as readable Markdown files with Obsidian + iCloud sync.

## What it does

After every Claude Code response, a `Stop` hook converts the current session from JSONL to Markdown and saves it to your Obsidian vault. Files are named by date + first question: `2026-03-22 Optimistic locking.md`.

## Files

| File | Purpose |
|------|---------|
| `settings.json` | Claude Code config with `Stop` hook |
| `convert.py` | JSONL → Markdown converter |
| `logs.conf` | All paths in one place — edit only here |

## Setup

### 1. Copy files to `~/.claude/`

```bash
cp settings.json ~/.claude/
cp convert.py ~/.claude/
cp logs.conf ~/.claude/
```

### 2. Configure paths

Edit `~/.claude/logs.conf` and set your paths:

```bash
# JSONL sessions directory (usually no need to change)
JSONL_DIR="$HOME/.claude/projects"

# Markdown logs output — CHANGE THIS TO YOUR FOLDER
LOGS_DIR=$HOME'/Library/Mobile Documents/iCloud~md~obsidian/Documents/Logs/claude-logs'

# Converter script path (usually no need to change)
CONVERT_SCRIPT="$HOME/.claude/convert.py"

# Delay before conversion (seconds)
SLEEP_SEC=3
```

> **Important:** if path contains spaces, use format `$HOME'/path with spaces/folder'`

### 3. Create logs directory

```bash
mkdir -p ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/Logs/claude-logs
```

### 4. Verify

Run manually:

```bash
. ~/.claude/logs.conf && LATEST=$(find "$JSONL_DIR" -name '*.jsonl' -type f -exec stat -f '%m %N' {} + 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-) && [ -f "$LATEST" ] && python3 "$CONVERT_SCRIPT" "$LATEST" "$LOGS_DIR"
```

Expected output: `✅ /path/to/file.md — N messages`.

## How it works

1. Claude Code finishes a response → `Stop` hook fires
2. `sleep 3` — wait for JSONL to be fully written to disk
3. `find` locates the most recently modified JSONL session file
4. `convert.py` parses JSONL, extracts messages, filters out system commands (`/model`, `/color`, etc.)
5. Filename is generated from date + first user question
6. If file with that name already exists — it gets overwritten (session update)
7. Markdown syncs to Obsidian via iCloud

## Batch convert old sessions

To convert all existing JSONL files at once:

```bash
shopt -s globstar
. ~/.claude/logs.conf
for f in "$JSONL_DIR"/**/*.jsonl; do
  python3 "$CONVERT_SCRIPT" "$f" "$LOGS_DIR"
done
```

## Output format

```markdown
# Optimistic locking
**Date:** 2026-03-22

---

## 👤 You (10:28:04)

Tell me about optimistic locking

---

## 🤖 Claude (10:28:12)

Optimistic locking is...

---
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Empty files (no Claude response) | Increase `SLEEP_SEC` in `logs.conf` |
| Hook not firing | Check `cat ~/.claude/settings.json` — hook must be under `Stop` |
| Path errors | Check `logs.conf` — spaces in paths require `$HOME'/path'` format |
| System commands in logs | Update `convert.py` — filter checks for `<local-command` |
| Duplicate files | Script overwrites files with the same name |

## Requirements

- macOS (uses `stat -f` for finding recent files)
- Python 3
- Claude Code CLI
- Obsidian + iCloud (optional — any folder works)
