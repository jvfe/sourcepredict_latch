"""
Predict metagenomics sample source with SourcePredict
"""

import subprocess
from enum import Enum
from pathlib import Path
from typing import List

from latch import medium_task, small_gpu_task, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import LatchDir, LatchFile, file_glob

from .docs import metadata


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

    subprocess.run(_sp_cmd)

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
