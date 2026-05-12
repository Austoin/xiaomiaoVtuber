import type { ChatHistoryItem } from '@proj-airi/stage-ui/types/chat'

/**
 * Appends a XiaoMiao bridge assistant reply to session history.
 *
 * Use when:
 * - the desktop bridge reports a fresh QQ-originated assistant reply
 * - the renderer needs to mirror that reply into the current chat session
 *
 * Expects:
 * - `messages` is the current persisted session history in display order
 * - `replyText` already comes from the trusted local XiaoMiao bridge payload
 *
 * Returns:
 * - a new history array with one assistant message appended when the reply is new
 * - the original history array when the reply is empty or already matches the tail
 */
export function appendBridgeAssistantReply(
  messages: ChatHistoryItem[],
  replyText: string,
  createdAt: number,
): ChatHistoryItem[] {
  const normalizedReply = replyText.trim()
  if (!normalizedReply) {
    return messages
  }

  const lastMessage = messages.at(-1)
  if (lastMessage?.role === 'assistant' && lastMessage.content === normalizedReply) {
    return messages
  }

  return [
    ...messages,
    {
      id: `xiaomiao-${createdAt.toString(36)}`,
      role: 'assistant',
      content: normalizedReply,
      slices: [],
      tool_results: [],
      createdAt,
    },
  ]
}
