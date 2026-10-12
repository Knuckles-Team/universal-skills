# Non-merge schema bundle prototype

This branch preserves an unsuccessful, unintegrated prototype for review. **Do
not merge or release it.** Schema redesign was stopped; the generator does not
call this code and no supported storage format has been adopted.

The preserved experiment consists of
[`schema_bundle_build.py`](../scripts/schema_bundle_build.py) and
[`templates/schema_bundle.py`](../scripts/templates/schema_bundle.py). It interns
identical JSON objects when references reduce storage and checks that hydration
restores the canonical document bytes. It is not an accepted runtime loader or a
solution to the generated-artifact policy question.

The offline ArtCraft experiment used published source
`0b6750101934e4fefefeee3fe72b4842d4f9baca` and base
`bf7207daa6c56ff29c82fcc863864d6a34e56cb7`, with unchanged pipelines policy at
`7b3d18d72b5622d455ece3bbe45a9482bc6e8b5e`:

- All three hydrated JSON artifacts were byte-identical to their inputs.
- The bundle contained 97 definitions; stored JSON fell from 302,505 to 171,806
  bytes.
- The differential clone probe measured 127 baseline pairs, 54 resulting pairs,
  and **26 new pairs**. Moving repeated fragments into the bundle did not clear
  the gate. This is a failed acceptance result.

No scanner policy, pipeline references, pilot source, credentials, live service,
deployment or released package was changed by this experiment. Preservation
checks on this branch do not establish security, runtime, schema-format or
ArtCraft gate acceptance. No further feature development belongs to this snapshot.
