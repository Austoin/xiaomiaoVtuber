import { describe, expect, it, vi } from 'vitest'

import {
  applyXiaomiaoBridgeReaction,
  applyXiaomiaoStageActionEvents,
  ensureBridgeSpeechReady,
  parseXiaomiaoStageActionEvent,
} from './xiaomiao-bridge-reaction'

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

describe('parseXiaomiaoStageActionEvent', () => {
  it('parses direct xiaomiao stage say events', () => {
    expect(parseXiaomiaoStageActionEvent({
      id: 7,
      event_type: 'stage_action',
      result_summary: 'say',
      content: '桌面小喵播报',
      timestamp: 1780399500,
    })).toEqual({
      id: 7,
      action: 'say',
      text: '桌面小喵播报',
      createdAtMs: 1780399500000,
    })
  })

  it('parses queued xiaomiaobot stage action payloads', () => {
    expect(parseXiaomiaoStageActionEvent({
      id: 8,
      event_type: 'stage_action',
      result_summary: 'stage:say',
      content: JSON.stringify({
        service: 'stage',
        action: 'tts',
        payload: { text: '从队列播报' },
      }),
      timestamp: 1780399501,
    })).toEqual({
      id: 8,
      action: 'tts',
      text: '从队列播报',
      createdAtMs: 1780399501000,
    })
  })

  it('does not pretend unsupported stage actions are executable', () => {
    expect(parseXiaomiaoStageActionEvent({
      id: 9,
      event_type: 'stage_action',
      result_summary: 'unknown-action',
      content: '不支持的动作',
      timestamp: 1780399502,
    })).toBeNull()
  })

  it('parses direct background, model, emotion, and status events', () => {
    expect(parseXiaomiaoStageActionEvent({
      id: 11,
      event_type: 'stage_action',
      result_summary: 'background',
      content: 'builtin:cute-streaming-room',
      timestamp: 1780399504,
    })).toMatchObject({
      id: 11,
      action: 'background',
      backgroundId: 'builtin:cute-streaming-room',
      createdAtMs: 1780399504000,
    })

    expect(parseXiaomiaoStageActionEvent({
      id: 12,
      event_type: 'stage_action',
      result_summary: 'model',
      content: 'preset-vrm-1',
      timestamp: 1780399505,
    })).toMatchObject({
      id: 12,
      action: 'model',
      modelId: 'preset-vrm-1',
    })

    expect(parseXiaomiaoStageActionEvent({
      id: 13,
      event_type: 'stage_action',
      result_summary: 'emotion',
      content: 'happy',
      timestamp: 1780399506,
    })).toMatchObject({
      id: 13,
      action: 'emotion',
      emotionName: 'happy',
      intensity: 1,
    })

    expect(parseXiaomiaoStageActionEvent({
      id: 14,
      event_type: 'stage_action',
      result_summary: 'status',
      content: '',
      timestamp: 1780399507,
    })).toMatchObject({
      id: 14,
      action: 'status',
      query: 'current',
    })
  })

  it('parses structured payloads for non-speech stage actions', () => {
    expect(parseXiaomiaoStageActionEvent({
      id: 15,
      event_type: 'stage_action',
      result_summary: 'stage:emotion',
      content: JSON.stringify({
        service: 'stage',
        action: 'emotion',
        payload: { name: 'curious', intensity: 0.7 },
      }),
      timestamp: 1780399508,
    })).toEqual({
      id: 15,
      action: 'emotion',
      emotionName: 'curious',
      intensity: 0.7,
      createdAtMs: 1780399508000,
    })
  })
})

