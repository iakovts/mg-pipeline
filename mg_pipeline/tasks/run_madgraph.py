from __future__ import annotations
from pathlib import Path
import gzip
from mg_pipeline.util import run_parallel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mg_pipeline.util import config

__all__ = ["run_madgraph"]


def run_madgraph(cfg: config) -> None:
    print("Running MadGraph scripts...")
    script_files = list(cfg.madgraph.scripts.glob("*.txt"))

    # Setup logging
    log_dir = cfg.runtime.intermediate_dir / "logs" / "madgraph"

    tasks = []
    for script in script_files:
        # FIX: Use .absolute() because we change CWD to madgraph_results
        cmd = [str(cfg.madgraph.bin.absolute()), str(script.absolute())]
        log_file = log_dir / f"{script.stem}.log"
        tasks.append((cmd, log_file))

    madgraph_results = cfg.runtime.intermediate_dir / "madgraph_results"
    madgraph_results.mkdir(parents=True, exist_ok=False)
    cfg.madgraph.results = madgraph_results

    run_parallel(cfg, tasks, madgraph_results)
    process_madgraph_results(cfg)


def process_madgraph_results(cfg: config) -> None:
    print("processing MadGraph results...")
    # First find all the results directories in the madgraph_results directory
    # Each result directory has an /Events subdirectory, and there we can find
    # the directories for each run. The .lhe.gz files are there. Here we will
    # extract them to the madgraph_results root directory for further processing.
    results_dir = list(
        res_dir for res_dir in cfg.madgraph.results.iterdir() if res_dir.is_dir()
    )
    lhe_dir = Path(cfg.runtime.intermediate_dir) / "lhe_files"
    lhe_dir.mkdir(parents=True, exist_ok=False)
    cfg.madgraph.lhe_dir = lhe_dir
    for result_dir in results_dir:
        events_dir = result_dir / "Events"
        if not events_dir.is_dir():
            continue
        for run_dir in events_dir.iterdir():
            if not run_dir.is_dir():
                continue
            target_dir = lhe_dir / result_dir.name / run_dir.name
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / f"{result_dir.name}_{run_dir.name}.lhe"
            for lhe_gz_file in run_dir.glob("*.lhe.gz"):
                with (
                    gzip.open(lhe_gz_file, "rb") as f_in,
                    target_file.open("wb") as f_out,
                ):
                    f_out.write(f_in.read())
                print(f"Extracted {lhe_gz_file} to {target_file}")
                # unlink the .gz file after extraction
                lhe_gz_file.unlink()
    print("MadGraph results processing completed.")
