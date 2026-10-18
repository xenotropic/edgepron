# AGENTS.md

Standing instructions for AI coding agents (and any human collaborators)
working in this repository. Read this first; it is the source of truth for how
this project is versioned, built, and committed.

## Project facts

- **Repository:** `https://github.com/xenotropic/lexphon`
- **Default branch:** `main`
- **Language/framework:** Python, SQLite
- **License:** MIT © 2026 Joseph Morris
- **Coding agent:** Cline (the open-source coding agent). The app was originally
  written with DeepSeek; credit wording in the README reflects the project
  history, but this repository is maintained through Cline.
  **General intent:** To create a Python utility that constructs a dictionary to look up words that TTS engines struggle with, particularly proper nouns, foreign language words, foreign language phrases, abbreviations and acronyms and convert them to either IPA or respell (or both). 

## Git & CI conventions (IMPORTANT — must be followed)

1. **Commit locally only.** Never run `git push` unless the user (or another rule here, see e.g., 6) explicitly
   instructs you to push to the remote.
2. **Never create or push tags** unless the user explicitly instructs you to.
3. Do not commit build artifacts, local config, or anything already listed in
   `.gitignore`.
4. The directory .todo is in the repository and (exception to point 1) 
   is tracked and should be kept in sync (pull at start of job / push   at end) 
   on each turn by agents unless something else instructs you not to. 
5. **Prime git credentials at task start.** Before doing any other git work in
   a task, warm the credential cache so pushes/pulls don't re-prompt mid-task.
   Run a no-change write-auth probe (a *dry-run* — it never updates the remote,
   so it is an explicit exception to rule 1):

   ```bash
   git config --global credential.helper 'cache --timeout=28800'  # idempotent; 8h in-memory
   git push --dry-run origin HEAD                                  # prompts if the PAT is uncached; changes nothing
   ```

   Credentials are held in-memory only (the `git-credential-cache` daemon) for
   at most 8 hours and are never written to disk, so a PAT can't be replayed
   after the agent has stepped away. The Dev Containers extension injects a
   host-keychain credential helper into `/etc/gitconfig` at container start;
   `GIT_CONFIG_NOSYSTEM=1` (set in `.devcontainer/devcontainer.json`) disables
   it so git never falls back to the indefinite host keychain.
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
See the instructions in resources/ntfy about notifying the user when you have a question or when you are complete with the task.
