# Setup diagnostics

`uasef doctor --project .` inspects resources, PATH, basic inception state,
memory readability and effective Git hooks (including core.hooksPath).
It does not execute hooks or change project state. Hook detection is static:
finding a Lefthook launcher does not prove its configuration works.

```powershell
uasef doctor --project . --json
uasef doctor --auth
uasef doctor --live --model provider/model --timeout 60
```

Authentication and live probes currently support OpenCode only. Other agent
executables are discovered, but their authentication is not assessed.
`--auth` invokes `opencode auth list --format json`; configuration presence is
not proof of valid credentials. Unsupported output is reported as unverified.
`--live` requires an explicit model and sends a minimal acknowledgement prompt.
It may incur provider charges. A successful response verifies access for that
request, not code quality or every provider. Raw agent output and credentials
are never included in reports.

Probes use a temporary directory without project attachments, deny tool
permissions and disable default plugins/project configuration via OpenCode
environment flags. Installed CLI versions must support these controls. Global
configuration still applies; this is not OS sandboxing. OpenCode can write its
own logs/cache/session data. Timeout kills the direct process; inspect for child
processes before retrying. No login, installation or configuration repair is automatic.

Exit codes: 0 means no detected errors (warnings/skipped checks may remain),
1 means diagnostic errors, 2 means invalid CLI arguments. JSON schema version 1
contains `checks` (name/status/detail/fix) and `healthy`; healthy does not mean all
optional checks ran. Reports can include local paths; review before sharing.

Local validation encountered OpenCode startup permission denial writing its log.
This is reported as a command failure, not mistaken for invalid credentials.
Provider-backed success must be tested in an environment with authorized working
credentials; mocked adapter tests do not prove live provider compatibility.
