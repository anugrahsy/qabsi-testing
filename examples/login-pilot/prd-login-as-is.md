# PRD — Gateway EA Login, SSO, 2FA, and Password Recovery

## 1. Document control

| Field | Value |
|---|---|
| Document type | As-is technical reconstruction; not yet an approved business PRD |
| Version / status | 0.1 / Draft — stakeholder and auth-platform validation required |
| Evidence cutoff | 2026-11-12 Asia/Jakarta |
| Frontend source | `lib-uii-gateway-ea-angular` commit `347be7947277be6005f5a721e7ec1109e29a9a1e`, branch `develop-ranp` |
| Backend source | `svc-ea-lumen` commit `d35378df083a77c149e663dc4c99a8192d61b5f7`, branch `develop` |
| Runtime evidence | None; no target URL, account, or login authorization was provided |
| Evidence classification | Source-verified facts, explicit inference, open questions, and recommendations are separated |

Both worktrees contained unrelated local changes. The analyzed login files were not listed as modified. No environment secret or credential file was read.

## 2. Executive summary

The frontend presents account authentication through direct username/password login, organizational SSO, parent SSO, optional authenticator-based 2FA, and a WhatsApp OTP password-recovery flow. Authentication execution is delegated primarily to `AuthenticationService` from external package `@uiigateway/core` version `4.1.3`; recovery calls use a separate API base URL. The supplied EA Lumen service does not expose the referenced login routes, so server-side authentication requirements cannot be verified from these two repositories alone.

This PRD documents observable source behavior and the evidence gaps that must be resolved before it can become an approved product contract.

## 3. Context and problem statement

Users need to enter the Gateway application through an authentication method appropriate to their environment and account type. The UI must prevent incomplete submissions, communicate failures, complete a second factor when enabled, and provide a recoverable forgotten-password path.

The current implementation spans the application repository, the external `@uiigateway/core` package, SSO providers, and login APIs outside `svc-ea-lumen`. No existing login PRD, API contract, unit spec, runtime target, or authorized test identity was found in the supplied scope.

## 4. Goals and success measures

### Verified goals reconstructed from source

- Expose canonical routes for login and SSO callback.
- Support direct credentials outside production and an environment-driven SSO path.
- Route authenticated users to `AuthenticationService.redirectUrl`.
- Require a second factor when the authentication service indicates 2FA.
- Allow password recovery through account verification, OTP verification, and password reset.
- Prevent repeated submission while an asynchronous action is loading.

### Success measures requiring product confirmation

- Authentication success/failure rate and latency targets.
- SSO callback success rate.
- OTP delivery and verification time targets.
- Accessibility conformance target.
- Rate-limit, lockout, session, audit, privacy, and recovery SLOs.

## 5. Scope, non-goals, dependencies, and constraints

### In scope

- Routes `/login`, `/account/login`, `/loginsso`, and `/account/loginsso`.
- Direct username/password form and its UI states.
- SSO links and callback processing visible in this frontend.
- Authenticator-code form displayed after primary authentication.
- Forgotten-password account, OTP, and password forms.
- Frontend-visible validation, loading, errors, navigation, and state reset.

### Out of scope

- Server-side credential verification, token issuance, session storage, SSO assertion validation, OTP generation/delivery, password hashing, authorization, and audit implementation.
- Production execution, security exploitation, performance/load tests, real WhatsApp delivery, and real password changes.
- Authentication APIs not present in `svc-ea-lumen`.

### Dependencies

- `@uiigateway/core` `4.1.3`, particularly `AuthenticationService`.
- Environment-provided SSO, parent-SSO, and API base URLs.
- External SSO identity providers.
- External `/v1/login/*` recovery API.
- WhatsApp OTP delivery provider.

## 6. Stakeholders and actors

| Actor | Need | Verified authorization boundary |
|---|---|---|
| Gateway member | Direct or SSO authentication and account recovery | Not available in supplied source |
| Parent user | Parent SSO entry | Link exists; downstream role behavior is unverified |
| 2FA-enabled member | Complete authenticator verification | UI path exists; server rules are external |
| QA engineer | Execute test identities without affecting real accounts | Test identities and environment not yet provided |
| Frontend team | Own application UI behavior | Ownership platform IDs not provided |
| Auth-platform team | Own core auth package/services | Team/person mapping not provided |

## 7. User journeys and states

### Direct login

`login form` → validate required username/password → set loading → `AuthenticationService.login` → either display error, navigate to redirect URL, or enter `2FA pending`.

### Query-token SSO

`/account/login?access_token=…&ttl=…` → `AuthenticationService.loginSSO` → navigate on success or show error. When the query token is absent, the component invokes logout.

### SSO callback route

`/account/loginsso/<member>/<session>` → extract two path segments → `AuthenticationService.loginSSO` → navigate to redirect URL or a derived login path.

### 2FA

`primary auth successful` → `enable2fa=true` → require authenticator code → `verify2FA` → navigate on success or display an error.

### Forgotten password

`forgot password` → submit SSO account → request WhatsApp OTP → submit OTP → receive reset token in component state → submit new password and confirmation → show success/error → return to login.

