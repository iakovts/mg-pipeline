import sys

from mg_pipeline.util import parse_arguments_and_setup
from mg_pipeline.util.stages import ALL_STAGES, default_stage_list_from_skips

from mg_pipeline.tasks import *

def main() -> None:
    cfg = parse_arguments_and_setup()
    assert cfg

    # Determine which stages to run.
    if cfg.runtime.stage_plan.stages is None:
        selected = default_stage_list_from_skips(cfg.runtime)
    else:
        selected = cfg.runtime.stage_plan.stages

    selected_set = set(selected)

    try:
        # Run stages in pipeline order, but only those selected.
        for stage in ALL_STAGES:
            if stage not in selected_set:
                print(f"⏩ Skipping {stage}.")

                # If a later stage is selected, seed cfg paths that are normally
                # produced by the skipped stage.
                if stage == "madgraph":
                    cfg.madgraph.results = (
                        cfg.runtime.intermediate_dir / "madgraph_results"
                    )
                    cfg.madgraph.lhe_dir = cfg.runtime.intermediate_dir / "lhe_files"
                elif stage == "madspin":
                    cfg.madspin.results = cfg.runtime.intermediate_dir / "madspin_results"
                elif stage == "pythia":
                    cfg.pythia.results = cfg.runtime.intermediate_dir / "pythia_results"
                continue

            if stage == "madgraph":
                run_madgraph(cfg=cfg)
            elif stage == "madspin":
                run_madspin(cfg=cfg)
            elif stage == "pythia":
                run_pythia(cfg=cfg)
            elif stage == "rivet":
                run_rivet(cfg=cfg)
            else:
                raise RuntimeError(f"Unhandled stage: {stage}")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
