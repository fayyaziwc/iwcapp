# AI App Builder Tool (Codex-style Workflow)

This repo provides a lightweight CLI tool that turns plain-English requirements into a structured app build plan.

It is inspired by the workflow described in the referenced Instagram reel:
- provide requirements
- automatically produce a feature set
- generate an implementation plan

## What it does

Given your app idea, it generates:
1. `product_requirements.md` (problem, users, goals, constraints)
2. `features.json` (feature list with priority and acceptance criteria)
3. `implementation_plan.md` (milestones and delivery plan)

## Quick start

```bash
python tool/app_builder.py generate \
  --name "Lead Capture Assistant" \
  --requirements "A web app that captures leads from forms, scores them, and emails daily summaries." \
  --out ./output/lead-assistant
```

## Commands

### Generate project artifacts

```bash
python tool/app_builder.py generate --name "My App" --requirements "..." --out ./output/my-app
```

### Use a requirements file

```bash
python tool/app_builder.py generate --name "My App" --requirements-file ./requirements.txt --out ./output/my-app
```

### Print to console only

```bash
python tool/app_builder.py generate --name "My App" --requirements "..." --stdout
```

## Notes

- No external dependencies required.
- Heuristic feature extraction is deterministic and easy to customize.
- If you want, this can be extended to call the OpenAI API for richer planning and code generation.
