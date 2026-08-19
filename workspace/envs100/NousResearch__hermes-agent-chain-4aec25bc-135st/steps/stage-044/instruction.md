**feat(auth):  Switch to JWT token for inference against Nous and stop replaying invalid Nous refresh tokens**

## What this does

Improves Nous Portal inference auth by preferring scoped inference:invoke JWTs directly, while keeping the legacy opaque session-key path as a fallback. The fallback can be removed once the JWT path has proven stable, simplifying the credential flow.

The branch also fixes cases where rotated refresh tokens were not persisted soon enough, and prevents Hermes from repeatedly replaying revoked or invalid Nous refresh tokens by quarantining terminally dead OAuth material from the auth store, shared store, and singleton-seeded credential pool entries.

To avoid a broad runtime rewrite, the existing compatibility field agent_key remains the runtime credential field; it may now contain either an invoke JWT or a legacy session key. The selected inference path is controlled explicitly via inference_auth_mode (auto, fresh, legacy) and reported via auth_path.

Using invoke JWTs lets the inference service evaluate user entitlements and limits from token claims, which moves us toward removing the $0.10 free-user workaround. It also removes the extra session-key mint step in the common path: refresh_token -> access_token, instead of refresh_token -> access_token -> inference_key.