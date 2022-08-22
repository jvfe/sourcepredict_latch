from latch.types import LatchAuthor, LatchMetadata, LatchParameter

metadata = LatchMetadata(
    display_name="SourcePredict",
    documentation="https://github.com/jvfe/sourcepredict_latch/blob/main/README.md",
    author=LatchAuthor(
        name="jvfe",
        github="https://github.com/jvfe",
    ),
    repository="https://github.com/jvfe/sourcepredict_latch",
    license="MIT",
)

metadata.parameters = {
    "sources_csv": LatchParameter(
        display_name="Source taxonomic count file",
        description="Path to source csv file.",
        section_title="Data",
    ),
    "labels_csv": LatchParameter(
        display_name="Source label file",
        description="Path to labels csv file.",
    ),
    "sink_count_file": LatchParameter(
        display_name="Sink taxonomic count file",
        description="Path to sink TAXID count table in csv format",
    ),
    "output_dir": LatchParameter(
        display_name="Output directory",
        description="Specify directory where output files should be sent to",
    ),
}
