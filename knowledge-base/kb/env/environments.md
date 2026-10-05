---
last_verified: never
---
# Environments

Where things run, how to reach them, what a session may do there. No secrets: name the secret's location (a vault, an env var name), never its value.

| Environment | Purpose | How to log in / connect | May read | May change | Notes |
|---|---|---|---|---|---|
| dev | … | `<command>` | yes | yes | … |
| test | … | … | yes | only via pipeline | … |
| prod | … | … | read-only with approval | never from an agent session | … |

## Accounts and roles

- `<account or role>` — what it can do; who grants it.

## Cloud scope (if any)

- Tenant / subscription / resource group naming; which subscription is the default; where the inventory command lives (see the `azure-cli` skill for the Azure CLI rules).
