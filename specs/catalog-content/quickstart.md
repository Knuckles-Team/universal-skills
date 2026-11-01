# US-CONTENT quickstart

Run the proof for `US-CONTENT-R001` from the repository root with the project environment.

1. `uv run pytest tests/test_catalog_content.py` builds the served catalog in process and compares the listed skills with the folders.
2. `uv run pytest tests/test_spec_row_delivery_skill.py` (planned) proves `US-CONTENT-R004`. It reads the delivery skill and checks its steps and prohibitions.
