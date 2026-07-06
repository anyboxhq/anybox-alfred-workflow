# Alfred Workflow for Anybox

Search links and notes, save the current browser tab or clipboard, browse lists,
and toggle Anybox features — all from [Alfred](https://www.alfredapp.com), without
leaving the keyboard.

![Search Links](./screenshots/1.png)

![Search Links](./screenshots/2.png)

This workflow is a thin bridge between Alfred and the **local HTTP API** that
[Anybox](https://anybox.app) exposes on port `6391`. Each Alfred command runs a
small Python 3 or shell script that calls the API and renders the result as an
Alfred list. Anybox must be running for the workflow to work.

## Requirements

- **Anybox 2.0+** (running, with its local API enabled)
- **Alfred 5** with the Powerpack (workflows require the paid Powerpack)
- **Python 3** at `/usr/bin/python3` — pre-installed on macOS. No third-party
  Python packages are required; scripts use only the standard library.

## Installation

1. Download [`Anybox.alfredworkflow`](https://github.com/anyboxhq/anybox-alfred-workflow/raw/main/Anybox.alfredworkflow)
   and double-click it to install into Alfred.
2. In Anybox, go to **Settings → General** and copy your **API key**.
3. In Alfred, go to **Workflows → Anybox → Configure Workflow…** (the `[𝓍]` button)
   and paste the API key. Adjust the other options if desired (see
   [Configuration](#configuration)).
4. Trigger the search with the default keyword `sd␣` (space) followed by your query.

## Configuration

The workflow's behavior is driven by user-configurable variables set in
**Configure Workflow…**. They are exported as environment variables to the scripts.

- **`api_key`** — Your Anybox API key. Sent as the `x-api-key` header on
  authenticated requests (search endpoints).
- **`search_keyword`** — The keyword that triggers link search. Defaults to `sd`.
- **`show_full_urls`** — Show the full URL instead of just the host in result
  subtitles. (`checkbox` → `1`/`0`)
- **`show_dates`** — Append the "last opened" date to result subtitles, formatted
  as `Today at HH:MM`, `Yesterday at HH:MM`, `Mon DD, YYYY at HH:MM`, or `Mon DD, YYYY`.
- **`show_tags`** — Interleave matching tags into link search results.
- **`show_folders`** — Interleave matching folders into link search results.

> When both `show_tags` and `show_folders` are enabled, the per-container result
> limit drops from 5 to 3 to keep the list readable.

## Usage

Trigger any of the following keywords in Alfred.

### Search

- **`sd␣<query>`** (`search_keyword`) — Search links. Results show the favicon,
  title, and a configurable subtitle. Selecting a tag or folder (when enabled)
  drills into that container and searches links within it.
- **`search notes␣<query>`** — Search note-type items. Subtitle shows character
  count and, optionally, the date.
- **`show list␣`** — Browse all Presets, Smart Lists, Tags, and Folders and open
  the chosen one in Anybox.

**Result modifiers (search links / notes):**

- `⏎` — Open the link (or note text) / open the item.
- `⌘ ⏎` — Use the `anybox://document/<id>` deep link (opens the item in Anybox).
- `⌥ ⏎` — Copy a Markdown link `[title](url)`.
- `⇧ ⏎` — Use the raw URL.
- `⌘ C` — Copy the URL (notes copy their text).
- Quick Look (`⇧`) previews the link URL.

### Save

- **`save current tab␣`** — Save the frontmost browser tab to Anybox.
- **`save tab tags␣`** — Save the current tab, then pick tag(s) to apply.
- **`save tab folder␣`** — Save the current tab into a chosen folder.
- **`save clipboard␣`** — Save the clipboard contents.
- **`save clipboard tag␣`** — Save the clipboard, then pick tag(s).
- **`save clipboard folder␣`** — Save the clipboard into a chosen folder.
- **`save note␣<text>`** — Save a new note with the given text.

### Toggles & AnyDock

- **`show quick save␣`** — Show the Quick Save panel.
- **`toggle anydock␣`** — Show/hide AnyDock.
- **`toggle stash box␣`** — Show/hide the Stash Box.
- **`toggle link detection␣`** — Enable/disable link detection.
- **`switch profile␣`** — Switch to a selected AnyDock profile.
- **`open all profile␣`** — Open all links in a selected AnyDock profile.

## How it works

Every command shells out to a script under [`src/`](./src) that talks to Anybox's
local API. Search-type commands are Alfred **Script Filters**: they print
[Script Filter JSON](https://www.alfredapp.com/help/workflows/inputs/script-filter/json/)
(`{"items": [...]}`) to stdout, which Alfred renders. Action-type commands issue a
`POST`/`PUT` to trigger a side effect (save, toggle, switch).

Source scripts:

- `search-links.py` — `sd` search; queries `/search`, downloads each result's
  favicon locally into `./Link Icons/<id>/icon`, and optionally merges in matching
  tags/folders.
- `search-links-in-container.py` — Search scoped to a tag or folder (via the `id`
  and `type` environment variables).
- `search-notes.py` — Searches note items (`type=note`).
- `savenote.py` — `POST /save` with a JSON `{ "note": ... }` body.
- `show-list.py` — Aggregates `/presets`, `/filters`, `/tags`, `/folders` and maps
  each to its `anybox://` URL scheme.
- `select-folder.py` / `select-tag.py` — Folder/tag pickers used by the
  save-to-folder / save-with-tags flows.
- `anydock-profiles.py` — Lists AnyDock profiles for the switch/open-all commands.

## API interaction

All requests target the local Anybox server on port **`6391`**. Search/read
endpoints require the `x-api-key` header (set from `api_key`).

### Read (GET)

- `GET /search?q=<query>&limit=<n>` — Search links. Optional parameters:
  - `type=note` — restrict to notes.
  - `tag=<id>` — restrict to a tag.
  - `folder=<id>` — restrict to a folder.
- `GET /tags` — List tags.
- `GET /folders` — List folders.
- `GET /presets` — List presets.
- `GET /filters` — List Smart Lists.
- `GET /anydock-profiles` — List AnyDock profiles.
- `GET /images/<id>/icon` — Favicon for a link (cached locally by the workflow).

A search result object includes fields such as `id`, `title`, `url`, `host`,
`comment`, `dateLastOpened`, and (for notes) `description`.

### Write (POST / PUT)

- `POST /save` — Save a note. JSON body `{ "note": "<text>" }`.
- `POST /save-current-tab` — Save the frontmost browser tab.
- `POST /paste` — Save clipboard contents.
- `PUT  /document/<id>` — Associate a just-saved item with a folder/tag
  (used by the save-to-folder / save-with-tags flows).
- `POST /show-quick-save` — Show the Quick Save panel.
- `POST /toggle-anydock` — Toggle AnyDock.
- `POST /toggle-stashbox` — Toggle the Stash Box.
- `POST /toggle-link-detection` — Toggle link detection.
- `POST /switch-profile/<id>` — Switch AnyDock profile.
- `POST /open-all-in-profile/<id>` — Open all links in an AnyDock profile.

### `anybox://` URL scheme

Results also expose deep links used as action arguments:

- `anybox://show` — Open Anybox.
- `anybox://show?id=<id>` — Open a preset.
- `anybox://document/<id>` — Open a specific document (link/note).
- `anybox://tag/<id>`, `anybox://folder/<id>`, `anybox://filter/<id>` — Open a
  tag, folder, or Smart List.

### Error handling

If Anybox is not running (connection refused → `URLError`) or returns an error
(`HTTPError`), the scripts emit a friendly Alfred item explaining the problem and
offering to open Anybox (`anybox://show`) or install it from the Mac App Store.

## Troubleshooting

### "Search Links" action not working

The scripts rely on a working Python 3 at `/usr/bin/python3`. Verify it in
Terminal:

```
/usr/bin/python3
```

A healthy install prints something like:

```
Python 3.9.6 (default, Oct 18 2022, 12:41:40)
[Clang 14.0.0 (clang-1400.0.29.202)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

If you instead see:

```
xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools), missing xcrun at: /Library/Developer/CommandLineTools/usr/bin/xcrun
```

follow this fix: [Why am I getting an "invalid active developer path"…](https://apple.stackexchange.com/questions/254380/why-am-i-getting-an-invalid-active-developer-path-when-attempting-to-use-git-a/254381#254381).

Also confirm that Anybox is running and that the API key in **Configure Workflow…**
matches the one in **Anybox → Settings → General**.

## Supported versions

Developed and tested with **Anybox 2.0** and **Alfred 5**.

## Feature requests or bug reports

Open an issue on the [repository](https://github.com/anyboxhq/anybox-alfred-workflow).
