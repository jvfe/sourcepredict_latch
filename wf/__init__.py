"""
Predict metagenomics sample source with SourcePredict
"""

import re
import subprocess
from typing import List, Tuple

from latch import message, small_gpu_task, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import LatchDir, LatchFile, file_glob

from .docs import metadata


# From: https://github.com/latch-verified/bulk-rnaseq/blob/64a25531e1ddc43be0afffbde91af03754fb7c8c/wf/__init__.py
def _capture_output(command: List[str]) -> Tuple[int, str]:
    captured_stdout = []

    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
    ) as process:
        assert process.stdout is not None
        for line in process.stdout:
            print(line)
            captured_stdout.append(line)
        process.wait()
        returncode = process.returncode

    return returncode, "\n".join(captured_stdout)


@small_gpu_task
def run_sourcepredict(
    sources_csv: LatchFile,
    labels_csv: LatchFile,
    sink_count_file: LatchFile,
    output_dir: LatchDir,
) -> List[LatchFile]:

    _sp_cmd = [
        "sourcepredict",
        "-s",
        sources_csv.local_path,
        "-l",
        labels_csv.local_path,
        sink_count_file.local_path,
    ]

    return_code, stdout = _capture_output(_sp_cmd)

    for step, acc in zip(
        re.findall("Step.*", stdout), re.findall("Testing Accuracy.*", stdout)
    ):
        message("info", {"title": step, "body": acc})

    if return_code != 0:
        errors = re.findall("Exception.*", stdout)
        for error in errors:
            message(
                "error",
                {
                    "title": f"An error was raised while running SourcePredict",
                    "body": error,
                },
            )
        raise RuntimeError

    return file_glob("*.sourcepredict.csv", output_dir.remote_path)


@workflow(metadata)
def sourcepredict(
    sources_csv: LatchFile,
    labels_csv: LatchFile,
    sink_count_file: LatchFile,
    output_dir: LatchDir,
) -> List[LatchFile]:
    """Prediction/source tracking of metagenomic samples source using machine learning

    Sourcepredict
    --------

    Sourcepredict[^1] is a Python package distributed through Conda,
    to classify and predict the origin of metagenomic samples,
    given a reference dataset of known origins, a problem also known as
    source tracking. Sourcepredict solves this problem by using machine
    learning classification on dimensionally reduced datasets.

    [Read the documentation here](https://sourcepredict.readthedocs.io/en/latest/intro.html)

    ---
    [^1]: Borry, Maxime (2019). Sourcepredict: Prediction of metagenomic sample
    sources using dimension reduction followed by machine learning
    classification. Journal of Open Source Software, 4(41), 1540,
    https://doi.org/10.21105/joss.01540
    """
    return run_sourcepredict(
        sources_csv=sources_csv,
        labels_csv=labels_csv,
        sink_count_file=sink_count_file,
        output_dir=output_dir,
    )


LaunchPlan(
    sourcepredict,
    "Example SourcePredict Data",
    {
        "sources_csv": LatchFile(
            "s3://latch-public/test-data/4318/modern_gut_microbiomes_sources.csv"
        ),
        "labels_csv": LatchFile(
            "s3://latch-public/test-data/4318/modern_gut_microbiomes_labels.csv"
        ),
        "sink_count_file": LatchFile(
            "s3://latch-public/test-data/4318/dog_test_sink_sample.csv"
        ),
        "output_dir": LatchDir("latch:///sourcepredict_outputs/"),
    },
)
