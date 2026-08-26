# Contributing to TerrAgent

Thank you for contributing to TerrAgent! We welcome contributions that adhere to our architectural principles and milestone discipline.

## Development Principles

1. **Milestone Discipline**: We build strictly one milestone at a time (M1 through M6). Do not introduce features from future milestones early.
2. **Layer Separation**: The Reflex layer must remain zero-latency and independent of LLM calls. The Action API must cleanly separate high-level planning from low-level execution.
3. **No Mock/Placeholder Code**: Unimplemented features should raise `NotImplementedError` or be absent, not faked.
4. **Documentation Integrity**: Every module, class, and function must have complete docstrings. Architectural decisions must be recorded in `docs/DECISIONS.md`.

---

## Code Quality Standards

All pull requests must pass the following automated checks:

```powershell
# Linting
ruff check .

# Formatting
ruff format --check .

# Type Checking
mypy agent tests

# Tests
pytest -v
```

---

## Pull Request Workflow

1. Fork the repository and create your branch from `main`.
2. Implement your changes adhering to type safety, docstrings, and tests.
3. Ensure all local tests and static analysis pass cleanly.
4. Update `PROJECT_STATE.md` and `docs/DECISIONS.md` if applicable.
5. Open a Pull Request referencing the relevant issue and milestone.
