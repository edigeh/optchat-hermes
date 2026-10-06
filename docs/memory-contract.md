# Portable memory contract

This contract specifies the OptChat memory behavior used by [the Hermes architecture](architecture.md). Implementations can use it without access to another harness's source or a personal archive.

## Originals and source identity

Each stream contains an ordered sequence of immutable retained records. Canonical record IDs are consecutive integers starting at zero. The retrieval identity is `(stream_id, record_id)`; the same integer in two streams names two different originals.

The legacy OptChat original format is:

```json
{
  "i": 0,
  "kind": "user",
  "text": "Use the fictional Aurora project for this example.",
  "size": 56,
  "date": "2000-01-01T00:00:00.000Z",
  "metadata": {"source": "synthetic-example"}
}
```

Kinds are `user`, `talk`, `tool`, `echo`, and `note`. `size` is the UTF-8 byte length of `kind + ": " + text`, including its prefix. `date` is the original timestamp, not the import time. Optional `payload` names a SHA-256 content-addressed blob. Metadata can preserve origin, native identities, attribution, and import provenance.

Distinct events with identical text remain distinct originals. Idempotency uses a stable source event or command identity, never equal text. A native message copied by compaction retains its logical identity; content edits produce an explicit version/lineage event.

## Binary summary tree

A node `(l, i)` covers the original half-open range:

```text
start = i * 2^l
count = 2^l
end   = start + count
```

Level zero is a summary or direct projection of one original. A node above level zero combines exactly these children:

```text
left  = (l - 1, 2*i)
right = (l - 1, 2*i + 1)
```

The legacy summary format contains `l`, `i`, `text`, and `size`, where `size` is the UTF-8 byte length of `text`. A parent can be published only when both complete children exist and the entire covered original range exists. Completed node contents are immutable within one generation. Track source hashes and supersession/generation separately when corrections change a derived view.

Leaf input preserves the original kind and text; worker-origin content stays attributed to work rather than being relabeled as human instructions. Merge input is the two completed child texts in chronological order. Content within the configured node-byte target can be copied deterministically. Longer input is compressed through a tool-free native auxiliary call. Reject empty or invalid output, and surface exhausted output budgets or missing source capacity as retryable failures. Never truncate an original to manufacture a successful summary.

The historical default node target is 512 bytes. This is a configurable byte target, not a model token limit or a promise that an LLM always obeys the exact requested length. Account for the actual completed node sizes when fitting a view.

## Complete bounded view

A view is an ordered, non-overlapping partition of a committed prefix of the stream. Its parts cover every original in that prefix exactly once. Each part names a completed summary node. Missing nodes may appear as an inspection placeholder but must never enter a model request.

On append, add the level-zero part for the new original. While completed visible-node sizes exceed the byte budget, consider adjacent siblings where:

```text
a.l == b.l
a.i is even
b.i == a.i + 1
their parent is complete
```

For a view covering `total` originals, rank eligible sibling pairs by:

```text
due = (total - a.i * 2^a.l) / 2^(a.l + 2)
```

Merge the pair with the greatest `due`. Ties choose the first pair in chronological view order. Update visible size by subtracting both children and adding the parent's actual size. Repeat until the view fits or no eligible pair exists. Older spans become coarser while recent content stays detailed.

If complete available summaries cannot fit the budget, surface a capacity error or build eligible parents; do not drop a historical range silently. Byte fitting is followed by provider-aware token/capacity validation including framing, native system content, tools, profile, exact state, active messages, attachments, reserved output, and margin.

A rendered historical address uses `start+count`. Text can be flattened to one line for the view while exact retained text remains available through retrieval. The current turn is separate: its triggering input appears once and open assistant/tool-call groups remain intact.

## Exact retrieval

`zoom(stream_id, id, n)` requires an integer `id >= 0`, integer power-of-two `n >= 1`, alignment `id % n == 0`, and a complete range within the stream. Reject boolean values accepted as integers by some languages. Preserve safe-integer compatibility with legacy archives.

- For `n > 1`, return exactly the two addressed child summaries. Missing child summaries produce a clear incomplete-tree result.
- For `n == 1`, return the exact original record. The legacy rendering uses the `id+0` marker for this original leaf.
- Access is validated against the caller's stream/range grant, including each referenced blob.

`date(stream_id, id)` returns the stored original timestamp and a display in the configured timezone. Ordering is canonical record order, not sorting by display date or import time.

`payload(stream_id, hash, offset, length)` validates the SHA-256 address and bounded nonnegative byte offsets. Return base64 bytes, total size, and the next offset so concatenated decoded chunks reconstruct the retained bytes exactly. Verify the blob hash. Reject corrupt blobs, invalid ranges, and unauthorized references.

Search returns cited source ranges. It accelerates access and does not replace full historical coverage or exact operational state.

## Durability and import

Acquire a native OS writer lease before changing an archive. Persist blobs before committing references. Append complete JSONL records and fsync acknowledged writes. A single command journal event can carry atomic input acceptance, attribution, target, and forwarding changes. SQLite projections are rebuildable indexes.

Malformed interior records stop loading with the valid history preserved. A torn final line is retained as recovery evidence and handled explicitly; do not discard corrupt bytes without provenance or pretend an incomplete command was accepted.

Imports preserve original bytes/text, dates, IDs where the destination permits, source origins, payloads, and scope relationships. A populated destination uses origin namespaces and an address map. Repeat imports use source identities and version hashes for idempotency. They cannot collapse distinct equal-text messages.

Backups include the complete committed prefix, required trees, journals, source bindings, effect/result state, and referenced blobs. Hash the manifest and validate restore into a new directory before admitting work. Validate paths and reject symlinks, traversal, unlisted content, corrupt blobs, and inaccessible source grants.

## Corrections, personal facts, and exact state

History, current fact projections, and operational state are different consumers. A user correction supersedes a fact's active influence while retaining its historical source. Retractions and erasure suppression prevent replay from restoring information that should no longer influence recall.

Main, project coordinators, and threads have independent streams and complete views. Context transfer carries source references and explicit read grants. Objectives, constraints, revisions, dependencies, accepted result IDs, budgets, and uncertain-effect status are exact journal-derived state supplied separately from summaries.

## Conformance scenarios

Use synthetic data to defend these observable behaviors:

1. UTF-8 source text and blobs round-trip exactly, including multibyte boundaries and byte-range reconstruction.
2. Equal text under distinct event IDs produces two originals; one redelivered event produces one admission.
3. A view fits through valid sibling merges and still partitions the entire committed prefix without gaps or overlap.
4. Parent construction waits for both children; zoom rejects misalignment, missing coverage, boolean/unsafe numeric inputs, and absent children.
5. A corrupted payload or interior journal line produces a surfaced error; torn-tail recovery retains evidence and does not invent completion.
6. Correction, retraction, audience isolation, and explicit range grants produce distinct active views and authorized retrieval outcomes.
7. Backup/restore retains original timestamps, IDs/source mappings, payload hashes, and project/result references.
8. Restart around an external action parks the uncertain effect for observed-state verification instead of replaying it automatically.
