# Contributing to Sanskrit Abhidhana

Thank you for your interest in contributing to **Sanskrit Abhidhana**! We welcome contributions, bug reports, documentation updates, performance improvements, and feature enhancements.

---

## 📜 Code of Conduct

By participating in this project, you agree to abide by our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Please report any unacceptable behavior to the project maintainers.

---

## 🛠 Local Development Setup

1. **Fork & Clone Repository**:
   ```bash
   git clone https://github.com/your-username/sanskrit-abhidhana.git
   cd sanskrit-abhidhana
   ```

2. **Create Virtual Environment & Install Dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Build Database Indices**:
   ```bash
   python3 scripts/build_indexes.py
   ```

4. **Run Server Locally**:
   ```bash
   python3 run.py
   ```

5. **Execute Unit Tests**:
   ```bash
   python3 -m unittest discover tests
   ```

---

## 📋 Pull Request Workflow

1. **Branch Naming**: Create a topic branch from `main` using descriptive names (`feature/add-script`, `fix/fts-query-escaping`).
2. **Coding Standards**:
   - Write clear, idiomatic Python code with type annotations.
   - Maintain the RAM RSS limit strictly under **300 MB** and sub-5ms latency SLAs.
   - Separate frontend HTML, CSS, and JS modularly inside `static/`.
3. **Verification**:
   - Ensure all automated unit tests pass before submitting a PR.
4. **Submit PR**: Open a Pull Request on GitHub with a clear description of changes and motivation.
