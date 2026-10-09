import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import os
import sys
from typing import Optional
from mg_pipeline.util.config import config

"""
Utility functions to run tasks with controlled output handling.
"""

__all__ = ["run_task", "run_parallel"]


def run_task(
    command: list[str], working_dir: Path, quiet: bool, log_file: Optional[Path] = None
) -> None:
    """
    Runs a command.
    - If log_file is provided:
        - If quiet=True: writes stdout/stderr ONLY to log_file.
        - If quiet=False: writes to log_file AND streams to stdout (tee).
    - If log_file is None:
        - Behaves like standard subprocess.run (stdout to console or devnull).
    """
    f_log = None
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        f_log = log_file.open("w")

    try:
        if quiet:
            # Quiet mode: Output goes to log file (if exists) or DEVNULL
            target = f_log if f_log else subprocess.DEVNULL
            subprocess.run(
                command,
                check=True,
                cwd=working_dir,
                stdout=target,
                stderr=subprocess.STDOUT,
            )
        else:
            # Verbose mode
            if f_log:
                # Tee mode: Stream to stdout AND write to file using Popen
                with subprocess.Popen(
                    command,
                    cwd=working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,  # Line buffered
                ) as proc:
                    if proc.stdout:
                        for line in proc.stdout:
                            sys.stdout.write(line)
                            f_log.write(line)

                    if proc.wait() != 0:
                        raise subprocess.CalledProcessError(proc.returncode, command)
            else:
                # Standard run, output goes to stdout naturally
                subprocess.run(command, check=True, cwd=working_dir)
    finally:
        if f_log:
            f_log.close()


def run_parallel(
    cfg: config, tasks: list[tuple[list[str], Path]], working_dir: Path
) -> None:
    cpu_count = max(1, (os.cpu_count() or 1) - 1)
    with ProcessPoolExecutor(max_workers=cpu_count) as pool:
        futures = {
            pool.submit(run_task, command, working_dir, cfg.runtime.quiet, log_file): (
                command,
                log_file,
            )
            for command, log_file in tasks
        }

        try:
            for future in as_completed(futures):
                cmd_list, log_file = futures[future]
                script_name = log_file.stem
                try:
                    future.result()
                    print(f"✅ Completed: {script_name}")
                except Exception as e:
                    print(f"❌ Error running {script_name}: {e}")
                    # Cancel all other pending futures to stop execution ASAP
                    for f in futures:
                        f.cancel()
                    # Shutdown pool immediately
                    pool.shutdown(wait=False, cancel_futures=True)
                    raise e
        except Exception:
            raise
