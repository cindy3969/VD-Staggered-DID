# VD — Staggered DID

Archive of the local VD research project, created on 2026-10-26.

- Research scripts, datasets, tables, figures and execution logs preserve their original folder paths.
- [Chat history](chatgpt_history/README.md): 18 local VD conversations, exported as Markdown and JSON (snapshot; ongoing chats may continue).
- [File inventory](github_archive/manifest.json): original paths, byte sizes and SHA-256 checksums.
- Files larger than 50 MiB are stored in the [GitHub Release](https://github.com/cindy3969/VD-Staggered-DID/releases/tag/vd-archive-2026-10-26). Very large files are split into numbered parts, mapped in the manifest.

## Restore large files

Clone this repository, then run:

```shell
python scripts/restore_github_assets.py
```

The script downloads and rejoins the release assets into their original paths and checks SHA-256 hashes. Existing files are verified and never overwritten.

## Archive scope

Local source files are retained. Installed dependency folders (`node_modules`, `.artifact_work/plot_packages`, `.artifact_work/textstat_deps`) are excluded; the manifest records these exclusions. These contain installed libraries or external directory links rather than project research outputs. Chat exports contain user and assistant messages, excluding internal reasoning, credentials and tool execution logs. Attachments outside the VD directory and cloud-only ChatGPT project conversations are not part of this local archive. The original local files and chats have not been deleted.
