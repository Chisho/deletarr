---
name: dev_mainseat
description: Flip this conversation to mainseat — main session and any code-modifying subagents provide ready-to-paste snippets instead of editing files. Conversation-scoped; new conversations always start in backseat.
---

You are executing `/dev_mainseat` — flips the current conversation's driver-mode to **mainseat**.

## What this does

For the rest of this conversation:

- You (the main Claude Code session) must NOT call `Edit`, `Write`, or `NotebookEdit` to change project files. Walk the user through changes in plain language and provide ready-to-paste snippets the user applies themselves.
- When you launch a code-modifying subagent (e.g. frontend-developer, backend-developer, embedded-developer), include the directive *"Operate in mainseat mode — provide ready-to-paste snippets, do not call Edit/Write."* in the subagent's task description so it inherits the mode.
- Read-only subagents (architect, code-reviewer, security-expert) don't need the directive — they can't edit anyway.

This mode is conversation-scoped — it does not persist. New conversations always start in **backseat** (the default — agent edits directly). Re-invoke `/dev_mainseat` at the start of any conversation where you want this mode.

## Steps

1. Acknowledge the switch (e.g. *"Driver-mode is now mainseat for this conversation — I'll provide snippets instead of editing files. Run `/dev_backseat` to revert."*).
2. Apply the mode for the rest of this conversation per the rules above.

## Notes

- Pure mode switch. Do not perform unrelated actions.
- If the user asks you to apply edits directly while in mainseat, explain the mode and suggest `/dev_backseat` first.
