export interface OverlapToken {
  text: string;
  match: boolean;
}

const normWord = (w: string): string => w.toLowerCase().replace(/[^a-z0-9\u00C0-\u017F]/gi, "");

export function splitOverlapTokens(quote: string, reference: string): OverlapToken[] {
  if (!quote) return [];
  const refWords = new Set(
    (reference || "")
      .split(/\s+/)
      .map(normWord)
      .filter((w) => w.length >= 3),
  );
  return quote.split(/(\s+)/).map((part) => {
    const clean = normWord(part);
    return { text: part, match: clean.length >= 3 && refWords.has(clean) };
  });
}
