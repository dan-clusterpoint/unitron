/**
 * Assemble the final analysis snapshot.
 *
 * The snapshot follows spec §3.1 and combines the core
 * analysis artifacts produced earlier in the pipeline.
 */

export interface Snapshot {
  profile: unknown;
  digitalScore: number;
  risk: unknown;
  stackDelta: unknown;
  growthTriggers: unknown;
  nextActions: unknown;
}

export interface BuildSnapshotResult {
  profile: unknown;
  digitalScore: number;
  risk: unknown;
  stackDelta: unknown;
  growthTriggers: unknown;
  nextActions: unknown;
}

export function buildSnapshot(result: BuildSnapshotResult): Snapshot {
  const {
    profile,
    digitalScore,
    risk,
    stackDelta,
    growthTriggers,
    nextActions,
  } = result;

  return {
    profile,
    digitalScore,
    risk,
    stackDelta,
    growthTriggers,
    nextActions,
  };
}

