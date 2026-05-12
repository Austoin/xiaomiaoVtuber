import { describe, expect, it, vi } from 'vitest'

import { applyXiaomiaoBridgeReaction, ensureBridgeSpeechReady } from './xiaomiao-bridge-reaction'

describe('ensureBridgeSpeechReady', () => {
  it('configures kokoro-local when bridge speech is still noop', async () => {
    const applyConfig = vi.fn()

    const changed = await ensureBridgeSpeechReady({
      currentProvider: 'speech-noop',
      currentModel: '',
      currentVoiceId: '',
      providerConfigModel: 'q4f16',
      loadVoices: async () => [{ id: 'zf_xiaoyi', languages: [{ code: 'zh-CN' }] }],
      applyConfig,
    })

    expect(changed).toBe(true)
    expect(applyConfig).toHaveBeenCalledWith({
      providerId: 'kokoro-local',
      modelId: 'q4f16',
      voice: { id: 'zf_xiaoyi', languages: [{ code: 'zh-CN' }] },
    })
  })

  it('prefers official Kokoro Mandarin voices over fallback English voices', async () => {
    const applyConfig = vi.fn()

    await ensureBridgeSpeechReady({
      currentProvider: 'speech-noop',
      currentModel: '',
      currentVoiceId: '',
      providerConfigModel: 'q4f16',
      loadVoices: async () => [
        { id: 'af_heart', languages: [{ code: 'en-US' }] },
        { id: 'zf_xiaobei', languages: [{ code: 'zh-CN' }] },
      ],
      applyConfig,
    })

    expect(applyConfig).toHaveBeenCalledWith({
      providerId: 'kokoro-local',
      modelId: 'q4f16',
      voice: { id: 'zf_xiaobei', languages: [{ code: 'zh-CN' }] },
    })
  })

  it('does nothing when an actual speech provider is already active', async () => {
    const applyConfig = vi.fn()

    const changed = await ensureBridgeSpeechReady({
      currentProvider: 'kokoro-local',
      currentModel: 'q4f16',
      currentVoiceId: 'af_heart',
      providerConfigModel: 'q4f16',
      loadVoices: async () => [{ id: 'af_heart', languages: [{ code: 'en-US' }] }],
      applyConfig,
    })

    expect(changed).toBe(false)
    expect(applyConfig).not.toHaveBeenCalled()
  })
})

describe('applyXiaomiaoBridgeReaction', () => {
  /**
   * @example
   * await applyXiaomiaoBridgeReaction({ currentTimestamp: 0, currentText: '', bridgeState, ...handlers })
   */
  it('fans out fresh bridge replies to caption, chat history, and speech', async () => {
    const postCaption = vi.fn()
    const syncChatHistory = vi.fn()
    const ensureSpeechReady = vi.fn(async () => {})
    const speakReply = vi.fn(async () => {})

    const result = await applyXiaomiaoBridgeReaction({
      currentTimestamp: 0,
      currentText: '',
      bridgeState: {
        replyText: '桥接回复',
        timestamp: 123,
        userId: 1,
      },
      postCaption,
      syncChatHistory,
      ensureSpeechReady,
      speakReply,
    })

    expect(postCaption).toHaveBeenCalledWith('桥接回复')
    expect(syncChatHistory).toHaveBeenCalledWith('桥接回复', 123000)
    expect(ensureSpeechReady).toHaveBeenCalledTimes(1)
    expect(speakReply).toHaveBeenCalledWith('桥接回复')
    expect(result).toEqual({
      accepted: true,
      nextTimestamp: 123,
      nextText: '桥接回复',
    })
  })

  /**
   * @example
   * const result = await applyXiaomiaoBridgeReaction({ currentTimestamp: 123, currentText: 'same', bridgeState: sameState, ...handlers })
   */
  it('ignores duplicate bridge replies so speech is not replayed', async () => {
    const postCaption = vi.fn()
    const syncChatHistory = vi.fn()
    const ensureSpeechReady = vi.fn(async () => {})
    const speakReply = vi.fn(async () => {})

    const result = await applyXiaomiaoBridgeReaction({
      currentTimestamp: 123,
      currentText: 'same',
      bridgeState: {
        replyText: 'same',
        timestamp: 123,
        userId: 1,
      },
      postCaption,
      syncChatHistory,
      ensureSpeechReady,
      speakReply,
    })

    expect(postCaption).not.toHaveBeenCalled()
    expect(syncChatHistory).not.toHaveBeenCalled()
    expect(ensureSpeechReady).not.toHaveBeenCalled()
    expect(speakReply).not.toHaveBeenCalled()
    expect(result).toEqual({
      accepted: false,
      nextTimestamp: 123,
      nextText: 'same',
    })
  })
})
