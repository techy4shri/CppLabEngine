# CppLab IDE - Roadmap & TODO

## Current Status: v1.1 Standalone Mode Complete ✓

The IDE now supports both project-based and standalone file workflows:
- ✓ Full project system with .cpplab.json configuration
- ✓ Standalone source file mode (compile single .c/.cpp files)
- ✓ Toolchain selection logic (mingw32 for graphics, mingw64 for console)
- ✓ Build system with proper compiler flags
- ✓ Graphics.h support (32-bit, with all required libraries)
- ✓ OpenMP support (64-bit)
- ✓ Syntax highlighting and code editor
- ✓ Build output panel with error display
- ✓ Run executables in separate console window

## Phase 1: Core Features (v1.0) - COMPLETE ✓

### Completed ✓
- [x] Project data model (ProjectConfig)
- [x] Toolchain management (mingw32, mingw64)
- [x] Build system (compile + run)
- [x] Main window UI with dock-based layout
- [x] Code editor with C++ syntax highlighting
- [x] Project explorer tree
- [x] New project dialog with type selection
- [x] Build output panel
- [x] File save/save all
- [x] Graphics.h support with proper linking (-lole32, -loleaut32)
- [x] OpenMP support
- [x] Project type templates (Console, Graphics, OpenMP)
- [x] **Standalone source file mode** - New in v1.1!
- [x] Open Source File action (Ctrl+Shift+O)
- [x] Build single .c/.cpp files without projects
- [x] Auto-detect language from extension
- [x] Build output in file's directory
- [x] Run standalone executables
- [x] Build and Run workflow for both modes
- [x] Proper status bar updates
- [x] UI state management (enable/disable actions)

### Testing Status
- [x] Test with MinGW toolchains (both 32-bit and 64-bit)
- [x] Test graphics.h project build and linking
- [x] Test standalone file compilation
- [ ] Test OpenMP project end-to-end
- [ ] Test mixed console+graphics project
- [ ] Verify DLL loading in run environment
- [ ] Test all keyboard shortcuts

## Phase 2: Essential Features (v1.2) - In Progress

### Project Management
- [ ] Add existing file to project
- [ ] Create new file in project
- [ ] Remove file from project
- [ ] Rename files
- [ ] Project settings dialog
- [ ] Recent projects list

### Editor Improvements
- [ ] Line numbers
- [ ] Code folding
- [ ] Find and replace
- [ ] Go to line
- [ ] Undo/redo in menu
- [ ] Copy/cut/paste in menu

### Build System
- [ ] Clean build output
- [ ] Rebuild (clean + build)
- [ ] Build configurations (Debug/Release)
- [ ] Custom compiler flags in project settings
- [ ] Incremental builds (only changed files)

### UI Polish
- [ ] Toolbar with common actions
- [ ] Status bar with file info
- [ ] Better error highlighting in editor
- [ ] Build progress indicator
- [ ] Tab icons for file types

## Phase 3: Advanced Features (v1.2)

### Code Intelligence
- [ ] Auto-completion (QScintilla integration)
- [ ] Function/class navigation
- [ ] Symbol search
- [ ] Code snippets library
- [ ] Header/source file switching

### Debugging
- [ ] GDB integration
- [ ] Breakpoints
- [ ] Step through code
- [ ] Variable inspection
- [ ] Call stack view

### Documentation
- [ ] Offline C++ reference browser
- [ ] Function lookup (hover or F1)
- [ ] Code examples database
- [ ] Tutorial system

### Templates
- [ ] Project templates library
- [ ] SDL2 template
- [ ] OpenGL template
- [ ] Console game template
- [ ] Data structures template

## Phase 4: Professional Features (v2.0)

### Version Control
- [ ] Git integration
- [ ] Commit/push/pull UI
- [ ] Diff viewer
- [ ] Branch management

### Customization
- [ ] Theme system
- [ ] Editor color schemes
- [ ] Custom keyboard shortcuts
- [ ] Font selection
- [ ] UI layout persistence

### Collaboration
- [ ] Export project as zip
- [ ] Import project from zip
- [ ] Code sharing snippets
- [ ] Assignment submission tool

### Advanced Tools
- [ ] Profiler integration
- [ ] Memory leak detector
- [ ] Static analysis (cppcheck)
- [ ] Code formatter (clang-format)

## Phase 5: Platform & Ecosystem (v2.5)

### Cross-Platform
- [ ] Linux support
- [ ] macOS support (if feasible)
- [ ] GCC toolchain support

### Extensions
- [ ] Plugin system
- [ ] Extension API
- [ ] Community extension marketplace

### Cloud Integration (Optional)
- [ ] Cloud save for projects
- [ ] Online code sharing
- [ ] Collaboration features

## Known Issues & Bugs

### High Priority
- [ ] Need to verify toolchain PATH handling on different Windows versions
- [ ] Test with non-ASCII characters in project paths
- [ ] Handle missing toolchain gracefully

### Medium Priority
- [ ] Editor doesn't show modified indicator in tab
- [ ] No confirmation on exit with unsaved files
- [ ] Build thread blocks UI briefly

### Low Priority
- [ ] Syntax highlighting could be more comprehensive
- [ ] Output panel doesn't auto-scroll in all cases
- [ ] No dark theme support yet

## Technical Debt

### Refactoring Needed
- [ ] Move UI logic out of app.py into separate controllers
- [ ] Create proper service layer for build operations
- [ ] Add type hints throughout codebase
- [ ] Unit tests for core modules
- [ ] Integration tests for build system

### Documentation
- [ ] API documentation (docstrings)
- [ ] Architecture diagrams
- [ ] Video tutorials
- [ ] User manual

### Performance
- [ ] Lazy load large projects
- [ ] Background indexing for code intelligence
- [ ] Cache build artifacts
- [ ] Optimize syntax highlighting for large files

## Packaging & Distribution

### Installer
- [ ] NSIS installer script
- [ ] Inno Setup script
- [ ] Include MinGW in installer
- [ ] Desktop shortcut creation
- [ ] File association (.cpplab.json)

### Distribution Channels
- [ ] GitHub releases
- [ ] Website with downloads
- [ ] Portable USB version
- [ ] Silent install for lab deployment

## Community & Support

### Documentation
- [ ] Wiki on GitHub
- [ ] FAQ page
- [ ] Common issues guide
- [ ] Video tutorials

### Support
- [ ] Issue templates on GitHub
- [ ] Discussion forum
- [ ] Email support
- [ ] Feature request process

## Success Metrics

### v1.0 Goals
- [ ] Successfully create and build all project types
- [ ] Graphics.h projects work out of box
- [ ] OpenMP projects compile with proper flags
- [ ] Stable enough for daily use

### v2.0 Goals
- [ ] Used in at least one college lab
- [ ] Positive user feedback
- [ ] < 5 critical bugs
- [ ] Feature-complete for basic C++ education

## Long-Term Vision

Create a comprehensive C++ learning environment that:
- Works offline in resource-constrained labs
- Supports both legacy (graphics.h) and modern (C++20) code
- Provides excellent educational tools
- Remains simple and focused
- Can be easily deployed and maintained

## Contributing

See CONTRIBUTING.md for:
- How to contribute
- Coding standards
- Pull request process
- Development setup
