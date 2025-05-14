# ADR Numbering process

## Status

Proposed after some conversation between @lassulus, @Mic92, & @lopter.

## Context

It can be useful to refer to ADRs by their numbers, rather than their full title. To that end, short and sequential numbers are useful.

The issue is that an ADR number is effectively assigned when the ADR is merged, before being merged its number is provisional. Because multiple ADRs can be written at the same time, you end-up with multiple provisional ADRs with the same number, for example this is the third ADR-3:

1. ADR-3-clan-compat: see [#3212];
2. ADR-3-fetching-nix-from-python: see [#3452];
3. ADR-3-numbering-process: this ADR.

This situation makes it impossible to refer to an ADR by its number, and why I (@lopter) went with the arbitrary number 7 in [#3196].

We could solve this problem by using the PR number as the ADR number (@lassulus). The issue is that PR numbers are getting big in clan-core which does not make them easy to remember, or use in conversation and code (@lopter).

Another approach would be to move the ADRs in a different repository, this would reset the counter back to 1, and make it straightforward to keep ADR and PR numbers in sync (@lopter). The issue then is that ADR are not in context with their changes which makes them more difficult to review (@Mic92).

## Decision

A third approach would be to:

1. Commit ADRs before they are approved, so that the next ADR number gets assigned;
1. Open a PR for the proposed ADR;
1. Update the ADR file committed in step 1, so that its markdown contents point to the PR that tracks it.

## Consequences

### ADR have unique and memorable numbers trough their entire life cycle

This makes it easier to refer to them in conversation or in code.

### You need to have commit access to get an ADR number assigned

This makes it more difficult for someone external to the project to contribute an ADR.

### Creating a new ADR requires multiple commits

Maybe a script or CI flow could help with that if it becomes painful.

[#3212]: https://git.clan.lol/clan/clan-core/pulls/3212/
[#3452]: https://git.clan.lol/clan/clan-core/pulls/3452/
[#3196]: https://git.clan.lol/clan/clan-core/pulls/3196/
