**fix(agent): prefer Ollama Modelfile num_ctx over GGUF training max**

## What does this PR do?

`_query_local_context_length()` was checking `model_info.context_length` (the GGUF training max) **before** `num_ctx` (the Modelfile runtime override) — the inverse of `query_ollama_num_ctx()`. The two helpers therefore disagreed on the same model:

\`\`\`
hermes-brain:qwen3-14b-ctx32k     # Modelfile: num_ctx 32768
underlying qwen3:14b GGUF         # qwen3.context_length: 40960
\`\`\`

\`query_ollama_num_ctx\` correctly returned \`32768\` (the value Ollama actually allocates KV cache for). \`_query_local_context_length\` returned \`40960\`, which let \`ContextCompressor\` grow conversations past \`32768\` before triggering compression — at which point Ollama silently truncates the prefix, corrupting context.

This PR swaps the order in \`_query_local_context_length()\` so \`num_ctx\` is checked first, matching \`query_ollama_num_ctx()\` and reflecting what the runtime will actually allocate.