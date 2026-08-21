**fix(model): avoid Bedrock credential probe in provider picker**

## What does this PR do?

Fixes a provider-picker slowdown where non-Bedrock /model and provider discovery paths could call Bedrock credential detection, causing botocore to probe EC2 instance metadata at 169.254.169.254 on local machines before returning no credentials.

The provider picker now treats Bedrock as available from fast explicit AWS signals such as AWS_PROFILE, AWS_ACCESS_KEY_ID plus AWS_SECRET_ACCESS_KEY, AWS_BEARER_TOKEN_BEDROCK, container credentials, or web identity. It only falls back to the full boto3 credential chain when Bedrock is the active provider, where implicit instance or task credentials are expected.

## Related Issue

N/A. Found while investigating a local /model minimax/minimax-m2.5:free --provider openrouter switch that was delayed by unrelated Bedrock IMDS timeouts.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_bedrock_model_picker.py`