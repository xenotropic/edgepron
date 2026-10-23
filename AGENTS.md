# AGENTS.md

Standing instructions for AI coding agents (and any human collaborators)
working in this repository. Read this first; it is the source of truth for how
this project is versioned, built, and committed.

## Project facts

- **Repository:** `https://github.com/xenotropic/edgepron`
- **Default branch:** `main`
- **Language/framework:** Python, SQLite
- **License:** MIT © 2026 Joseph Morris
- **Coding agent:** Cline (the open-source coding agent). The app was originally
  written with DeepSeek; credit wording in the README reflects the project
  history, but this repository is maintained through Cline.
  **General intent:** To create a Python utility that constructs a dictionary to look up words that TTS engines struggle with, particularly proper nouns, foreign language words, foreign language phrases, abbreviations and acronyms and convert them to either IPA or respell (or both). 

## Output language

All agent output (summaries, status reports, ticket notes, commit messages, and any prose replies to the user) must be written in English. The underlying model occasionally emits other languages (e.g. Chinese); re-render any such output in English before it reaches the user.

## Git & CI conventions (IMPORTANT — must be followed)

1. **Commit locally only.** Never run `git push` unless the user (or another rule here, see e.g., 6) explicitly
   instructs you to push to the remote.
2. **Never create or push tags** unless the user explicitly instructs you to.
3. Do not commit build artifacts, local config, or anything already listed in
   `.gitignore`.
4. The directory .todo is in the repository and (exception to point 1) 
   is tracked and should be kept in sync (pull at start of job / push   at end) 
   on each turn by agents unless something else instructs you not to. 
5. **Prime git credentials at task start.** Credentials live in an in-memory
   cache (the `git-credential-cache` daemon) shared by every shell in the
   container. The PAT is never written to disk and expires after 8h or a
   container rebuild. Two ways to refresh it:

   - **Agents** (non-interactive shells) must probe without hanging and delegate
     to the user when the cache is empty — see `.clinerules` → "GIT CREDENTIAL
     PRIMING RULE" for the exact probe/fallback commands.
   - **Humans** (interactive terminal) can prime the cache in one step — git
     prompts for `Username` (your GitHub login) and `Password` (paste the
     fine-grained PAT; it is not echoed), then caches it:

     ```bash
     cd /workspaces/edgepron && env -u GIT_ASKPASS GIT_CONFIG_NOSYSTEM=1 git push --dry-run origin main
     ```

     (`env -u GIT_ASKPASS` forces git's inline terminal prompt rather than VS
     Code's askpass dialog; `--dry-run` authenticates but never updates refs.)

   The Dev Containers extension injects a host-keychain credential helper into
   `/etc/gitconfig` at container start; we neuter it — the entry is removed for
   the session, and `GIT_CONFIG_NOSYSTEM=1` is set in `.devcontainer/devcontainer.json`
   + `.devcontainer/Dockerfile` so it stays ignored after any rebuild — leaving
   git with only the ephemeral 8h cache.
## Todo index (.todo/index)

The file `.todo/index` is a quick-reference listing of every ticket in this
repo and must be kept current. Agents update it whenever they create, resolve,
or close a ticket. Format:

- Two sections — `## Open` (top) and `## Closed` (bottom) — each sorted by
  ticket number, highest first.
- The first line states the **next open ticket number** (highest number in
  use + 1) so a new ticket can be created without hunting for the max.
- Every open-ticket line ends with `(Cline Difficulty Rating: X)`, a quick
  0–9 guess at difficulty: `0` = trivial / 100% confidence, `9` = "can't even
  guess how hard without a deep architectural dive". Closed tickets need no
  rating.
- A ticket's slug is its filename minus the leading `N-` and any trailing
  `-CLOSED`.

## Releasing (a quick reference for when instructed)

To cut a release, push a `v*` tag — e.g.:

```bash
git tag v0.1
git push origin v0.1
```

This triggers the release workflow, which builds the debug APK and creates a
GitHub Release attached to the tag. Only do this when explicitly instructed.

## Miscellaneous

- Throwaway planning notes/scratch files that should not be published live in
  the gitignored `resources/` directory. You should feel welcome to download other data sources, make throwaway scripts, or use other things that you need to in that file. Ask for user permission before downloading something that's going to be bigger than 2 gb

## Notifications to User

Send the user an ntfy push alert at two specific, mandatory points in every
turn. The exact `curl` commands live in `resources/ntfy`; run them verbatim.

1. **Before asking the user a question** (via the `ask` tool or otherwise) —
   send the "question" alert.
2. **As the very last action before ending the turn** (right before writing the
   final summary) — send the "wrapping up" alert.

These are easy to miss because they sit at the end of a long task; treat them
as part of the task's completion checklist, not an afterthought (see also the
NTFY NOTIFICATION RULE in `.clinerules`).
