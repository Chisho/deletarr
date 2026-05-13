---
name: dev_backseat
description: Revert this conversation to backseat (the default) — main session and subagents use Edit/Write to make changes directly.
---

You are executing `/dev_backseat` — flips the current conversation's driver-mode to **backseat** (the default).

## What this does

For the rest of this conversation:

- You (the main Claude Code session) and any subagents you launch operate normally — using `Edit`, `Write`, etc. to make changes directly. The user reviews after.
- Backseat is the default — `/dev_backseat` is mainly useful to revert after a previous `/dev_mainseat` invocation in the same conversation.

This mode is conversation-scoped. New conversations always start in **backseat** by default; you don't need to invoke this at the start of fresh sessions.

## Steps

1. Acknowledge the switch (e.g. *"Driver-mode is now backseat for this conversation — I'll edit files directly. Run `/dev_mainseat` to switch back."*).
2. Apply the mode for the rest of this conversation per the rules above.

## Notes

- Pure mode switch. Do not perform unrelated actions.
