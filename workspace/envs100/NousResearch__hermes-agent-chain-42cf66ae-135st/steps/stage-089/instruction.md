**fix(discord): preserve native document and video attachment support**

## Summary
- salvage the remaining non-redundant Discord attachment support from PR #1115 onto current main
- send local videos and documents as native Discord attachments instead of falling back to text path output
- reuse the shared Discord file attachment helper and preserve the optional file_name override for documents
- add regression coverage for Discord document/video attachment uploads