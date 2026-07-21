/**
 * Extracts the JSON payload from an optional Markdown code fence.
 *
 * The parser uses delimiters instead of a backtracking regular expression so
 * large model responses remain linear to scan even when a closing fence is
 * missing.
 *
 * @param rawContent - Raw text returned by the Director model.
 * @returns Trimmed fenced content, or the original text when no complete fence exists.
 */
export function extractJsonContent(rawContent: string): string {
  const openingFence = rawContent.indexOf('```')
  if (openingFence < 0)
    return rawContent

  const contentStart = openingFence + 3
  const closingFence = rawContent.indexOf('```', contentStart)
  if (closingFence < 0)
    return rawContent

  const languageStart = rawContent.slice(contentStart, contentStart + 4)
  const payloadStart = languageStart === 'json' ? contentStart + 4 : contentStart
  return rawContent.slice(payloadStart, closingFence).trim()
}
