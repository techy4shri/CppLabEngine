# Toolchain and Standard Selection Feature

## Overview
Added explicit toolchain (32-bit/64-bit MinGW) and C/C++ standard selection dropdowns to the main toolbar, giving users manual control over build settings while maintaining intelligent defaults.

## User Interface

### Toolchain Selection ComboBox
- **Location**: Main toolbar
- **Options**:
  - Auto (default) - Automatically selects based on project features
  - 64-bit (mingw64) - Forces 64-bit toolchain
  - 32-bit (mingw32) - Forces 32-bit toolchain
- **Behavior**:
  - Graphics projects ALWAYS use 32-bit toolchain (forced, regardless of selection)
  - Other projects respect user selection
  - Defaults to "Auto" for new projects

### Standard Selection ComboBox
- **Location**: Main toolbar (next to toolchain)
- **Options**: Dynamically populated based on language:
  - **C Projects**: C11 (default), C17
  - **C++ Projects**: C++11, C++14, C++17 (default), C++20
- **Behavior**:
  - Changes persist to project configuration
  - Standalone files use per-file settings

## Implementation Details

### Backend Changes

#### 1. `src/cpplab/core/project_config.py`
- Added `toolchain_preference: str = "auto"` field to `ProjectConfig` dataclass
- Updated `to_dict()` and `from_dict()` to include `toolchain_preference`
- New projects default to `toolchain_preference="auto"`

#### 2. `src/cpplab/core/toolchains.py`
- Updated `select_toolchain()` function:
  ```python
  def select_toolchain(project_config: ProjectConfig, available_toolchains: dict) -> Toolchain:
      # Graphics projects ALWAYS use mingw32 (forced)
      if project_config.graphics:
          return available_toolchains["mingw32"]
      
      # Check toolchain preference
      pref = project_config.toolchain_preference
      if pref == "mingw64" and "mingw64" in available_toolchains:
          return available_toolchains["mingw64"]
      elif pref == "mingw32" and "mingw32" in available_toolchains:
          return available_toolchains["mingw32"]
      
      # Auto selection (default behavior)
      if project_config.openmp and "mingw64" in available_toolchains:
          return available_toolchains["mingw64"]
      return next(iter(available_toolchains.values()))
  ```

#### 3. `src/cpplab/core/builder.py`
- Updated standalone file functions to accept overrides:
  - `project_config_for_single_file(source_path, standard_override=None, toolchain_preference="auto")`
  - `build_single_file(source_path, toolchains, standard_override=None, toolchain_preference="auto")`
  - `run_single_file(source_path, toolchains, standard_override=None, toolchain_preference="auto")`

### Frontend Changes

#### 4. `src/cpplab/ui/MainWindow.ui`
- Added `toolchainComboBox` to main toolbar with label "Toolchain:"
- Added `standardComboBox` to main toolbar with label "Standard:"

#### 5. `src/cpplab/app.py`
- Added state tracking:
  - `self.standalone_toolchain_preference = "auto"` - Tracks toolchain for standalone files
  - `self.standalone_standard: Optional[str] = None` - Tracks standard for standalone files

- Added helper methods:
  - `_setup_combo_boxes()` - Initializes combo box items
  - `_update_standard_combo_for_language(language, current_standard)` - Populates standard combo based on C/C++
  - `_update_toolchain_combo(current_preference)` - Syncs toolchain combo with current setting

- Added signal handlers:
  - `on_toolchain_changed(index)` - Updates project config or standalone preference
  - `on_standard_changed(index)` - Updates project config or standalone standard

- Updated project/file loading:
  - `set_current_project()` - Syncs combo boxes with project settings
  - `on_open_source_file()` - Syncs combo boxes with standalone settings

- Updated build/run methods:
  - Standalone builds pass `standard_override` and `toolchain_preference` to builder functions

## Usage

### For Projects
1. Open or create a project
2. Select desired toolchain from dropdown (graphics projects ignore this, always use 32-bit)
3. Select desired C/C++ standard from dropdown
4. Changes automatically save to `.cpplab.json`
5. Build/run uses selected settings

### For Standalone Files
1. Open a source file (Ctrl+Shift+O)
2. Select desired toolchain from dropdown
3. Select desired C/C++ standard from dropdown
4. Changes persist for current session (per-file basis)
5. Build/run uses selected settings

## Examples

### Example 1: Force 64-bit Build for Non-Graphics Project
1. Open project
2. Change toolchain dropdown to "64-bit"
3. Build → Uses mingw64 compiler

### Example 2: Use C++20 Features
1. Open C++ project or file
2. Change standard dropdown to "C++20"
3. Build → Uses `-std=c++20` flag

### Example 3: Graphics Project (Forced 32-bit)
1. Open graphics project (uses BGI/winbgim)
2. Try changing toolchain dropdown to "64-bit"
3. Build → STILL uses mingw32 (forced for graphics compatibility)

## Technical Notes

### Graphics Override Behavior
The toolchain selection dropdown is **advisory only** for graphics projects. The system ALWAYS forces mingw32 for graphics because:
- BGI/winbgim libraries are 32-bit only
- Attempting 64-bit builds will fail with linker errors

### Standard Defaults
- **C projects**: Default to C11 (widely supported)
- **C++ projects**: Default to C++17 (modern, stable)

### Persistence
- **Project mode**: Settings saved to `.cpplab.json` in project root
- **Standalone mode**: Settings stored in memory for current session only

## Testing Checklist

- [x] UI combo boxes appear in toolbar
- [x] Toolchain combo populates with Auto/64-bit/32-bit
- [x] Standard combo populates correctly for C/C++
- [ ] Opening project syncs combo boxes with project settings
- [ ] Opening standalone file syncs combo boxes with defaults
- [ ] Changing toolchain saves to project config
- [ ] Changing standard saves to project config
- [ ] Standalone mode uses selected settings for build/run
- [ ] Graphics projects always use mingw32 regardless of dropdown
- [ ] Build commands include correct `-std=` flag
- [ ] Settings persist across IDE restarts (projects only)

## Future Enhancements

1. **Visual Indicator for Forced Settings**: Show icon or tooltip when graphics override is active
2. **More Standards**: Add C99, C++23 when compiler support improves
3. **Persistent Standalone Settings**: Save standalone preferences to user config file
4. **Warning Dialog**: Alert user when trying to select 64-bit for graphics project
