const EYE_SACCADE_INTERVAL_STEP_MS = 400
const EYE_SACCADE_INTERVAL_DISTRIBUTION = [
  [0.075, 800],
  [0.110, 0],
  [0.125, 0],
  [0.140, 0],
  [0.125, 0],
  [0.050, 0],
  [0.040, 0],
  [0.030, 0],
  [0.020, 0],
  [1.000, 0],
] as Array<[number, number]>

for (let i = 1; i < EYE_SACCADE_INTERVAL_DISTRIBUTION.length; i++) {
  EYE_SACCADE_INTERVAL_DISTRIBUTION[i][0] += EYE_SACCADE_INTERVAL_DISTRIBUTION[i - 1][0]
  EYE_SACCADE_INTERVAL_DISTRIBUTION[i][1] = EYE_SACCADE_INTERVAL_DISTRIBUTION[i - 1][1] + EYE_SACCADE_INTERVAL_STEP_MS
}

/**
 * Generate a random interval between eye saccades.
 *
 * @returns Interval in milliseconds.
 */
export function randomSaccadeInterval(): number {
  const randomValue = Math.random()

  for (const [probabilityUpperBound, intervalOffset] of EYE_SACCADE_INTERVAL_DISTRIBUTION) {
    if (randomValue <= probabilityUpperBound) {
      return intervalOffset + Math.random() * EYE_SACCADE_INTERVAL_STEP_MS
    }
  }

  const [, fallbackIntervalOffset] = EYE_SACCADE_INTERVAL_DISTRIBUTION.at(-1)!
  return fallbackIntervalOffset + Math.random() * EYE_SACCADE_INTERVAL_STEP_MS
}
