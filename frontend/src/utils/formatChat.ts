export interface ChatSpan { text: string; bold?: boolean; italic?: boolean; code?: boolean }
export interface ChatBlock { type: "heading" | "list" | "paragraph"; marker?: string; spans: ChatSpan[] }

const INLINE_RE = /(`[^`\n]+`|\*\*[^\n]+?\*\*|\*[^\s*\n][^*\n]*?\*)/g;

export function parseInline(raw: string): ChatSpan[] {
  const spans: ChatSpan[] = [];
  let last = 0;
  for (const m of raw.matchAll(INLINE_RE)) {
    const idx = m.index ?? 0;
    if (idx > last) {
      const plain = raw.slice(last, idx).replace(/\*\*/g, "");
      if (plain) spans.push({ text: plain });
    }
    const tok = m[0];
    if (tok.startsWith("`")) spans.push({ text: tok.slice(1, -1), code: true });
    else if (tok.startsWith("**")) spans.push({ text: tok.slice(2, -2).replace(/\*\*/g, ""), bold: true });
    else spans.push({ text: tok.slice(1, -1), italic: true });
    last = idx + tok.length;
  }
  if (last < raw.length) {
    const tail = raw.slice(last).replace(/\*\*/g, "");
    if (tail) spans.push({ text: tail });
  }
  return spans.length ? spans : [{ text: raw.replace(/\*\*/g, "") }];
}

export function formatChatBlocks(content: string): ChatBlock[] {
  const blocks: ChatBlock[] = [];
  let para: string[] = [];
  const flush = () => {
    if (!para.length) return;
    blocks.push({ type: "paragraph", spans: parseInline(para.join("\n")) });
    para = [];
  };
  for (const line of content.replace(/\r\n/g, "\n").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed) { flush(); continue; }
    const h = trimmed.match(/^#{2,6}\s*(.+)$/) || trimmed.match(/^#\s+(.+)$/);
    if (h) {
      flush();
      blocks.push({ type: "heading", spans: parseInline((h[1] || h[2] || "").trim()) });
      continue;
    }
    const bullet = trimmed.match(/^[-*]\s+(.+)$/);
    if (bullet) {
      flush();
      blocks.push({ type: "list", marker: "•", spans: parseInline(bullet[1].trim()) });
      continue;
    }
    const ordered = trimmed.match(/^(\d+\.)\s+(.+)$/);
    if (ordered) {
      flush();
      blocks.push({ type: "list", marker: ordered[1], spans: parseInline(ordered[2].trim()) });
      continue;
    }
    para.push(trimmed);
  }
  flush();
  return blocks;
}
