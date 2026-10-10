# Disclaimer, citing and license

## Disclaimer

`mg-pipeline` is an independent wrapper/orchestration tool. It is **not** part
of, affiliated with, endorsed by, or supported by the developers of the software
it drives. In particular, this project wraps:

- [MadGraph5_aMC@NLO](https://launchpad.net/mg5amcnlo) — event generation
  (MadSpin is distributed as part of it; see
  [arXiv:1307.1694](https://arxiv.org/abs/1307.1694))
- [PYTHIA](https://pythia.org/) — parton shower, hadronization and decays
- [Rivet](https://rivet.hepforge.org/) — analyses and histogramming

This tool only automates running the above programs with your cards; it does not
modify, redistribute or replace them. Please install them from their official
sources, respect their licenses, and report problems with the tools themselves
to their own bug trackers. Issues with the wrapper belong in this repository.

## Citing

If you use this tool in academic work, please cite the underlying tools as
requested by their authors (see links above), in addition to this repository.

## License

GNU GPL v3.0 or later — see [LICENSE](https://github.com/iakovts/mg-pipeline/blob/main/LICENSE).
