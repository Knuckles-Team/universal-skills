# US-SKILL-GRAPH-BUILDER — Research

## Is the pipeline still available

The script imports `SkillGraphPipeline` from the retired `agent_utilities` package. That package is not part of the workspace and not a dependency of this repository. The package index still serves its last release, so a build works only by installing a retired package. The pipeline therefore moves here (`R004.1`), where the skill owns it.

## Why daemon enrichment goes

The pipeline ingested the corpus into the graph when a daemon answered, and wrote `kg_ingested` into the records. The engine now imports a graph as a pack (`MEDULLA-TYPED-PACKS-R700`). A second ingest path from the builder would duplicate it, so `R004.2` deletes it.
