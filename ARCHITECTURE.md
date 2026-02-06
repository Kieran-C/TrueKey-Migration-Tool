# Project Architecture

## Overview

The TrueKey Converter is organized into clean, modular components for maintainability and clarity.

## File Structure

```
truekey-to-proton-csv/
├── main.py              # Application entry point (15 lines)
├── converter.py         # CSV conversion logic (286 lines)
├── gui/                 # GUI module
│   ├── __init__.py      # Module exports (5 lines)
│   ├── app.py           # Main application window (521 lines)
│   ├── styles.py        # Colors, fonts, constants (35 lines)
│   └── widgets.py       # Custom UI components (806 lines)
├── icon.ico             # Application icon
├── README.md            # User documentation
└── ARCHITECTURE.md      # This file
```

## Module Responsibilities

### main.py
**Purpose**: Application entry point

**Responsibilities**:
- Initialize the application
- Create the root window
- Start the main event loop

**Key Functions**:
- `main()` - Entry point

---

### converter.py
**Purpose**: CSV conversion business logic

**Responsibilities**:
- Parse TrueKey CSV format
- Handle multi-line notes
- Convert to target password manager formats
- Clean and validate data

**Key Functions**:
- `convert_csv()` - Main conversion function
- `parse_truekey_line()` - Parse individual CSV rows
- `read_csv_with_multiline_notes()` - Handle TrueKey's multi-line format

**Supported Formats**:
- Proton Pass
- LastPass
- 1Password

---

### gui/styles.py
**Purpose**: UI theme and styling constants

**Responsibilities**:
- Define color scheme
- Define font styles
- Define UI constants

**Exports**:
- `COLORS` - Dictionary of color values
- `FONTS` - Dictionary of font configurations
- `FONT_FAMILY` - Default font family
- `DEFAULT_VAULT_NAME` - Default vault name

---

### gui/widgets.py
**Purpose**: Custom UI components

**Responsibilities**:
- Implement modern, custom-styled widgets
- Handle widget-specific logic
- Provide reusable UI components

**Components**:
1. **ModernButton** - Primary/secondary styled buttons
2. **DropZone** - Drag & drop file input area
3. **FileSelector** - File path selector with browse button
4. **Card** - Container with card styling
5. **ModernCombobox** - Styled dropdown menu
6. **ModernCheckbox** - Styled checkbox
7. **HelpTooltip** - Question mark icon with hover tooltip

---

### gui/app.py
**Purpose**: Main application window and logic

**Responsibilities**:
- Create and layout the UI
- Handle user interactions
- Coordinate between UI and converter
- Manage application state

**Key Class**:
- `CSVConverterApp` - Main application window

**Key Methods**:
- `_create_widgets()` - Build the UI
- `_convert()` - Trigger conversion
- `_on_format_change()` - Handle format selection
- `_toggle_notes_export()` - Show/hide notes options
- `_set_app_icon()` - Set custom application icon

**Helper Function**:
- `create_root()` - Create root window with DnD support

---

## Data Flow

```
User Input (TrueKey CSV)
    ↓
[gui/app.py]
    ├─ Validates inputs
    ├─ Collects settings (format, vault, etc.)
    └─ Calls converter
         ↓
    [converter.py]
         ├─ Parses TrueKey format
         ├─ Converts to target format
         └─ Writes output files
              ↓
         Success/Error
              ↓
    [gui/app.py]
         └─ Shows result to user
```

## UI Component Hierarchy

```
Root Window (tk.Tk / TkinterDnD.Tk)
└── CSVConverterApp
    └── Main Container (ttk.Frame)
        ├── Header
        │   ├── Title
        │   └── Subtitle
        │
        ├── Card (Input/Output Section)
        │   ├── Input File Label + HelpTooltip
        │   ├── DropZone
        │   ├── Output Format (ModernCombobox)
        │   ├── Output File (FileSelector)
        │   ├── Options Label
        │   ├── Export Notes (ModernCheckbox)
        │   ├── Notes File (FileSelector) [conditional]
        │   ├── Custom Vault (ModernCheckbox) [Proton only]
        │   └── Vault Entry [conditional]
        │
        ├── Progress Section
        │   ├── Status Label
        │   └── Progress Bar
        │
        ├── Convert Button (ModernButton)
        │
        └── Footer
```

## Design Patterns Used

### Separation of Concerns
- **UI**: `gui/` module
- **Business Logic**: `converter.py`
- **Styling**: `gui/styles.py`
- **Components**: `gui/widgets.py`

### Composition
- Custom widgets composed from basic tkinter widgets
- Application composed from custom widgets

### Callback Pattern
- Widgets accept callback functions for events
- Application methods handle callbacks

### State Management
- Application state stored in `CSVConverterApp` instance
- Widget state managed via tkinter Variables (BooleanVar, StringVar)

## Threading

The application uses threading for the conversion process:

```python
def _convert(self):
    # UI thread - disable button, show progress
    
    def run_conversion():
        # Background thread - perform conversion
        convert_csv(...)
    
    thread = threading.Thread(target=run_conversion, daemon=True)
    thread.start()
```

This keeps the UI responsive during conversion.

## Error Handling

- Try/except blocks in conversion logic
- User-friendly error messages via messagebox
- Graceful fallbacks (icon, DnD support)
- Validation before conversion

## Extensibility

### Adding New Password Managers

1. Update `converter.py`:
   - Add field mappings
   - Add format-specific logic

2. Update `gui/app.py`:
   - Add to format dropdown
   - Add display name
   - Handle format-specific UI (if needed)

### Adding New Features

1. **New Widget**: Add to `gui/widgets.py`
2. **New Style**: Add to `gui/styles.py`
3. **New UI Section**: Modify `gui/app.py`
4. **New Conversion Logic**: Modify `converter.py`

## Dependencies

### Required
- Python 3.7+
- tkinter (built-in)

### Optional
- `tkinterdnd2` - Drag & drop support
- `Pillow` - PNG icon support

## Performance Considerations

- Conversion runs in background thread
- Progress updates throttled (every 10 rows)
- UI updates use `update_idletasks()` sparingly
- Large files handled via streaming (not loaded into memory)
