/**
 * Parse an author string in various formats into a clean array.
 *
 * Handles:
 * - Newline-separated: "Yaxuan Wang\nHaixia Zhu"
 * - Comma-separated: "Yaxuan Wang, Haixia Zhu"
 * - Python repr: "['Yaxuan Wang', 'Haixia Zhu']"
 * - JSON array: '["Yaxuan Wang", "Haixia Zhu"]'
 * - Single author: "Yaxuan Wang"
 */
export function parseAuthorList(authors: string | null | undefined): string[] {
  if (!authors) return [];

  const trimmed = authors.trim();
  if (!trimmed) return [];

  // Try JSON array: ["Name1", "Name2"]
  if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
    try {
      const parsed = JSON.parse(trimmed);
      if (Array.isArray(parsed))
        return parsed.map((s) => String(s).trim()).filter(Boolean);
    } catch {
      // fall through
    }
    // Try Python list repr: ['Name1', 'Name2']
    const pyMatches = trimmed.match(/'([^']*)'/g);
    if (pyMatches) {
      return pyMatches.map((s) => s.slice(1, -1).trim()).filter(Boolean);
    }
  }

  // Try newline separation
  const byNewline = trimmed
    .split("\n")
    .map((s) => s.trim())
    .filter(Boolean);
  if (byNewline.length > 1) return byNewline;

  // Try comma separation
  const byComma = trimmed
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (byComma.length > 1) return byComma;

  // Single value
  return byNewline.length > 0 ? byNewline : byComma;
}

/**
 * Format an author array into a human-readable display string (comma-separated).
 */
export function displayAuthors(authors: string | null | undefined): string {
  return parseAuthorList(authors).join(", ");
}
