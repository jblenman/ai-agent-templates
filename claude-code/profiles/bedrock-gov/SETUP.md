# Claude Code — Amazon Bedrock / Restricted-Government Setup

Setup guide for Claude Code in an isolated government development environment: Claude is reached only through **Amazon Bedrock** inside the enterprise boundary, internet access is limited or absent, and nothing internal may leave the boundary. Model ceiling: **Claude Opus 5**.

Verified against the Claude Code docs on 2026-08-28 (`code.claude.com/docs/en/amazon-bedrock`, `permission-modes`, `network-config`, `data-usage`, `settings-reference`). Re-check anything version-sensitive before a rollout.

## What this profile changes

| Aspect | Default template | This profile |
|--------|------------------|--------------|
| Provider | Anthropic API / subscription login | Amazon Bedrock (`CLAUDE_CODE_USE_BEDROCK=1`), AWS credentials |
| Model | Whatever the account defaults to | `opus` alias pinned to `us.anthropic.claude-opus-5[1m]` (1M context) |
| Web tools | `WebSearch`, `WebFetch` allowed | Both **denied**. WebSearch doesn't exist on Bedrock; WebFetch fetches from the client but first sends each hostname to `api.anthropic.com` for a safety check |
| Permissions | auto mode, read tools pre-approved | auto mode, only `Read`/`Glob`/`Grep` pre-approved; everything else is classifier-reviewed |
| Network | Defaults | Telemetry, error reports, feature-flag fetches, `/feedback` `/bug` `/share`, auto-update all off |
| Remote Control / cloud sessions / artifacts | Available with a claude.ai login | Not available on Bedrock; `remoteControlAtStartup: false` made explicit |
| Commit attribution | Co-authored-by trailer + session URL | Trailer kept (audit trail), session URL off (points at claude.ai) |
| CLAUDE.md | Base | Base + "Environment — read first" section (data boundary, offline behavior, hand transfer) |

## Prerequisites

- **Claude Code** brought in through the organization's software intake process (the native installer and npm both download from the internet; Anthropic documents no offline installer). Pin one version; `DISABLE_AUTOUPDATER` keeps it there. An internal npm mirror works too: `npm install -g @anthropic-ai/claude-code@<version>`.
- **AWS credentials** that can invoke Bedrock in the environment's region, via any standard mechanism: `aws configure`, an SSO profile (`AWS_PROFILE`), access keys in the environment, or a Bedrock API key (`AWS_BEARER_TOKEN_BEDROCK`).
- **Model access** enabled in the Bedrock console (Model catalog → Anthropic → use-case form; instant). Enable **Claude Opus 5** and **Claude Sonnet 5** — Sonnet 5 runs the auto-mode permission classifier. If Sonnet 5 isn't available, sessions start in Manual mode (more prompts, otherwise fine).
- **IAM** — the policy from the Bedrock doc, minimum actions: `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`, `bedrock:ListInferenceProfiles`, `bedrock:GetInferenceProfile` on `inference-profile/*`, `application-inference-profile/*`, `foundation-model/*`. Check what the account can actually run: `aws bedrock list-inference-profiles --region <region>`.

## 1. Install the config files

Copy from a clone of this repo, or transfer by hand (each file is self-contained):

```powershell
$src = "$HOME\ai-agent-templates\claude-code\profiles\bedrock-gov"
New-Item -ItemType Directory -Path "$HOME\.claude" -Force
Copy-Item "$src\CLAUDE.md"     "$HOME\.claude\CLAUDE.md"
Copy-Item "$src\settings.json" "$HOME\.claude\settings.json"
```

`settings.json` must be the **user** file (`~/.claude/settings.json`): `defaultMode: "auto"` is ignored in project-level settings.

## 2. Set the region and model prefix

Edit `~/.claude/settings.json` → `env`:

- `AWS_REGION` — the environment's Bedrock region. Only needed if it differs from the active AWS profile's region.
- `ANTHROPIC_DEFAULT_OPUS_MODEL` — cross-region inference profile ID for Opus 5. The prefix follows the region: `us.` for `us-*`, **`us-gov.` for AWS GovCloud** (`us-gov.anthropic.claude-opus-5[1m]`), `eu.` / `apac.` / `global.` elsewhere. An application inference profile ARN works here too (use `modelOverrides` for several). Keep the `[1m]` suffix for the 1M-token context window; drop it if the environment prefers the 200K window.

Optional env additions:

```json
"ANTHROPIC_DEFAULT_HAIKU_MODEL": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
"HTTPS_PROXY": "http://proxy.internal:8080",
"NO_PROXY": "localhost,127.0.0.1",
"NODE_EXTRA_CA_CERTS": "C:\\path\\to\\corporate-ca.pem",
"ANTHROPIC_BEDROCK_BASE_URL": "https://your-gateway.internal"
```

- Haiku pin: background tasks (session titles, etc.) run on the primary model unless a Haiku model is pinned and enabled in the account. Cheaper, not required.
- Proxy / CA: Bedrock traffic honors `HTTPS_PROXY`/`NO_PROXY`; TLS-inspecting proxies need the corporate CA in `NODE_EXTRA_CA_CERTS`. No SOCKS support.
- Gateway: if model traffic goes through a central LLM gateway that signs requests itself, also set `CLAUDE_CODE_SKIP_BEDROCK_AUTH=1`.
- SSO refresh: `"awsAuthRefresh": "aws sso login --profile <name>"` as a top-level setting re-authenticates when credentials expire. Remove it if the proxy breaks the browser flow (it loops); run `aws sso login` by hand instead.

