import { describe, expect, it } from 'vitest'

import { mediaStreamFromAudioFile } from './index'

describe('audio-pipelines-transcribe public entry', () => {
  it('exports the audio file media stream helper', () => {
    expect(mediaStreamFromAudioFile).toBeTypeOf('function')
  })
})
