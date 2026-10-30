# Claude Code Instructions (GTA 5 RP Suite & Mirror Legislation)

This repository provides agentic tools, skills, and the full legislative and judicial database for the GTA 5 RP **Mirror** server.

## Commands / Triggers
Activate Module 3 (`gta5rp-mirror-legislation`) whenever the user starts a prompt with:
- `/mirror-law <prompt>`
- `/mirror <prompt>`
- `/gta-law <prompt>`
or asks to analyze laws, arrests, searches, court claims, or GTA 5 RP mod mechanics.

## Modules Overview
- `gta5rp-forum-navigation/`: XenForo 2.3 parser, hidden spoiler/quote expander, media extractor (Imgur, Yapx, YouTube, Google Docs/Sheets).
- `gta5rp-forum-documents/`: Court claim audit, SLA tracker (24h/72h/96h), fee/passport checks, MetaGaming detector.
- `gta5rp-mirror-legislation/`: Complete Mirror legislation (34 laws/codes), Supreme Court precedents (`LEP-№1`), OOC overrides, game mechanics.

## Quick CLI Search (Zero Hallucination)
Always verify article numbers and sanctions before answering:
```bash
python gta5rp-mirror-legislation/scripts/search_mirror_law.py --law УК --article 17.6
python gta5rp-mirror-legislation/scripts/search_mirror_law.py --law ПК --article 15.1
python gta5rp-mirror-legislation/scripts/search_mirror_law.py --law "взаимодействие" --article 8.1
python gta5rp-mirror-legislation/scripts/search_mirror_law.py --precedents --query "LEP-1"
python gta5rp-mirror-legislation/scripts/search_mirror_law.py --ooc --query "штурм"
```

## Key Server Rules & Conventions
1. OOC server rules always override IC legislation in case of conflict.
2. Supreme Court Precedent `LEP-№1`: continuous video record, 2 demands + 10s wait for art. 17.6 УК; ticket + 20s wait for art. 17.7 p. 3 УК.
3. State employees on duty can only be detained for violent/felony crimes explicitly listed in art. 8 of Law on Law Enforcement Interaction (never on the spot for art. 15.1 / 15.6).
4. Only DB (LSPD/LSSD) and CID (FIB) may write raid case files. Only MP (NG) may patrol for deserters.
5. In-game mechanics: Handcuffs (`X`), Escort (`Z`), WANTED tag in Green Zones without mask, SP secret identity, 180° bodycam from 24/7, virtual parking protection.
