from __future__ import annotations
from pathlib import Path
import gzip
from typing import TYPE_CHECKING
from mg_pipeline.util import run_parallel

if TYPE_CHECKING:
    from mg_pipeline.util import config


__all__ = ["run_madspin"]


def patch_madspin_card(card_path: Path, lhe_path: Path, madspin_results: Path) -> None:
    """Patch the MadSpin card to set the input LHE file path."""
    with card_path.open("r") as f:
        lines = f.readlines()

    with card_path.open("w") as f:
        for line in lines:
            stripped = line.strip()

            # 1. Remove 'set ms_dir' entirely.
            #    We want MadSpin to output to the source directory (default)
            #    so process_madspin_results can find and move the files.
            if stripped.startswith("set ms_dir"):
                continue

            # 2. Update the import line
            elif stripped.startswith("import"):
                # FIX: Use .absolute() so MadSpin finds the file regardless of CWD
                f.write(f"import {lhe_path.absolute()}\n")
                print(f"Patched import to: {lhe_path.absolute()}")

            # 3. Keep everything else
            else:
                f.write(line)


def process_madspin_results(cfg: config) -> None:
    """Process the results of the MadSpin runs.
    Madspin refuses to place the decayed LHE files in a custom directory,
    so we need to move them. The files are placed next to the input LHE
    files with '_decayed' appended to the filename before the extension.
    We will move them to the madspin results directory for further processing,
    unzip them maintaining their original name and delete the original files.
    """
    print("processing MadSpin results...")
    for decayed_zip in cfg.madgraph.lhe_dir.rglob("*_decayed.lhe.gz"):
        with gzip.open(decayed_zip, "rb") as f_in:
            # remove only the ".gz" suffix, keeping ".lhe"
            out_name = decayed_zip.name.removesuffix(
                ".gz"
            )  # or decayed_zip.with_suffix("").name
            target_file = cfg.madspin.results / out_name
            with target_file.open("wb") as f_out:
                f_out.write(f_in.read())
            print(f"Extracted {decayed_zip} to {target_file}")
            decayed_zip.unlink()
    print("MadSpin results processing completed.")


def run_madspin(cfg: config) -> None:
    print("Running MadSpin scripts...")

    madspin_results = cfg.runtime.intermediate_dir / "madspin_results"
    madspin_results.mkdir(parents=True, exist_ok=False)
    cfg.madspin.results = madspin_results

    madspin_cards_dir = cfg.runtime.intermediate_dir / "madspin_cards"
    madspin_cards_dir.mkdir(parents=True, exist_ok=True)

    # Setup logging
    log_dir = cfg.runtime.intermediate_dir / "logs" / "madspin"

    madspin_card_names = [card.name for card in cfg.madspin.scripts.glob("*.txt")]
    tasks: list[tuple[list[str], Path]] = []

    for lhe_file in cfg.madgraph.lhe_dir.rglob("*.lhe"):
        event_name = lhe_file.parent.parent.name
        print(event_name)

        matching_card_name = next(
            (
                card_name
                for card_name in madspin_card_names
                if card_name.startswith(f"decay_{event_name}")
            ),
            None,
        )
        if matching_card_name is None:
            raise ValueError(f"No matching MadSpin card found for LHE file {lhe_file}")

        template_card = cfg.madspin.scripts / matching_card_name

        per_job_card = madspin_cards_dir / f"{lhe_file.stem}.txt"
        per_job_card.write_text(template_card.read_text())

        patch_madspin_card(per_job_card, lhe_file, madspin_results)

        # FIX: Use .absolute() for binary and card
        command = [str(cfg.madspin.bin.absolute()), str(per_job_card.absolute())]

        log_file = log_dir / f"{lhe_file.stem}.log"
        tasks.append((command, log_file))

    run_parallel(cfg, tasks, madspin_results)
    print("MadSpin runs completed.")
    process_madspin_results(cfg)
