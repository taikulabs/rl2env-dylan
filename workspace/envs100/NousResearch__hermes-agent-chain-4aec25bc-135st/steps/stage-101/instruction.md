**fix(packaging): ship dashboard plugin assets in wheel**

Salvages #23737 by @LeonSGP43.

Adds `plugins/*` manifest.json and dist/ globs to setuptools package-data so wheel installs ship the bundled dashboard plugin assets. Without these, `/api/dashboard/plugins` can't discover plugin assets outside a source checkout.

Original branch was stale; applied the substantive change manually onto current main. Authorship preserved via rebase merge.

## Validation
- New regression test (test_dashboard_plugin_manifests_and_assets_are_packaged) passes.