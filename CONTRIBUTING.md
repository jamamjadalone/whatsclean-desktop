# Contributing to WhatsClean Desktop

Thank you for your interest in contributing to **WhatsClean Desktop**! We welcome community contributions from developers and privacy enthusiasts to help make Windows cleaner, faster, and more private.

---

## Code of Conduct
By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## How Can You Contribute?

### 1. Reporting Bugs
- Check the [Issues tab](https://github.com/jamamjadalone/whatsclean-desktop/issues) to ensure the bug hasn't already been reported.
- Open a new issue using our **Bug Report** template.
- Include:
  - Your Windows version (Windows 10 / Windows 11, Build version).
  - WhatsApp Desktop installation type (Microsoft Store UWP / MSIX vs. Classic installer).
  - Terminal scan output (`python main.py --scan`).

### 2. Suggesting Enhancements
- Open a **Feature Request** issue describing the proposed functionality.
- Note: Our core focus is currently **WhatsApp Desktop** cache reclamation. All additions must adhere to:
  - Zero telemetry (no network calls).
  - 100% offline functionality.
  - Safe Recycle Bin deletion defaults.

### 3. Submitting Pull Requests (PRs)
1. **Fork** the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Keep code clean**:
   - Run Ruff for Python linting:
     ```bash
     python -m ruff check .
     ```
   - Ensure zero syntax errors and clean separation of concerns.
4. **Test empirical functionality**:
   - Verify `python main.py --scan` runs cleanly without crashes.
   - Verify `python main.py --dry-run --clean-safe` behaves as expected.
5. **Commit with conventional messages**:
   ```bash
   git commit -m "feat: add support for custom cache directory path"
   ```
6. **Push and open a PR** against the `main` branch.

---

## Development Setup

### Local Standalone Build
To test compilation into a standalone Windows binary:
```bash
pip install pyinstaller
python build_exe.py
```
Verify that `dist/WhatsClean.exe` launches correctly.

---

## Questions or Ideas?
Feel free to start a discussion in GitHub Issues or contact the maintainer at [jamamjadalone.is-a.dev](https://jamamjadalone.is-a.dev).
