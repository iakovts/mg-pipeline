from __future__ import annotations
import re
from pathlib import Path
from mg_pipeline.util import run_parallel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mg_pipeline.util import config

__all__ = ["run_pythia"]


def make_cmnd(template: Path, lhe: Path, dest: Path) -> Path:
    text = template.read_text()
    # FIX: Use .absolute() here.
    # Pythia runs in 'pythia_results', so a relative path like 'Experiments/...'
    # would be looked for inside 'pythia_results/Experiments/...', which is wrong.
    patched = re.sub(
        r"^Beams:LHEF.*$", f"Beams:LHEF = {lhe.absolute()}", text, flags=re.MULTILINE
    )
    dest.write_text(patched)
    return dest


def run_pythia(cfg: config) -> None:
    print("Running Pythia on MadSpin results...")
    pythia_results = cfg.runtime.intermediate_dir / "pythia_results"
    pythia_results.mkdir(parents=True, exist_ok=False)
    cfg.pythia.results = pythia_results

    # Setup logging
    log_dir = cfg.runtime.intermediate_dir / "logs" / "pythia"

    tasks = []
    for lhe_file in cfg.madspin.results.glob("*.lhe"):
        print(f"LHE file: {lhe_file}")
        cmnd_dest = cfg.pythia.results / f"{lhe_file.stem}.cmnd"
        make_cmnd(cfg.pythia.command_file, lhe_file, cmnd_dest)

        # FIX: Use .absolute() for the executable and command file
        command = [
            str(cfg.pythia.main_executable.absolute()),
            "-c",
            str(cmnd_dest.absolute()),
            "-o",
            str(lhe_file.name.replace(".lhe", ".hepmc")),
        ]
        log_file = log_dir / f"{lhe_file.stem}.log"
        tasks.append((command, log_file))

    run_parallel(cfg, tasks, cfg.pythia.results)
    print("Pythia runs completed.")
