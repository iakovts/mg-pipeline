"""Stage planning utilities.

We keep stage parsing/validation out of `run.py` so the entrypoint can stay as
clean orchestration.

A stage plan is always returned in canonical pipeline order.
"""

from __future__ import annotations

from dataclasses import dataclass


ALL_STAGES: tuple[str, ...] = ("madgraph", "madspin", "pythia", "rivet")


@dataclass(frozen=True)
class StagePlan:
    """Normalized stage plan.

    If `stages` is None, it means "use default behavior" (backwards compatible:
    run all stages except those disabled via skip flags).
    """

    stages: tuple[str, ...] | None


def parse_stage_list(stages: str | None) -> StagePlan:
    """Parse `--stages` value.

    Args:
      stages: comma-separated list, e.g. "madgraph,madspin".

    Returns:
      StagePlan(stages=None) if stages is None/empty.
      Otherwise a StagePlan with stages in canonical pipeline order.
    """
    if stages is None:
        return StagePlan(stages=None)

    raw = [s.strip().lower() for s in stages.split(",") if s.strip()]
    if not raw:
        return StagePlan(stages=None)

    unknown = [s for s in raw if s not in ALL_STAGES]
    if unknown:
        raise ValueError(
            f"Unknown stage(s): {unknown}. Valid stages: {', '.join(ALL_STAGES)}"
        )

    wanted = set(raw)
    ordered = tuple(s for s in ALL_STAGES if s in wanted)
    return StagePlan(stages=ordered)


def default_stage_list_from_skips(runtime: object) -> tuple[str, ...]:
    """Backwards-compatible default stage selection.

    Uses `runtime.skip_<stage>` boolean flags.
    """
    selected: list[str] = []
    for s in ALL_STAGES:
        if not getattr(runtime, f"skip_{s}"):
            selected.append(s)
    return tuple(selected)
