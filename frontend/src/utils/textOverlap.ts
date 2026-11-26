export interface OverlapToken {
  text: string;
  match: boolean;
}

const STOPWORDS = new Set([
  "dan", "atau", "yang", "untuk", "dengan", "pada", "dari", "dalam", "oleh",
  "sebagai", "serta", "terhadap", "adalah", "ini", "itu", "agar", "karena",
  "sehingga", "bahwa", "dapat", "akan", "telah", "juga", "antara", "secara",
  "the", "and", "for", "with", "that", "this", "from", "into", "are", "was",
  "were", "been", "have", "has", "not", "but", "such", "their", "these",
]);

const normWord = (w: string): string => w.toLowerCase().replace(/[^a-z0-9\u00C0-\u017F]/gi, "");
const isContentWord = (w: string): boolean => w.length >= 3 && !STOPWORDS.has(w);

export function splitOverlapTokens(quote: string, reference: string): OverlapToken[] {
  if (!quote) return [];
  const refWords = new Set(
    (reference || "")
      .split(/\s+/)
      .map(normWord)
      .filter(isContentWord),
  );
  return quote.split(/(\s+)/).map((part) => {
    const clean = normWord(part);
    return { text: part, match: isContentWord(clean) && refWords.has(clean) };
  });
}
