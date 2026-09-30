from pathlib import Path

import yaml
from langchain_core.documents import Document


REQUIRED_METADATA = {
    "document_id",
    "title",
    "category",
    "version",
    "source",
    "effective_date",
}


def _parse_markdown_file(path: Path) -> Document:
    content = path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        raise ValueError(
            f"Missing YAML front matter in document: {path}"
        )

    parts = content.split("---", 2)

    if len(parts) != 3:
        raise ValueError(
            f"Invalid YAML front matter in document: {path}"
        )

    metadata_raw = parts[1].strip()
    page_content = parts[2].strip()

    metadata = yaml.safe_load(metadata_raw)

    if not isinstance(metadata, dict):
        raise ValueError(
            f"Invalid metadata format in document: {path}"
        )

    missing_fields = REQUIRED_METADATA - metadata.keys()

    if missing_fields:
        raise ValueError(
            f"Missing metadata fields in {path}: "
            f"{sorted(missing_fields)}"
        )

    if not page_content:
        raise ValueError(
            f"Document has no content: {path}"
        )

    return Document(
        page_content=page_content,
        metadata=metadata,
    )


def load_documents(directory: str) -> list[Document]:
    directory_path = Path(directory)

    if not directory_path.exists():
        raise FileNotFoundError(
            f"Document directory not found: {directory}"
        )

    if not directory_path.is_dir():
        raise NotADirectoryError(
            f"Expected a directory: {directory}"
        )

    documents = []

    for path in sorted(directory_path.glob("*.md")):
        document = _parse_markdown_file(path)
        documents.append(document)

    return documents