import { describe, expect, it } from 'vitest'

import { extractJsonContent } from './artistry-json'

describe('extractJsonContent', () => {
  it('extracts JSON from a fenced response', () => {
    expect(extractJsonContent('```json\n{"intensity": 3}\n```')).toBe('{"intensity": 3}')
  })

  it('keeps an unfenced response unchanged', () => {
    expect(extractJsonContent('{"intensity": 3}')).toBe('{"intensity": 3}')
  })

  it('keeps an incomplete fence unchanged', () => {
    expect(extractJsonContent('```json\n{"intensity": 3}')).toBe('```json\n{"intensity": 3}')
  })
})