## 8. Functional requirements

| ID | Requirement reconstructed from source | Evidence | Confidence | Acceptance criteria |
|---|---|---|---|---|
| FR-AUTH-001 | `/login` shall redirect to `/account/login`; `/loginsso` shall redirect to `/account/loginsso`. | `src/app/app.routing.ts:10-15`; login route modules | High | Each alias resolves once to the expected component route without a redirect loop. |
| FR-AUTH-002 | The direct login form shall require non-empty username and password and disable submit while invalid or loading. | `login.component.ts:55-58`; `login.component.html:24-40` | High | Empty fields cannot submit; visible field errors and disabled state match form state. |
| FR-AUTH-003 | A direct login submission shall delegate credentials to `AuthenticationService.login` and navigate to its redirect URL when successful without 2FA. | `login.component.ts:145-171` | High | Exactly one auth request is initiated and navigation occurs only after successful callback. |
| FR-AUTH-004 | A failed direct login shall stop loading and display the service error or translated generic fallback. | `login.component.ts:160-168`; `login.component.html:44` | High | Loading clears and an error is perceivable without exposing secrets. Exact generic-message policy remains open. |
| FR-AUTH-005 | Production shall hide the direct-login controls by default while non-production shall show them. | `login.component.ts:66-75` | High | Environment-specific visibility matches the approved policy. The `developer` query override requires explicit confirmation. |
| FR-SSO-001 | The login form shall present environment-configured organizational and parent SSO links. | `login.component.ts:63-64`; `login.component.html:45-46` | High | Each link uses the correct authorized destination for the active environment. |
| FR-SSO-002 | When an SSO access token is supplied on the login route, the component shall delegate it and its TTL to `AuthenticationService.loginSSO`. | `login.component.ts:78-99` | High | Valid and invalid callbacks produce the approved navigation/error state; token-handling security remains external. |
| FR-SSO-003 | When no query access token is present, opening the login component shall invoke logout. | `login.component.ts:100-102` | High | Existing authenticated state is handled according to the approved session policy. |
| FR-MFA-001 | When the auth service indicates 2FA, the primary login shall not navigate directly and the authenticator-code form shall appear. | `login.component.ts:154-159`; `login.component.html:49-61` | High | Full application navigation is unavailable until second-factor success. Server enforcement is unverified. |
| FR-MFA-002 | The authenticator form shall require a code and delegate `code`, `fa_code`, and user UUID to `verify2FA`. | `login.component.ts:199-225`; `login.component.html:49-60` | High | Empty code cannot submit; success navigates; failure remains on the form with safe feedback. |
| FR-REC-001 | The forgotten-password entry shall collect an SSO account identifier and request an OTP after account verification. | `login.component.html:63-106`; `login.component.ts:240-280` | High | Loading and error states settle deterministically; account-enumeration policy remains open. |
| FR-REC-002 | The recovery flow shall verify the submitted OTP for the verified account and retain the returned reset token only in component state. | `login.component.ts:283-308` | High | Invalid/expired/reused codes are rejected; valid code advances once. Server behavior is unverified. |
| FR-REC-003 | The password-reset form shall collect password and confirmation and submit them with the verified account and reset token. | `login.component.html:109-140`; `login.component.ts:311-335` | High | Success and failure are distinguishable; password policy, matching, token lifetime, and single-use behavior require API confirmation. |
| FR-STATE-001 | Returning from recovery shall clear local identifiers, OTP/token/password values, errors, loading flags, and visibility state. | `login.component.ts:115-137` | High | Returning to login does not retain recovery secret/state in visible controls. |

## 9. Business rules and state transitions

| ID | Rule/state | Classification |
|---|---|---|
| BR-AUTH-001 | Direct login is hidden when `environment.production` is true. | Verified implementation |
| BR-AUTH-002 | Any truthy `developer` query parameter makes direct-login controls visible in production. | Verified implementation; business intent and security acceptance open |
| BR-AUTH-003 | Missing query access token on login invokes logout. | Verified implementation; desired session UX open |
| BR-MFA-001 | `AuthenticationService.enable2Fa` selects the second-factor state after primary login. | Verified frontend behavior; server authority open |
| BR-REC-001 | Recovery steps progress account → OTP → password; back resets local state. | Verified frontend behavior |

## 10. Roles and permissions

Server-side role, permission, and ownership enforcement are not available in the supplied repositories. The PRD cannot confirm whether direct login, SSO, parent SSO, recovery, 2FA, redirect targets, and post-login resources are protected for each actor. This is a release-blocking contract gap for security testing, not evidence of a defect by itself.

## 11. Data requirements and classification

| Data | Classification / required handling |
|---|---|
| Username / SSO member identifier | Personal identifier; minimize in reports and logs |
| Password and confirmation | Secret; never log, record, persist in artifacts, or place in URL |
| Access token, session IDP, reset token | Authentication secret; short-lived/single-use behavior requires external contract |
| Authenticator/OTP code | Authentication secret; rate, lifetime, reuse, and binding require external contract |
| User UUID | Internal identifier; exposure rules require confirmation |

## 12. Interface contracts

