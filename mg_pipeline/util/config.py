from argparse import Namespace
from typing import Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import os
import re

from mg_pipeline.util.stages import StagePlan, parse_stage_list


def _resolve_dir(cli_val: Optional[str], *env_vars: str) -> Optional[Path]:
    """Return the first non-empty value from: CLI arg, then each env var in order.
    Returns (path, source_label) so callers can report how the path was resolved.
    Returns (None, None) if all sources are absent."""
    if cli_val:
        return Path(cli_val), f"CLI"
    for var in env_vars:
        val = os.environ.get(var)
        if val:
            return Path(val), f"${var}"
    return None, None


def verify_existence(config: object) -> None:
    """Helper function to verify that all Path fields in a config dataclass exist."""
    for field_value in config.__dict__.values():
        if isinstance(field_value, Path):
            if not field_value.exists():
                raise FileNotFoundError(
                    f"[ERROR] Inspecting values for {config.__class__.__name__}."
                    f" Path does not exist: {field_value}"
                    f" Please check your configuration and existence of files/folders."
                )


@dataclass
class BaseConfig:
    madgraph_dir: Optional[Path] = None
    pythia_dir: Optional[Path] = None
    pythia_examples_dir: Optional[Path] = None
    rivet_dir: Optional[Path] = None
    project_base_dir: Path = field(default=Path(__file__).parent.parent.parent.parent)

    # Resolution source labels — populated in __post_init__ for the startup banner.
    _madgraph_src: str = field(default="", init=False, repr=False)
    _pythia_src: str = field(default="", init=False, repr=False)
    _pythia_examples_src: str = field(default="", init=False, repr=False)
    _rivet_src: str = field(default="", init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.madgraph_dir:
            self.madgraph_dir, self._madgraph_src = _resolve_dir(
                None, "MADGRAPH"
            )
        else:
            self._madgraph_src = "CLI"
        if not self.madgraph_dir:
            self.madgraph_dir = self.folder_heuristics(target_folder="MG5_aMC")
            self._madgraph_src = "heuristic"

        if not self.pythia_dir:
            self.pythia_dir, self._pythia_src = _resolve_dir(None, "PYTHIA8")
        else:
            self._pythia_src = "CLI"
        if not self.pythia_dir:
            self.pythia_dir = self.folder_heuristics(target_folder="pythia8")
            self._pythia_src = "heuristic"

        if not self.pythia_examples_dir:
            self.pythia_examples_dir, self._pythia_examples_src = _resolve_dir(
                None, "PYTHIA8_EXAMPLES"
            )
        else:
            self._pythia_examples_src = "CLI"
        if not self.pythia_examples_dir and self.pythia_dir:
            # pythia_dir is the source tree root (e.g. pythia8316/); examples/ lives inside it.
            candidate = self.pythia_dir / "examples"
            self.pythia_examples_dir = candidate
            self._pythia_examples_src = "sibling convention"

        if not self.rivet_dir:
            self.rivet_dir, self._rivet_src = _resolve_dir(None, "RIVET", "RIVET_ROOT")
        else:
            self._rivet_src = "CLI"
        if not self.rivet_dir:
            self.rivet_dir = self.folder_heuristics(target_folder="Rivet")
            self._rivet_src = "heuristic"

    def folder_heuristics(self, target_folder: str) -> Path:
        regex: re.Pattern[str] = re.compile(rf"{target_folder}")
        candidates: Any = []
        for item in self.project_base_dir.iterdir():
            if item.is_dir() and regex.match(item.name):
                candidates.append(item)
        if len(candidates) != 1:
            raise ValueError(
                f"Ambiguous number of candidates found for {target_folder}: {candidates}"
            )
        return candidates[0]


@dataclass
class MadGraphConfig:
    base_config: BaseConfig
    bin: Path = field(init=False)
    scripts: Path = field(init=False)
    results: Optional[Path] = None  # Output directory for madgraph results
    lhe_dir: Optional[Path] = None  # Directory for extracted LHE files

    def __post_init__(self) -> None:
        if self.base_config.madgraph_dir is None:
            raise ValueError("madgraph_dir must not be None in BaseConfig")
        self.bin = self.base_config.madgraph_dir / "bin" / "mg5_aMC"
        self.scripts = self.base_config.project_base_dir / "madgraph_scripts"
        verify_existence(self)


@dataclass
class MadSpinConfig:
    base_config: BaseConfig
    bin: Path = field(init=False)
    scripts: Path = field(init=False)
    results: Optional[Path] = None  # Output directory for madspin results

    def __post_init__(self) -> None:
        if self.base_config.madgraph_dir is None:
            raise ValueError("madgraph_dir must not be None in BaseConfig")
        self.bin = self.base_config.madgraph_dir / "MadSpin" / "madspin"
        self.scripts = self.base_config.project_base_dir / "madspin_scripts"
        verify_existence(self)


@dataclass
class PythiaConfig:
    base_config: BaseConfig
    examples: Path = field(init=False)
    command_file: Path = field(init=False)
    main_name: str = "main134"
    main_executable: Path = field(init=False)
    results: Optional[Path] = None

    def __post_init__(self) -> None:
        if self.base_config.pythia_examples_dir is None:
            raise ValueError("pythia_examples_dir must not be None in BaseConfig")
        self.examples = self.base_config.pythia_examples_dir
        self.main_executable = self.examples / self.main_name
        self.command_file = self.examples / f"{self.main_name}.cmnd"
        verify_existence(self)


@dataclass
class RivetConfig:
    base_config: BaseConfig
    analysis_dir: Path = field(init=False)
    results: Optional[Path] = None
    intermediate_dir: Optional[Path] = None

    def __post_init__(self) -> None:
        self.analysis_dir = self.base_config.project_base_dir / "analysis"
        # rivet and rivet-build are on PATH after 'module load Rivet' — no
        # explicit bin paths needed here.
        verify_existence(self)


@dataclass
class YodaConfig:
    # base_config: BaseConfig
    results: Optional[Path] = None
    plots: Optional[Path] = None
    # custom_conf: Path = field(init=False)

    # def __post_init__(self) -> None:
    #     self.custom_conf = self.base_config.project_base_dir / "yoda_conf" / "config.plot"
    #     if not self.custom_conf.exists():
    #         raise FileNotFoundError(
    #             f"[ERROR] Yoda configuration file does not exist: {self.custom_conf}"
    #         )


@dataclass
class RuntimeConfig:
    base_config: BaseConfig
    intermediate_dir: Optional[Path] = None
    quiet: bool = False
    stage_plan: StagePlan = field(default_factory=lambda: StagePlan(stages=None))
    skip_madgraph: bool = False
    skip_madspin: bool = False
    skip_pythia: bool = False
    skip_rivet: bool = False
    resume_mode: bool = False

    def __post_init__(self) -> None:
        if not self.intermediate_dir:
            self.intermediate_dir = self.base_config.project_base_dir / "Experiments"

        # Ensure absolute path immediately
        self.intermediate_dir = self.intermediate_dir.resolve()

        if self.resume_mode:
            # In resume mode, we expect the directory to exist and we use it as-is
            if not self.intermediate_dir.exists():
                raise FileNotFoundError(
                    f"Resume mode enabled but intermediate directory does not exist: {self.intermediate_dir}"
                )
        else:
            # Create a new (incremental) directory if it already exists
            if self.intermediate_dir.exists():
                existing_dirs = [
                    d
                    for d in self.intermediate_dir.parent.iterdir()
                    if d.is_dir() and d.name.startswith(self.intermediate_dir.name)
                ]
                new_index = len(existing_dirs) + 1
                self.intermediate_dir = (
                    self.intermediate_dir.parent
                    / f"{self.intermediate_dir.name}_{new_index}"
                )
            self.intermediate_dir.mkdir(parents=True, exist_ok=False)

        verify_existence(self)


@dataclass
class config:
    base: BaseConfig
    madgraph: MadGraphConfig
    madspin: MadSpinConfig
    pythia: PythiaConfig
    rivet: RivetConfig
    runtime: RuntimeConfig
    yoda: YodaConfig


def setupcfg(args: Namespace) -> config:
    base_config = BaseConfig(
        madgraph_dir=Path(args.mg5) if args.mg5 else None,
        pythia_dir=Path(args.pythia) if args.pythia else None,
        pythia_examples_dir=Path(args.pythia_examples) if args.pythia_examples else None,
        rivet_dir=Path(args.rivet) if args.rivet else None,
    )

    # Resume is explicit: it controls whether we re-use an existing intermediate directory.
    resume_mode = bool(getattr(args, "resume", False))

    madgraph_config = MadGraphConfig(base_config=base_config)
    madspin_config = MadSpinConfig(base_config=base_config)
    pythia_config = PythiaConfig(base_config=base_config)
    rivet_config = RivetConfig(base_config=base_config)
    runtime_config = RuntimeConfig(
        base_config=base_config,
        intermediate_dir=Path(args.intermediate_dir) if args.intermediate_dir else None,
        quiet=args.quiet,
        stage_plan=parse_stage_list(getattr(args, "stages", None)),
        skip_madgraph=args.skip_madgraph,
        skip_madspin=args.skip_madspin,
        skip_pythia=args.skip_pythia,
        skip_rivet=args.skip_rivet,
        resume_mode=resume_mode,
    )
    yoda_config = YodaConfig()
    cfg = config(
        base_config,
        madgraph_config,
        madspin_config,
        pythia_config,
        rivet_config,
        runtime_config,
        yoda_config,
    )
    return cfg
