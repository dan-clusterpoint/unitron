/**
 * Assemble the final analysis snapshot.
 *
 * The snapshot follows spec §3.1 and combines the core
 * analysis artifacts produced earlier in the pipeline.
 */

export interface Snapshot {
  profile: unknown;
  digitalScore: number;
  stack: unknown;
  growthTriggers: unknown;
}

export interface BuildSnapshotResult {
  profile: unknown;
  digitalScore: number;
  stack: unknown;
  growthTriggers: unknown;
}

export function buildSnapshot(result: BuildSnapshotResult): Snapshot {
  const {
    profile,
    digitalScore,
    stack,
    growthTriggers,
  } = result;

  return {
    profile,
    digitalScore,
    stack,
    growthTriggers,
  };
}

