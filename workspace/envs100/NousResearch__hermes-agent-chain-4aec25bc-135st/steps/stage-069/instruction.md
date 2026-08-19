**fix(acp): render structured JSON tool output as markdown bullets**

Salvage of #23425 by @HenkDz cherry-picked onto current main.

## Summary
Non-polished tools (plugins, MCP, third-party) dumped raw JSON blobs (truncated at 5000 chars) into the Zed transcript AND attached the full unstructured blob as `raw_output`. Now renders JSON dict/list results as Markdown bullets with depth/item caps, and drops `raw_output` for those tools (consistent with the existing polished-tools pattern).

## Changes
- `acp_adapter/tools.py`: `_format_structured_value()` recursive Markdown bullet renderer (max_depth=3, max_items=8, per-string 240/500 limits, blanket 5000/7000 cap), `fallback_to_text=False` overload of `_format_generic_structured_result`, search_files files-list special case, empty-args shortcut in `build_tool_start`. `raw_output=None` when JSON detected.
- `tests/acp/test_tools.py`: 4 new tests covering dict-shaped JSON, list-shaped JSON, nested dict-of-dicts, and search_files files-only shape.

## Validation
`scripts/run_tests.sh tests/acp/test_tools.py` → 61/61 passing.

## Behavior note
Non-polished tools that previously got `raw_output=<json string>` will now get `raw_output=None` when the result was JSON. Matches existing polished-tools behavior; `raw_output` is `Optional` in the ACP schema.

 (salvage merge — author preserved).