describe('applyXiaomiaoStageActionEvents', () => {
  it('fans out subtitle stage actions to caption once', async () => {
    const handledEventIds = new Set<number>()
    const postCaption = vi.fn()
    const ensureSpeechReady = vi.fn(async () => {})
    const speakReply = vi.fn(async () => {})
    const events = [{
      id: 10,
      event_type: 'stage_action',
      result_summary: 'subtitle',
      content: '只播一次',
      timestamp: 1780399503,
    }]

    const first = await applyXiaomiaoStageActionEvents({
      events,
      handledEventIds,
      postCaption,
      ensureSpeechReady,
      speakReply,
    })
    const second = await applyXiaomiaoStageActionEvents({
      events,
      handledEventIds,
      postCaption,
      ensureSpeechReady,
      speakReply,
    })

    expect(first.accepted).toHaveLength(1)
    expect(first.rejected).toHaveLength(0)
    expect(second.accepted).toHaveLength(0)
    expect(second.rejected).toHaveLength(0)
    expect(postCaption).toHaveBeenCalledTimes(1)
    expect(postCaption).toHaveBeenCalledWith('只播一次')
    expect(ensureSpeechReady).not.toHaveBeenCalled()
    expect(speakReply).not.toHaveBeenCalled()
  })

  it('dispatches background, model, emotion, and status actions through callbacks', async () => {
    const handledEventIds = new Set<number>()
    const postCaption = vi.fn()
    const speakReply = vi.fn(async () => {})
    const applyBackground = vi.fn(async () => {})
    const applyModel = vi.fn(async () => {})
    const applyEmotion = vi.fn(async () => {})
    const readStatus = vi.fn(async () => '舞台在线：yes')

    const result = await applyXiaomiaoStageActionEvents({
      events: [
        stagePayloadEvent(20, 'background', { id: 'builtin:cozy-tea-corner' }),
        stagePayloadEvent(21, 'model', { id: 'preset-vrm-1' }),
        stagePayloadEvent(22, 'emotion', { name: 'happy', intensity: 0.5 }),
        stagePayloadEvent(23, 'status', { query: 'current' }),
      ],
      handledEventIds,
      postCaption,
      speakReply,
      applyBackground,
      applyModel,
      applyEmotion,
      readStatus,
    })

    expect(result.rejected).toHaveLength(0)
    expect(result.accepted.map(action => action.action)).toEqual(['background', 'model', 'emotion', 'status'])
    expect(applyBackground).toHaveBeenCalledWith('builtin:cozy-tea-corner')
    expect(applyModel).toHaveBeenCalledWith('preset-vrm-1')
    expect(applyEmotion).toHaveBeenCalledWith('happy', 0.5)
    expect(readStatus).toHaveBeenCalledWith('current')
    expect(postCaption).toHaveBeenCalledWith('背景已切换：builtin:cozy-tea-corner')
    expect(postCaption).toHaveBeenCalledWith('模型已切换：preset-vrm-1')
    expect(postCaption).toHaveBeenCalledWith('舞台在线：yes')
    expect(speakReply).not.toHaveBeenCalled()
  })

  it('rejects unsupported stage actions visibly and marks them handled', async () => {
    const handledEventIds = new Set<number>()
    const onRejected = vi.fn()

    const result = await applyXiaomiaoStageActionEvents({
      events: [{
        id: 24,
        event_type: 'stage_action',
        result_summary: 'stage:unsupported',
        content: JSON.stringify({
          service: 'stage',
          action: 'unsupported',
          payload: { id: 'x' },
        }),
        timestamp: 1780399509,
      }],
      handledEventIds,
      postCaption: vi.fn(),
      speakReply: vi.fn(async () => {}),
      onRejected,
    })

    expect(result.accepted).toHaveLength(0)
    expect(result.rejected).toEqual([{
      id: 24,
      action: 'unsupported',
      reason: '无法解析或不支持的舞台动作',
    }])
    expect(onRejected).toHaveBeenCalledWith(result.rejected[0])
    expect(handledEventIds.has(24)).toBe(true)
  })
})

function stagePayloadEvent(id: number, action: string, payload: Record<string, unknown>) {
  return {
    id,
    event_type: 'stage_action',
    result_summary: `stage:${action}`,
    content: JSON.stringify({
      service: 'stage',
      action,
      payload,
    }),
    timestamp: 1780399500 + id,
  }
}
