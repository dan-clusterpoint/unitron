import { buildSnapshot, BuildSnapshotResult, Snapshot } from '../../analyze/buildSnapshot';

export interface AnalyzeResponse {
  snapshot: Snapshot;
}

/**
 * Analyze the supplied artifacts and assemble a final snapshot.
 *
 * The handler expects the request body to match `BuildSnapshotResult`
 * and returns the resulting snapshot inside a JSON object.
 */
export async function analyze(body: BuildSnapshotResult): Promise<AnalyzeResponse> {
  const snapshot = buildSnapshot(body);
  return { snapshot };
}
