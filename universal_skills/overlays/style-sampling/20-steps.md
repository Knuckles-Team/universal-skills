---
mode: append
---
## Steps

1. Run `npx hyperframes auth status` first, every time. Verify that it shows a signed-in account, otherwise ask the person to run `npx hyperframes auth login` themselves.
2. Choose the template from the table by the person's topic and wait for their pick when more than one fits. Verify that the pick is one of the slugs in the table, such as `collage-explainer`.
3. Pull it with `npx hyperframes templates pull <slug>`. Verify that `ls templates/<slug>/` lists the template and its `series/` folder.
4. Read `references/remix.md` and follow the template's `series/<series>/REMIX.md` through the storyboard and draft stops. Verify that the person approved both stops before any render.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| The pull is refused as a Pro feature | The account is on Free or signed out | Ask the person to run `npx hyperframes billing subscribe --feature templates --skill style-sampling` and pull nothing meanwhile |
| The style is none of the five | The request names a channel or film | Offer `reverse-any-video` or `hyperframes` with `references/look.md` and ask for one example video |
| A paid step is refused | The credit limit would be exceeded | Say what does not fit, ask before dropping it, and run the step again after the person runs the named `billing` command |
