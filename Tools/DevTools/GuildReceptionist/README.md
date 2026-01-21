# GuildReceptionist (DevTools)

Generate a clean, single copy-block guild from Codex output so you can paste into ChatGPT (or another agent) safely. No browser automation, no API posting.

## Why
- Enforces one fenced code block for the “Next Codex prompt.”
- Redacts common secrets by default (ghp_, AIza*, private keys).
- Produces GUILD.md (and optional zip) in one command.
- Optional clipboard copy for instant paste (manual paste keeps you in control).

## Usage
```
guild <input-file> [--stdin] [--clipboard] [--zip] [--allow-secrets] [--prompt-only] [--out <path>]
```
Examples:
- `guild codex_output.txt`
- `guild codex_output.txt --clipboard`
- `guild codex_output.txt --clipboard --zip`
- `cat codex_output.txt | guild --stdin`
- `guild codex_output.txt --prompt-only` (outputs only the fenced prompt)
- `guild codex_output.txt --prompt-only --out prompt.md`

## Behavior
- Input: text file (or stdin) containing Codex output.
- Output: GUILD.md with:
  - Context summary (first lines of input)
  - Files touched (if present in the input)
  - Next Codex prompt in exactly one fenced code block
- Optional: `guild_pack.zip` (if `--zip` is used) containing GUILD.md.
- Optional: copy GUILD.md to clipboard (`--clipboard`).
- Secret handling (default ON): ghp_*, AIza*, and private key blocks are replaced with `REDACTED_SECRET`. Use `--allow-secrets` to disable redaction (prints a warning).
- Code fence enforcement: if input has more than one fenced block (or a single unmatched fence), the tool errors out; otherwise it wraps the whole prompt in one block.
- `--prompt-only` outputs only the fenced prompt (no summary/headers), still enforcing redaction unless `--allow-secrets` is passed.
- `--out <path>` saves output to a file (prompt-only mode skips writing unless you set `--out`).

## Security notes
- DevTools-only; portable builds exclude Workbench/Tools/DevTools/** by default.
- No browser/chat automation; no API calls.
- No credentials stored. Redaction is best-effort—review GUILD.md before sharing.

## Example
Input: `examples/codex_output.txt`  
Command: `guild examples/codex_output.txt --clipboard`  
Output: `GUILD.md` (and copied to clipboard) with a single ready-to-paste code block.

## Workflow helpers
- `./ops/guild_from_codex.ps1 path\to\codex_output.txt`  
  Runs GuildReceptionist with `--clipboard --zip` and prints locations.
- `./ops/guild_to_codex.ps1`  
  Prints the standard footer: `IMPORTANT: Put your entire final response in a single code block.`

## Fast Loop (recommended)
1) Codex -> save output to a file.
2) `./ops/guild_from_codex.ps1 <file>` -> clipboard has the guild (and zip if needed).
3) Paste into ChatGPT.
4) When prompting Codex, append the footer from `guild_to_codex.ps1`:  
   `IMPORTANT: Put your entire final response in a single code block.`

Prompt-only example:
- `guild codex_output.txt --prompt-only` (stdout only)
- `guild codex_output.txt --prompt-only --out prompt.md` (saves prompt to file)

Redaction reminder:
- Default: ghp_/AIza/private keys -> `REDACTED_SECRET`
- Use `--allow-secrets` to skip redaction (prints warning)
