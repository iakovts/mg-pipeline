# Prerequisites

No additional Python packages are required to run this script. It has been
developed on Python 3.13 but should run with previous versions (>3.10).

To run this script you need a usable **MadGraph5_aMC@NLO** installation with
**MadSpin**, **Pythia 8** and **Rivet** properly configured. The script should
be run from the same directory as the root directories of the above programs:

```
ProjectRoot/
├── MG5_aMC_vX_Y_Z/   # MadGraph5_aMC@NLO root directory
├── pythiaXYZW/       # Pythia8 root directory
├── Rivet-X.X.X/      # Rivet root directory
├── madgraph_scripts/ # MadGraph scripts directory
├── madspin_scripts/  # MadSpin scripts directory
├── analysis/         # Analysis directory
└── mg_pipeline/run_script.py
```

The script can work without providing the exact versions of the above programs
and will automatically detect them at runtime. You can specify your own
directories using flags — see [Usage](usage.md).

> **Note:** An example of the cards that can be used with this script can be
> found under the `example_cards` directory in this repository. Essentially they
> are simple txt files that are readily used by MadGraph/MadSpin anyway. You can
> have multiple different cards that can be executed in a single run.
