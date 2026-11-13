# AQABSI Stack and Profile Routing

AQABSI resolves configuration in this order: `organization-bsi` → team profile → project profile. A lower layer may add verified paths, commands, owners, thresholds, and selected stack profiles, but it cannot enable managed external data egress, unauthorized active security testing, production active testing, unauthorized publication, or guessed assignment.

Use `config/module-registry.json` as the routing source. Detection cues are evidence prompts, not permission to assume a framework. Confirm the dependency/entry point before selecting a profile; otherwise choose `unknown-web` or `unknown-service` and derive the real call graph.

## Universal backend flow

Trace entry point/route → middleware/policy → validation → business/service logic → data/integration boundary → serialization/error/audit result. Framework profiles only locate these responsibilities; they do not force one architecture.

## Universal web flow

Trace route/guard → state/data source → form/input validation → network contract → rendering states → accessibility/focus → side effects and cleanup. Use the isolated web adapter only after a target URL, accounts, data rules, and authority are established.

## Module selection

Select modules by observed feature and risk. CRUD is a family, not one generic case: GET collection, GET detail, POST, PUT, PATCH, and DELETE have different contracts and risks. Authentication adds login/session and authorization modules; uploads, queues, integrations, migrations, and non-functional checks are selected only when evidence or change impact makes them relevant.
