# Workflow Backup e Branch (Migrazione Weebly)

Questo documento definisce il modo in cui lavoriamo per mantenere:

1. `master` stabile (GitHub Pages: solo pagina statica "dominio registrato")
2. backup continuo su GitHub del lavoro di migrazione
3. separazione netta tra "sito live" e "lavoro in corso"

## Regola principale

- `master` resta dedicato al sito live minimale.
- Tutta la migrazione Weebly vive su branch dedicati (esempio: `work/migrazione-weebly`).

## Cosa non fare

- Non fare commit/push della migrazione su `master`.
- Non cambiare workflow Pages su `master` per puntare alla migrazione.

## Cosa fare sempre

1. Creare/usare un branch di lavoro:
   - `git switch -c work/migrazione-weebly` (prima volta)
   - `git switch work/migrazione-weebly` (volte successive)
2. Committare in modo frequente.
3. Pushare il branch su GitHub per backup:
   - `git push -u origin work/migrazione-weebly` (prima volta)
   - `git push` (poi)

## Struttura attuale (WIP)

- Sito live (master): `hugo/`
- Mirror statico locale: `hugo-mirror/`
- Ricostruzione markdown: `hugo-weebly-md/`
- Sorgente mirror: `mirror-source/`
- Script: `scripts/`
- Note/report migrazione: `docs/`

## Comandi operativi utili

Build migrazione markdown:

```bash
./scripts/rebuild-weebly-markdown-site
```

Fidelity check:

```bash
./scripts/check-weebly-fidelity.py
```

Split recensioni:

```bash
./scripts/split-recensioni-pages.py
```

Preview locale migrazione:

```bash
hugo server --source /home/federico/Codex/aburati.github.io/hugo-weebly-md --port 1315 --bind 127.0.0.1
```

## Checklist prima del push del branch di lavoro

1. Build ok (`hugo-weebly-md`).
2. Nessun file temporaneo non desiderato.
3. Commit con messaggio chiaro (pagina/sezione migrata + note QA).

## Quando pubblicare online la migrazione

Solo su tua decisione esplicita:

1. review contenuti completata
2. approvazione finale
3. piano di merge/deploy separato da questo workflow
