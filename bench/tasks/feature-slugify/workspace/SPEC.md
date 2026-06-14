# slugify spec

`slugify(title: str, max_length: int = 60) -> str`

1. Transliterate: ä->ae, ö->oe, ü->ue, ß->ss, å->a, é->e, è->e, ñ->n (also their
   uppercase forms, before lowercasing).
2. Lowercase.
3. Every maximal run of characters other than [a-z0-9] becomes a single hyphen.
4. Strip leading/trailing hyphens.
5. If longer than max_length, cut at the last hyphen at or before max_length
   (so no word is cut mid-way); if there is no hyphen in the first max_length
   characters, hard-cut at max_length. Strip any trailing hyphen again.
6. Empty input (or input that reduces to nothing) returns "".
