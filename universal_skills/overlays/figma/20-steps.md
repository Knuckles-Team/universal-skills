---
mode: append
---
## Steps

1. Check that `FIGMA_TOKEN` exists in the shell or the project `.env` before the first command, for example with `grep -c '^FIGMA_TOKEN=' .env`. Verify that it prints 1, otherwise tell the person how to create one and stop.
2. Import brand colours and type with `npx hyperframes figma tokens <fileKey>` and paste the printed entries into `data-composition-variables`. Verify that the output lists the token entries.
3. Import a frame with `npx hyperframes figma component '<url or fileKey:nodeId>'`. Verify that `ls compositions/components/` shows the new package.
4. Import logos and images with `npx hyperframes figma asset '<url or fileKey:nodeId>' --format svg`. Verify that a file appears under `.media/` with its source recorded.
5. Compare hero components against Figma's pixels with `npx hyperframes figma asset '<same node>' --format png`. Verify that text drift is fixed or reported, and that no Figma URL remains with `grep -rn 'figma.com' compositions/`.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `BAD_TOKEN` (401) | The token expired or was revoked | Ask the person to create a new personal access token and set it themselves |
| `FORBIDDEN` (403) | A scope is missing or the file is not visible | Read the missing scope from the message and ask the person to regrant it |
| `RATE_LIMITED` (429) | Too many nodes in one call | Wait a minute or import fewer nodes per call |
| An unknown token stays a literal marked `data-figma-unresolved` | The library's tokens were not imported | Run `npx hyperframes figma tokens <libraryFileKey>` and re-import the component |
