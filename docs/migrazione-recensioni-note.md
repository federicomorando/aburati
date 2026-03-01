# Operational Notes - Reviews Migration

## Current status

Split into individual posts:

- Piemonte
- Giapponesi in Piemonte
- Nord Italia
- Sud Italia (initial manual conversion)
- Estero

## Required manual checks

1. Piemonte: `#credenza` and `#belvedere` exist in the index but no matching content blocks are present in the available source.
2. Review each post text, punctuation, and formatting against source pages.
3. Keep tags in Italian and aligned with original naming (location, region, cuisine type).
4. Decide whether historical references (for example, "Visitato nel 2010") should stay in body text only or also be normalized into dedicated metadata.

## Script used

- `scripts/split-recensioni-pages.py`
