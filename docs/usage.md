# Usage

Run the pipeline script directly:

```bash
python run.py
```

Add the `--help` flag to see all available options:

```bash
python run.py --help
```

For example, to run in quiet mode:

```bash
python run.py -q
```

## Running only some stages (recommended)

You can run just a subset of the pipeline stages without having to interrupt
the run manually.

Valid stages are: `madgraph`, `madspin`, `pythia`, `rivet`.

Examples:

```bash
# Run only MadGraph + MadSpin and stop
python run.py --stages madgraph,madspin

# Run only Rivet (typically with --resume and an existing experiment directory)
python run.py --resume --intermediate-dir /path/to/Experiments_23 --stages rivet
```

## Resume mode

Resume mode is explicit:

- Without `--resume`, a new experiment folder is created (e.g. `Experiments`,
  `Experiments_2`, ...).
- With `--resume`, `--intermediate-dir` must point to an existing experiment
  directory and will be re-used.

## Installation (optional)

Since this is a proper Python project, you can also install it in editable mode:

```bash
pip install -e .
```
