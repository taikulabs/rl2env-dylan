**build(deps): add qrcode to dingtalk + feishu extras (parity with messaging)**

## Summary

Completes the `qrcode` packaging work started in #4b1567f4 by @anthhub.

@anthhub landed `qrcode>=7.0,<8` on the `messaging` extra for Weixin's QR login (addressing part of #9431). This PR adds the same dep to the `dingtalk` and `feishu` extras, which use the same Python `qrcode` package but are independent of `[messaging]`:

- `hermes_cli/dingtalk_auth.py` — QR device-flow auth shipped in #11574
- `gateway/platforms/feishu.py:3962` — Feishu QR login rendering

Users who install `hermes-agent[dingtalk]` or `hermes-agent[feishu]` without `[messaging]` currently hit the same "QR render failed" error @zhangzhiqiangcs originally reported. Declaring the dep on each extra closes that gap.

### Changes

- `pyproject.toml`:
  - `dingtalk` extra — add `qrcode>=7.0,<8`
  - `feishu` extra — add `qrcode>=7.0,<8`
  - Pin matches @anthhub's recent `messaging` choice (`<8`) for consistency.
- `tests/test_project_metadata.py` — adds `test_dingtalk_extra_includes_qrcode_for_qr_auth` and `test_feishu_extra_includes_qrcode_for_qr_login`, mirroring @anthhub's `test_messaging_extra_includes_qrcode_for_weixin_setup`.

The `all` extra inherits from all three, so it picks up `qrcode` transitively.

### Tests

```
tests/test_project_metadata.py  4 passed
  test_requires_python_version_pin
  test_all_extra_includes_messaging
  test_all_extra_matrix_gated_by_linux
  test_messaging_extra_includes_qrcode_for_weixin_setup  (anthhub)
  test_dingtalk_extra_includes_qrcode_for_qr_auth        (new)
  test_feishu_extra_includes_qrcode_for_qr_login         (new)
```

### Closes

 — fully resolves the original report once this lands alongside @anthhub's messaging fix.