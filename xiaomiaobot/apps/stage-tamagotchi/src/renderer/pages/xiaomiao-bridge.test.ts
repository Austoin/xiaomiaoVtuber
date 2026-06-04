import { describe, expect, it, vi } from 'vitest'

import { readXiaomiaoBridgeState, shouldAdoptXiaomiaoBridgeState } from './xiaomiao-bridge'

describe('readXiaomiaoBridgeState', () => {
  it('returns reply text from a successful bridge response', async () => {
    const fetcher = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        reply_text: '桌面桥接成功',
        timestamp: 1777425310,
        user_id: 3554978979,
      }),
    })

    const result = await readXiaomiaoBridgeState(fetcher, 3554978979)

    expect(fetcher).toHaveBeenCalledWith('http://127.0.0.1:5519/v1/xiaomiao/state?user_id=3554978979')
    expect(result).toEqual({
      replyText: '桌面桥接成功',
      timestamp: 1777425310,
      userId: 3554978979,
    })
  })

  it('returns null when the bridge response is not ok', async () => {
    const fetcher = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({ reply_text: 'ignored', timestamp: 1, user_id: 1 }),
    })

    const result = await readXiaomiaoBridgeState(fetcher, 3554978979)

    expect(result).toBeNull()
  })

  it('returns null when reply text is empty', async () => {
    const fetcher = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        reply_text: '   ',
        timestamp: 1777425310,
        user_id: 3554978979,
      }),
    })

    const result = await readXiaomiaoBridgeState(fetcher, 3554978979)

    expect(result).toBeNull()
  })
})

describe('shouldAdoptXiaomiaoBridgeState', () => {
  it('adopts newer bridge timestamps', () => {
    expect(shouldAdoptXiaomiaoBridgeState(1777425300, 1777425310, '旧消息', '新消息')).toBe(true)
  })

  it('adopts changed text even when timestamps match', () => {
    expect(shouldAdoptXiaomiaoBridgeState(1777425310, 1777425310, '旧消息', '新消息')).toBe(true)
  })

  it('ignores duplicate timestamp and text', () => {
    expect(shouldAdoptXiaomiaoBridgeState(1777425310, 1777425310, '同一条', '同一条')).toBe(false)
  })
})
