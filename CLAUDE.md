# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

This is the Flask webserver for **M1CR0B1AL1Z3R 2.0**, a Tel Aviv University (Pupko Lab) web tool for comparative
analysis of bacterial genomes at scale (published in Nucleic Acids Research, 2025). This repo is the web
front-end/job-submission layer only — it does not contain the actual bioinformatics pipeline. It uploads user
genome files, submits a job to a separate pipeline codebase, polls job state on disk, and renders results.

## Critical dependency on a sibling repo

This app cannot run standalone: at import time it appends a sibling repository's `pipeline/flask` directory to
`sys.path` and imports several modules from it (`flask_interface_consts`, `SharedConsts`, `slurm_example`). This
happens in `app/__init__.py`, `Job_Manager_API.py`, `JobHandler.py`, and `utils.py`, each guarded by `consts.LOCAL`:

- `consts.LOCAL = True` → looks in `consts.MICROBIALIZER_PIPELINE_LOCAL_PATH` (`C:\repos\microbializer` by default).
- `consts.LOCAL = False` → looks in the production path `/microbializer/pipeline/flask` on the TAU server.

If that sibling repo is missing/misconfigured locally, imports of `app` will fail. When making changes that touch
job submission, results parsing, or shared UI constants, check whether the corresponding definitions live in that
sibling `microbializer` pipeline repo rather than here.

Key shared symbols pulled from the sibling repo include: `UI_CONSTS`, `State`, `USER_FILE_NAME_TAR/ZIP`,
`WEBSERVER_ADDRESS`, `ALLOWED_EXTENSIONS`, `WEBSERVER_PROJECT_ROOT_DIR`, `WEBSERVER_DOMAIN`, job parameter key
constants (`IDENTITY_CUTOFF`, `JOB_NAME`, `EMAIL`, etc.), `EMAIL_CONSTS`, `OWNER_EMAIL`, and `submit_job` (actual
job/Slurm submission logic).

## Architecture

- **`app/__init__.py`** — the single Flask app module. All routes are defined here directly (no blueprints). Routes
  cover: home/upload (`/`), process polling (`/process_state/<id>`), results (`/results/<id>`), file download
  (`/download/<id>/<file>`, `/download_page/<id>`), paginated OG table (`/get_table/<id>`), static pages
  (`/about`, `/overview`, `/gallery`, `/tools`, `/faq`), error display (`/error/<type>`, `/error_from_job/<id>`),
  and a debug kill-switch (`/debug/killswitch`).
- **`Job_Manager_API.py`** — `Job_Manager_API` class: the main business-logic layer between Flask routes and job
  state on disk. Handles process-id generation, input file discovery/validation dispatch, submitting jobs (via
  `JobHandler.Handler`), reading job state/progress/results (histogram data, orthogroups table, Newick species
  tree, summary stats) from files under each job's process folder, and sending status emails.
- **`JobHandler.py`** — `Handler` class: thin wrapper that writes job parameters to a JSON file and calls the
  sibling repo's `submit_job` (Slurm submission) with a formatted command template.
- **`InputValidator.py`** — validates uploaded genome files are actually FASTA (using Biopython `SeqIO`),
  transparently un-gzipping `.gz` inputs first.
- **`utils.py`** — logging setup (writes to `local_run/logs/` when `LOCAL`, else `/var/www/vhosts/<domain>/logs/`)
  and a `send_email` helper (uses TAU's `mxout.tau.ac.il` SMTP relay).
- **`consts.py`** — path configuration and the `LOCAL` / `CAN_SUBMIT_NEW_JOBS` feature flags, plus the mapping from
  internal pipeline argument names to user-facing display strings (`ARG_NAME_IN_PIPELINE_TO_DISPLAY`).
- **`run.py`** — dev entrypoint (`python run.py`); production likely serves `app` via WSGI (`wsgi.py` is
  git-ignored, created only on the server).

### Job lifecycle / state model

Each submitted job gets a `process_id` (UUID) and a folder under the upload root (`local_run/user_results/<id>`
locally, or a server path from the sibling repo otherwise). Job state is inferred purely from **which files exist**
in that folder (`Job_Manager_API.get_process_state`): an error file means `Crashed`, a "finished" marker means
`Finished`, a progress-bar CSV means `Running`, otherwise `Init`. There is no database — polling
(`/process_state/<id>`) re-reads the filesystem each time and the front end auto-refreshes.

Results (`get_summary_stats`, `get_historgram_data`, `get_orthologous_data`, `get_newick_tree`, `get_progress_bar`)
are all read from well-known filenames inside the process folder, with the filenames themselves defined in the
sibling repo's `flask_interface_consts`. The `/gallery` feature lets pre-computed example runs (living under the
gallery path) be viewed through the same results pipeline as user-submitted jobs — `get_process_folder` resolves a
`process_id` against gallery directories first, then the upload root.

### Frontend

- Server-rendered Jinja templates in `app/templates/` (`base.html` / `base_result.html` as layout bases).
- Plain JS in `app/static/js/` (`home.js`, `results.js`, `consts.js`, `colors.js`, `utlilities.js`) — no JS bundler
  or framework.
- Tailwind CSS lives in `app/tailwind/` as a separate npm project; compiled output is `app/static/css/output.css`.
- `render_template_wrapper()` in `app/__init__.py` injects a random background image into every page render — use
  it instead of calling `render_template` directly when adding new routes/pages.

## Common commands

There is no test runner, lint config, or CI wired up in this repo (`test/` contains ad hoc scripts, not a test
suite). Development is:

```bash
# Python env (conda, per env.yaml)
conda env create -f env.yaml
conda activate microbializer_webserver

# Run the dev server (defaults to consts.LOCAL, port 5000)
python run.py

# Tailwind CSS build (from app/tailwind/)
cd app/tailwind
npm install
npx tailwindcss -i input.css -o ../static/css/output.css --watch
```

To run locally you must also have the sibling `microbializer` pipeline repo checked out at the path configured in
`consts.py` (`MICROBIALIZER_PIPELINE_LOCAL_PATH`, default `C:\repos\microbializer`), with `consts.LOCAL = True`.

## Deployment

Deployed via SFTP to the TAU server `power9login.tau.ac.il` (see `.idea/deployment.xml`), served under
`/lsweb/pupko` in production, with `consts.LOCAL = False` pointing at `/microbializer/pipeline/flask` for the
sibling pipeline code.
