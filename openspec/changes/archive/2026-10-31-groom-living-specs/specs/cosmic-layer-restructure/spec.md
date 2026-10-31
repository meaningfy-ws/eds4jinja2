## REMOVED Requirements

### Requirement: The version is bumped to 1.0.0 to signal the breaking move
**Reason**: It recorded a one-off version bump, not a behaviour; the package has since moved to 2.x
and the requirement is false. Versioning is release policy.
**Migration**: None. `eds4jinja2/VERSION` stays the single source of the version, kept in sync with
`pyproject.toml` by `make check-version`.
