# Claude maintenance instructions

Read and follow `AGENTS.md` as the canonical maintenance instructions for this repository. Read `README.md` for source layout and deployment steps.

Routine content updates go in `content/*.json`. Do not edit generated HTML in `dist/`. Run:

```bash
python3 build.py
python3 scripts/check_site.py
```

Keep the site static, accessible, and dependency-free. Do not infer student or publication facts. Follow the owner's instructions for committing and deploying.
