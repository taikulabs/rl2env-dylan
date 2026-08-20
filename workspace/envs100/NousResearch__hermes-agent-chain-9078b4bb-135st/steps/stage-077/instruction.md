**fix(api): allow dashboard updates for git checkouts in containers**

## Summary

Salvages #50469 by @libre-7 and applies the review narrowing requested there.

`_dashboard_local_update_managed_externally()` previously blocked every containerized dashboard from the local update API, even when the running install was a bind-mounted git checkout that can be updated with `hermes update`.

This PR now:
- Allows dashboard updates for containerized `git` installs, where the checkout is self-managed.
- Keeps hosted `/opt/data`, Docker-stamped, and `pip` installs managed externally.
- Blocks `pip` inside containers because its apply path mutates the running container filesystem and is not the bind-mounted checkout case.
- Adds regression coverage for docker/git/pip install-method handling inside containers.
- Adds @libre-7 to `AUTHOR_MAP` for release attribution.

## Changes from #50469

The original PR allowed both `git` and `pip` inside containers. The salvage keeps only the proven self-managed checkout case (`git`) and leaves `pip` blocked until/unless a safe container-pip update path is designed and tested.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_web_server.py`