**fix(skills): read name from SKILL.md frontmatter in skills_sync**

Cherry-pick of #6859 (konsisumer). Fixes skills_sync using dir name instead of frontmatter name, causing misclassification as 'local' instead of 'builtin'. 37 tests pass.