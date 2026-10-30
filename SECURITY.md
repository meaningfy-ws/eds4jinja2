# Security Policy

## Reporting a vulnerability

**Do not open a public issue for security problems.** Report privately via GitHub Security Advisories:
**[Report a vulnerability](https://github.com/meaningfy-ws/eds4jinja2/security/advisories/new)**.

We follow **coordinated disclosure**: we triage the private report, develop and release a fix, request
a CVE where warranted, and publish the advisory once a fixed release is available. Please give us a
reasonable window to remediate before any public disclosure.

We aim to acknowledge a report within a few working days.

## Supported versions

Security fixes land on the latest released line. Older lines are supported at maintainers' discretion.

| Version | Supported |
|---------|-----------|
| 2.x     | ✅ |
| 1.x     | ⚠️ best-effort (Python 3.11 users) |

## Handling fixed releases

A vulnerable release already published is **yanked** (kept installable for existing pins, hidden from
new resolves) and superseded by a patched release — it is never deleted, which would break downstream
pinned installs.
