import sys
import argparse
from mg_pipeline.util.config import setupcfg, config


def _print_banner(cfg: config) -> None:
    b = cfg.base
    rows = [
        ("MadGraph dir",      cfg.madgraph.bin.parent,       b._madgraph_src),
        ("MadGraph binary",   cfg.madgraph.bin,               b._madgraph_src),
        ("MadSpin binary",    cfg.madspin.bin,                b._madgraph_src),
        ("Pythia prefix",     b.pythia_dir,                   b._pythia_src),
        ("Pythia examples",   cfg.pythia.examples,            b._pythia_examples_src),
        ("Pythia main134",    cfg.pythia.main_executable,     b._pythia_examples_src),
        ("Rivet dir",         b.rivet_dir,                    b._rivet_src),
        ("Analysis dir",      cfg.rivet.analysis_dir,         "project"),
        ("Intermediate dir",  cfg.runtime.intermediate_dir,   "runtime"),
    ]
    width = max(len(label) for label, _, _ in rows)
    print("\n┌─ mg-pipeline resolved paths ──")
    for label, path, src in rows:
        print(f"│  {label:<{width}}  {path}  [{src}]")
    print("└" + "─" * 34 + "\n")


def parse_arguments_and_setup() -> config | None:
    parser = argparse.ArgumentParser(
        description="Run scripts with configurations for MadGraph, MadSpin, Pythia, and Rivet."
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        default=False,
        help=(
            "Reuse an existing --intermediate-dir instead of creating a new Experiments[_N] folder. "
            "Requires --intermediate-dir to point to an existing directory."
        ),
    )
    parser.add_argument(
        "--stages",
        type=str,
        default=None,
        help=(
            "Comma-separated list of stages to run in order. "
            "Stages: madgraph,madspin,pythia,rivet. Example: --stages madgraph,madspin"
        ),
    )
    parser.add_argument(
        "--show-paths",
        action="store_true",
        help="Show the paths of the configured tools and exit.",
    )
    parser.add_argument(
        "--mg5",
        type=str,
        required=False,
        default=None,
        help="Path to MadGraph installation directory.",
    )
    parser.add_argument(
        "--pythia",
        type=str,
        required=False,
        default=None,
        help="Path to Pythia installed prefix (lib/, bin/). Default: $PYTHIA8.",
    )
    parser.add_argument(
        "--pythia-examples",
        type=str,
        required=False,
        default=None,
        help="Path to Pythia examples directory containing main134. Default: $PYTHIA8_EXAMPLES.",
    )
    parser.add_argument(
        "--rivet",
        type=str,
        required=False,
        default=None,
        help="Path to Rivet installation directory.",
    )
    parser.add_argument(
        "--intermediate-dir",
        type=str,
        required=False,
        default=None,
        help=(
            "Base experiments directory (default: ./Experiments). "
            "With --resume, this must point to an existing experiment folder."
        ),
    )
    parser.add_argument(
        "--rivet-analysis-dir",
        type=str,
        required=False,
        default=None,
        help="Path to Rivet analysis directory.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Run tasks in quiet mode, suppressing output.",
    )

    # Skip flags
    parser.add_argument(
        "--skip-madgraph", action="store_true", help="Skip MadGraph generation."
    )
    parser.add_argument(
        "--skip-madspin", action="store_true", help="Skip MadSpin decay."
    )
    parser.add_argument(
        "--skip-pythia", action="store_true", help="Skip Pythia showering."
    )
    parser.add_argument(
        "--skip-rivet", action="store_true", help="Skip Rivet analysis."
    )

    args = parser.parse_args()

    # Validation: resume is explicit and requires an existing directory
    if args.resume and not args.intermediate_dir:
        parser.error("--resume requires --intermediate-dir")

    cfg = setupcfg(args)

    if not args.quiet:
        _print_banner(cfg)

    if args.show_paths:
        sys.exit(0)
    return cfg
