# Target Application Authentication Adapter

AQABSI authenticates a target application (development, staging, or local test environment) through one of the modes below. Every mode keeps credentials out of PRDs, manifests, reports, dashboards, and committed files. Passwords and tokens are transmitted only to the configured target and are redacted from all outputs.

## Modes

| Mode | Use when | Credentials | Automation |
|---|---|---|---|
| `web_login` | The target has a form/API login endpoint | username + password | `scripts/auth_login.py --mode web_login` |
| `bearer_token` | The target accepts an API or session bearer token | token | set `AQABSI_TEST_TOKEN` |
| `basic_auth` | The target uses HTTP Basic authentication | username + password | `scripts/auth_login.py --mode basic_auth` |
| `sso_browser` | The target redirects through SAML/OIDC with interactive/browser steps | browser session | manual browser automation |
| `sso_manual_handoff` | Interactive SSO or MFA cannot be scripted safely | manual session | operator sign-in, then hand over |

The default mode is `web_login`. Configure the mode with `AQABSI_TARGET_AUTH_MODE`; the supported values are `web_login`, `bearer_token`, `basic_auth`, `sso_manual_handoff`, and `none`.

## Environment variables

- `AQABSI_TARGET_BASE_URL` — base URL of the target application (HTTPS, or HTTP only for loopback).
- `AQABSI_TARGET_AUTH_MODE` — authentication mode (default `web_login`).
- `AQABSI_TEST_USERNAME` — dedicated test account username.
- `AQABSI_TEST_PASSWORD` — test account password; never echoed or written to files.
- `AQABSI_TEST_TOKEN` — API/bearer token for `bearer_token` mode.
- `AQABSI_TARGET_LOGIN_PATH` — custom login route (default `/login`).

Supplying values into the gitignored `.env` (via `scripts/configure_env.py`), a secret manager, or terminal environment injection is preferred. Never commit a password or token, and never write it to a report, manifest, memory, or cookie description.

## Login helper

`scripts/auth_login.py` performs a bounded login for `web_login` and `basic_auth` and persists the resulting session cookies to a cookie jar file without printing credentials:

```bash
# form/API login
python3 scripts/auth_login.py --mode web_login \
  --base-url "$AQABSI_TARGET_BASE_URL" \
  --cookie-jar .aqabsi-output/session-cookies.txt

# HTTP Basic authentication
python3 scripts/auth_login.py --mode basic_auth \
  --base-url "$AQABSI_TARGET_BASE_URL" \
  --cookie-jar .aqabsi-output/session-cookies.txt
```

The command exits `0` on a successful login, `2` on unreachable/unauthorized/error, and prints a JSON summary containing only non-secret fields (`status`, `mode`, `base_url`, `status_code`, `cookie_file`, `message`). It blocks cross-origin redirects so credentials are never forwarded to a different host. The cookie jar is the input for a subsequent browser or cookie-authenticated run; keep it outside source control.

## SSO and self-signed certificate flow

Many BSI-internal deployments sit behind an identity provider (IdP) with a self-signed or internal-CA certificate. A common real-world symptom is the service provider (SP) presenting a certificate the IdP does not trust, or the browser showing a certificate-mismatch warning. Never disable certificate validation. Instead, record the warning and continue through the browser's explicit trust step only when it is an approved internal endpoint:

1. Open the target URL in the automated/manual browser profile.
2. If the browser shows a certificate warning, expand the error details and confirm the certificate subject matches the expected internal host.
3. Click **Advanced**, then **Proceed to <host> (unsafe)** (Chromium) or the equivalent **Accept the Risk and Continue** (Firefox).
4. Complete the IdP sign-in with the dedicated test account, including any MFA or consent prompt.
5. On redirect back to the SP, confirm the session is established and capture only sanitized evidence (URL, visible state, response correlation ID) — never cookies, tokens, or IdP secrets.
6. For non-interactive execution, classify the case as `blocked` or `sso_manual_handoff` rather than pretending the browser step executed.

Document the certificate host, the approved trust action, and the account used in the run's authorization record. If the internal CA bundle is available, configure the runner to trust that bundle instead of clicking through a warning.

## Safety invariants

- Never store a password, token, session cookie, or IdP secret in a report, manifest, memory, or committed file.
- Never disable TLS verification (`-k`, `NODE_TLS_REJECT_UNAUTHORIZED=0`, or equivalent).
- Never forward credentials cross-origin; block cross-origin redirects.
- Treat production-like hosts as forbidden unless an explicit, scoped test authorization exists.
- Keep SSO/browser evidence sanitized and reproducible; label interactive steps that were not actually executed.
