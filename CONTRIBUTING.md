# Contributing to CppLab IDE

Thank you for your interest in contributing to CppLab IDE! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites
- Python 3.13+
- PyQt6
- Git
- MinGW toolchains (for testing)

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/CppLabEngine.git
   cd CppLabEngine
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run tests to verify setup:
   ```bash
   python test_setup.py
   ```

5. Launch the IDE:
   ```bash
   python -m cpplab.main
   ```

## Code Style

### Python Code
- Follow PEP 8 with the following modifications:
  - Line length: 100 characters (not 79)
  - Use 4 spaces for indentation
  - No emojis in code or comments

### Comments
We prefer minimal, clear comments:

```python
# File-level comment: brief module description

class MyClass:
    # Class-level: what this class does
    
    def my_method(self):
        # Inside: only where helpful
        result = compute()  # Brief inline note if needed
```

### Naming Conventions
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Private methods**: `_leading_underscore`
- **Constants**: `UPPER_SNAKE_CASE`
- **Files**: `snake_case.py`

## Project Structure

```
src/cpplab/
├── main.py              # Entry point
├── app.py               # Main window controller
├── dialogs.py           # Dialog implementations
├── ui/                  # Qt Designer .ui files
├── widgets/             # Custom Qt widgets
└── core/                # Business logic (no Qt)
    ├── project_config.py
    ├── toolchains.py
    ├── builder.py
    └── docs.py
```

**Important**: Keep Qt code out of `core/` modules. The core should be GUI-agnostic.

## Making Changes

### Branch Naming
- Feature: `feature/short-description`
- Bug fix: `fix/issue-number-description`
- Documentation: `docs/what-you-changed`

Examples:
- `feature/add-line-numbers`
- `fix/123-graphics-path-issue`
- `docs/update-quickstart`

### Commit Messages
Use conventional commits format:

```
type(scope): brief description

Longer explanation if needed.

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(editor): add line numbers to code editor

fix(builder): correct PATH handling for 32-bit toolchain

docs(readme): update installation instructions
```

### Testing Your Changes

1. Run the test script:
   ```bash
   python test_setup.py
   ```

2. Manual testing checklist:
   - [ ] Create new console project → builds and runs
   - [ ] Create graphics project → builds and runs
   - [ ] Create OpenMP project → builds and runs
   - [ ] Open existing project → loads correctly
   - [ ] Save and reload → no data loss
   - [ ] UI is responsive, no crashes

3. If you added new features, test:
   - Normal workflow
   - Edge cases
   - Error conditions

## Pull Request Process

1. **Update your fork**:
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Make your changes** following style guidelines

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/my-feature
   ```

6. **Create Pull Request** on GitHub:
   - Clear title and description
   - Reference any related issues
   - Explain what changed and why
   - Include screenshots for UI changes

### PR Checklist
- [ ] Code follows style guidelines
- [ ] Comments are minimal and clear
- [ ] No unnecessary files included
- [ ] Tested manually
- [ ] No breaking changes (or clearly documented)
- [ ] Updated relevant documentation

## Types of Contributions

### Bug Reports
Use the issue template with:
- Clear title
- Steps to reproduce
- Expected vs actual behavior
- System info (Windows version, Python version)
- Screenshots if applicable

### Feature Requests
Open an issue with:
- Problem you're trying to solve
- Proposed solution
- Alternative solutions considered
- Impact on existing features

### Code Contributions

**Easy First Issues**:
- Documentation improvements
- UI polish (colors, spacing, icons)
- Additional code templates
- Error message improvements

**Medium Difficulty**:
- New project templates
- Editor enhancements
- Build system improvements
- UI features from TODO.md

**Advanced**:
- Debugger integration
- Code intelligence
- Plugin system
- Cross-platform support

## Documentation

### Code Documentation
- Add docstrings to public classes and functions
- Keep docstrings concise
- Focus on "what" and "why", not "how"

```python
def build_project(project_config: ProjectConfig) -> BuildResult:
    """
    Compile the project using the appropriate toolchain.
    
    Args:
        project_config: Project configuration
        
    Returns:
        BuildResult with success status and output
    """
```

### User Documentation
- Update README.md for feature changes
- Update QUICKSTART.md for workflow changes
- Update DEVELOPMENT.md for architecture changes
- Add examples where helpful

## Code Review Process

1. Maintainer reviews PR within 1 week
2. Address review comments
3. Once approved, maintainer merges
4. PR is automatically closed

### Review Criteria
- Code quality and style
- Functionality and correctness
- Performance impact
- Documentation completeness
- Test coverage

## Community Guidelines

### Be Respectful
- Constructive feedback only
- Assume good intentions
- Help newcomers
- Be patient with questions

### Be Collaborative
- Discuss major changes before implementing
- Accept feedback gracefully
- Give credit where due
- Share knowledge

### Be Professional
- No harassment or discrimination
- Keep discussions on-topic
- Respect maintainer decisions
- Follow code of conduct

## Getting Help

### Resources
- README.md - Project overview
- QUICKSTART.md - Getting started
- DEVELOPMENT.md - Architecture details
- TODO.md - Roadmap and tasks

### Support Channels
- GitHub Issues - Bug reports and features
- GitHub Discussions - General questions
- Email - Private concerns

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- GitHub contributors page
- Release notes

Thank you for contributing to CppLab IDE!