### Verified recovery endpoints invoked by the frontend

- `POST {apiUrl}/v1/login/forget`
- `POST {apiUrl}/v1/login/forget/request-otp`
- `POST {apiUrl}/v1/login/forget/verify-otp`
- `POST {apiUrl}/v1/login/reset`

Request and response schemas, status codes, error envelopes, rate limits, idempotency, and authorization are not present in the supplied scope. Login/SSO/2FA service endpoints are hidden behind `@uiigateway/core`.

## 13. Non-functional requirements and recommendations

These are recommendations pending adoption, not reconstructed requirements:

- Credentials and authentication secrets should use encrypted transport and never appear in URL, referrer, console, analytics, logs, screenshots, or reports.
- Authentication/recovery responses should resist account enumeration and timing differences.
- Login, OTP, and recovery should have server-side throttling, bounded attempts, and auditable outcomes.
- Session/token identifiers should rotate after authentication and be invalidated after logout/reset according to contract.
- The complete flow should be keyboard-operable with programmatic labels, focus management, perceivable errors, and non-color-only feedback.
- Critical authentication journeys should have component, contract, API, and narrow E2E regression coverage.

## 14. Audit and observability

No approved audit/telemetry contract was found. Required clarification includes events for login success/failure, SSO callback, 2FA verification, recovery request/verification/reset, throttling, account/session state changes, correlation IDs, retention, alerting, and privacy masking.

## 15. Risks and failure modes

| Risk ID | Evidence / concern | Impact | Current status |
|---|---|---|---|
| RISK-AUTH-URL-TOKEN | Query `access_token` and path session values are consumed by frontend; SSO component logs `window.location`. | Secret leakage through console/history/referrer/logging | Source-observed risk; runtime and platform contract unverified |
| RISK-AUTH-DEV-OVERRIDE | Truthy `developer` query reveals direct-login controls in production. | Alternate auth surface may be unintentionally exposed | Source-observed behavior; server protection and intent unverified |
| RISK-AUTH-EXTERNAL | Core login/SSO/2FA implementation is outside supplied source. | Critical security behavior cannot be reviewed or tested completely | Confirmed scope gap |
| RISK-REC-ENUMERATION | Account verification displays response information from server. | Account existence may be disclosed | Requires authorized runtime comparison |
| RISK-REC-POLICY | Client only requires both password fields; no visible match/length policy before submit. | Inconsistent UX or reliance on unknown server validation | Source-observed gap; backend contract required |
| RISK-OTP-STATE | False response branch after OTP verification is empty; errors depend on transport-error path. | UI may remain ambiguous on business-level rejection | Source-observed risk; runtime behavior unverified |
| RISK-QA-COVERAGE | No login/recovery component spec was found. | Regression may reach deployed environments undetected | Confirmed repository gap |

## 16. Assumptions, open questions, and decisions

1. Which repository/package owns `AuthenticationService`, and what exact version/source is deployed?
2. Is direct login via `?developer=...` approved in production, and what server-side restrictions protect it?
3. Are query/path authentication secrets permitted by the security architecture, and how are referrer/history/log risks mitigated?
4. What are the request/response/error contracts for login, SSO, 2FA, and the four recovery endpoints?
5. What are the rate-limit, lockout/throttling, OTP/reset-token lifetime, reuse, and account-binding rules?
6. Must password reset invalidate all existing sessions and refresh tokens?
7. What generic error policy prevents username/member enumeration?
8. Which environments, test identities, and WhatsApp sandbox may QA use?
9. What browser/accessibility/latency/reliability targets define release acceptance?
10. Which ClickUp/Confluence destinations and platform user IDs own frontend versus auth-platform defects?

## 17. Acceptance and release criteria

Before this feature can receive a release verdict:

- Product/auth owners approve or correct this as-is reconstruction.
- Missing API/session/security contracts are supplied.
- Test environment, identities, OTP channel, target allowlist, and cleanup rules are authorized.
- Critical/high test cases in the companion manifest are executed with sanitized evidence.
- Confirmed critical/high defects are resolved or explicitly accepted by an authorized owner.
- Flaky, blocked, and environment failures have separate dispositions.
- Production secrets and personal data are absent from all artifacts.

## 18. Traceability matrix

| Requirement | Source | Main risk | Planned test cases | Result |
|---|---|---|---|---|
| FR-AUTH-001..005 | Frontend routes/component/template | Developer override, errors, duplicate submission | TC-LOGIN-001..008 | Not run |
| FR-SSO-001..003 | Frontend component and SSO callback | URL token leakage, invalid callback, logout side effect | TC-SSO-001..006 | Not run |
| FR-MFA-001..002 | Frontend component/template | MFA bypass, OTP reuse/rate | TC-MFA-001..006 | Not run |
| FR-REC-001..003 | Frontend template/service/component | Enumeration, token reuse, password policy | TC-REC-001..010 | Not run |
| FR-STATE-001 | Frontend component | Sensitive state retained | TC-STATE-001 | Not run |
| Accessibility recommendations | Frontend template | Keyboard/label/error barriers | TC-A11Y-001..003 | Not run |
