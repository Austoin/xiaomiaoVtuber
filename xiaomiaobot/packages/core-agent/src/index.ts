export type { AgentContextPort } from './contracts/context-port'
export type { ChatHookRegistry } from './contracts/hook-types'
export type { AgentSessionPort } from './contracts/session-port'

export { createChatHooks } from './runtime/agent-hooks'
export type { ContextHistoryEntry, ContextRegistry } from './runtime/context-registry'
export { createContextRegistry } from './runtime/context-registry'
export { mergeLoadedSessionMessages } from './session/merge-loaded-session-messages'
export type {
  ChatAssistantMessage,
  ChatHistoryItem,
  ChatMessage,
  ChatSlices,
  ChatSlicesText,
  ChatSlicesToolCall,
  ChatSlicesToolCallResult,
  ChatStreamEvent,
  ChatStreamEventContext,
  ContextMessage,
  ErrorMessage,
  StreamingAssistantMessage,
} from './types/chat'