Alternatively run `/setup-bedrock` inside Claude Code: it detects the AWS profile and region, checks which models the account can invoke, pins them (with a 1M-context option) into the same `env` block, and leaves the rest of the file alone. Confirm the permission/deny keys survived.

## 3. Verify

```text
claude --version        # the pinned version
claude
/status                 # provider "Amazon Bedrock", resolved region, model = Opus 5
/permissions            # deny: WebFetch, WebSearch; mode: auto
/context                # cache-read tokens > 0 after a couple of turns = prompt caching works in this region
```

Then ask Claude to fetch any URL — it must report the tool is denied, not try a workaround. Ask it to summarize a file — it should work without a prompt (Read is pre-approved). Ask it to create a file — auto mode should allow it silently; if it prompts, auto mode fell back to Manual (see Troubleshooting).

## Outbound network

| Destination | Status | Why |
|-------------|--------|-----|
| `bedrock-runtime.<region>.amazonaws.com` (or the gateway) | **Required** | The model |
| STS `GetCallerIdentity` | Only if `awsAuthRefresh` is set | Expiry check before re-login; goes through the proxy |
| `api.anthropic.com` | Blocked by config | Feature flags (`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`) and the WebFetch hostname check (`skipWebFetchPreflight` + WebFetch denied) |
| Datadog intake (`*.datadoghq.com`) | Off | Telemetry and error reports — off by default on Bedrock, and forced off here |
| `claude.ai`, `platform.claude.com` | Unused | Only for subscription sign-in; Remote Control, cloud sessions, and artifact publishing need that sign-in and don't exist on Bedrock |
| npm / GitHub | Blocked by config | Auto-update (`DISABLE_AUTOUPDATER`) |
| Plugin marketplace | Not disabled by any flag | Policy: don't install plugins or MCP servers that reach outside the boundary. Managed settings can lock this (`allowManagedMcpServersOnly`) |

Conversation content goes only to Bedrock; nothing is sent to Anthropic. `/feedback` and `/bug` are disabled; on Bedrock they would only write a local bundle under `~/.claude/feedback-bundles/` anyway.

## Locking it down for a team

Put the `permissions` block in the managed settings file so users can't loosen it: Windows `C:\Program Files\ClaudeCode\managed-settings.json` (or `HKLM\SOFTWARE\Policies\ClaudeCode`, value `Settings`), macOS `/Library/Application Support/ClaudeCode/managed-settings.json`, Linux `/etc/claude-code/managed-settings.json`. Managed settings outrank user settings. Useful managed-only keys: `disableRemoteControl`, `allowManagedMcpServersOnly`, `permissions.disableAutoMode`.

## Opus 5 notes

- **Effort.** `effortLevel: "xhigh"` is Claude Code's default for coding and is pinned here so a future default change can't silently lower it. Opus 5 is unusually strong at `low`/`medium`; `/effort medium` for routine edits cuts Bedrock spend and latency. Effort is the lever for thinking depth, not response length.
- **Thinking is on by default** (adaptive). Nothing to configure.
- **1M context** comes from the `[1m]` variant; auto-compaction still runs as the window fills. Keep `session-context.md` current so a `/clear` or a new session costs little.
- **Prompt caching** is on by default and billed at Bedrock rates; not every Bedrock region supports it — `/context` shows zero cache-read tokens where it doesn't. `DISABLE_PROMPT_CACHING=1` turns it off; `ENABLE_PROMPT_CACHING_1H=1` buys the longer TTL at a higher rate.
- **Fast mode** and the **advisor** tool are Anthropic-API-only; not available on Bedrock.
- **Pin models before a multi-user rollout.** Unpinned aliases follow Claude Code's built-in Bedrock default, which can move to a model the account hasn't enabled yet; Claude Code then falls back to an older model with a notice.

## Troubleshooting

- **Session starts in Manual, no error** — `defaultMode: "auto"` is in a project settings file, or auto mode is unavailable. Run `/status`; auto mode needs Sonnet 5 / Opus 4.7+ / Fable 5 on Bedrock and an org policy that hasn't disabled it.
- **"auto mode cannot determine the safety of an action"** naming a model — the classifier model (Sonnet 5) isn't invokable in this account/region. Enable it, or accept Manual/`acceptEdits`.
- **`on-demand throughput isn't supported`** — use an inference profile ID (`us.anthropic…`), not a bare foundation-model ID.
- **400 naming the model in GovCloud** — the prefix must be `us-gov.`; Claude Code forces it for `us-gov-*` regions, so check the pinned ID.
- **`Bedrock streaming response has content-type …`** — a gateway is rewriting the event stream; it must pass `InvokeModelWithResponseStream` bodies and `Content-Type` through unmodified.
- **Startup hangs behind a proxy** — the STS expiry check or SSO refresh can't reach out; set `HTTPS_PROXY`/`NO_PROXY` or remove `awsAuthRefresh`.
- **`/logout` missing** — expected on Bedrock; credentials are AWS-managed.
