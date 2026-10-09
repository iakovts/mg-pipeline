from __future__ import annotations
from mg_pipeline.util import run_parallel, run_task

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mg_pipeline.util import config

__all__ = ["run_rivet"]


def run_rivet(cfg: config) -> None:
    print("Running Rivet on Pythia results...")
    rivet_results = cfg.runtime.intermediate_dir / "rivet_results"
    rivet_results.mkdir(parents=True, exist_ok=False)
    cfg.rivet.results = rivet_results

    yoda_results = cfg.runtime.intermediate_dir / "yoda_results"
    yoda_results.mkdir(parents=True, exist_ok=False)
    cfg.yoda.results = yoda_results
    yoda_plots = yoda_results / "plots"
    yoda_plots.mkdir(parents=True, exist_ok=False)
    cfg.yoda.plots = yoda_plots

    analysis_file = list(cfg.rivet.analysis_dir.glob("*.cc"))
    if len(analysis_file) != 1:
        raise ValueError(
            f"Expected exactly one analysis .cc file in {cfg.rivet.analysis_dir}, found {len(analysis_file)}"
        )

    analysis_name = analysis_file[0].stem

    compile_command = [
        "rivet-build",
        f"Rivet{analysis_name}.so",
        str(analysis_file[0].resolve()),
    ]
    compile_log = cfg.runtime.intermediate_dir / "logs" / "rivet" / "compile.log"
    run_task(compile_command, cfg.rivet.analysis_dir, cfg.runtime.quiet, compile_log)

    # Setup logging for runs
    log_dir = cfg.runtime.intermediate_dir / "logs" / "rivet"

    tasks = []
    for hepmc_file in cfg.pythia.results.glob("*.hepmc"):
        yoda_output = rivet_results / hepmc_file.with_suffix(".yoda").name
        command = [
            "rivet",
            f"--analysis-path-append",
            str(cfg.rivet.analysis_dir),
            "-a",
            analysis_name,
            str(hepmc_file),
            "-o",
            str(yoda_output),
        ]
        log_file = log_dir / f"{hepmc_file.stem}.log"
        tasks.append((command, log_file))

    run_parallel(cfg, tasks, rivet_results)
    print("Rivet runs completed.")
