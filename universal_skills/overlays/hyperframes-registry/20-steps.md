---
mode: append
---
## Steps

1. Search the catalog with `npx hyperframes catalog --query "<what the beat should do, in English>" --json`. Verify that the envelope names the tier that answered and lists candidate items.
2. Install the chosen item with `npx hyperframes add <name> --json`. Verify that the output lists the written files and a mount snippet, and that `ls compositions/` shows the new file.
3. Mount a block with `data-composition-src` and a `data-composition-id` equal to its own id, or merge a component into your scene. Verify that `grep -n 'data-composition-id' index.html` shows the mount.
4. Set variables with `add --vars '{"title":"..."}'` or `data-variable-values` on the host. Verify that `npx hyperframes check --json` reports no errors for the mounted item.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| The catalog finds nothing | The query is not in English or the `words` tier lacks the term | Rephrase in English, or offer `--on-device` after telling the person about the ~33 MB download |
| `add` fails offline | `add` needs the network even for a cached item | Reconnect and re-run `npx hyperframes add <name> --json`, since search alone works offline |
| Two items collide | Their ids were renamed or unprefixed | Restore the prefixed ids the installed source shipped with |
| Nothing fits the effect | The registry has no matching item | Run the pre-filled `npx hyperframes feedback --search-miss` line from the catalog output, then hand-build |
