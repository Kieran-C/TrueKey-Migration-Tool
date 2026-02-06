"""Main application window for the TrueKey converter."""

import threading
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

from converter import convert_csv
from gui.styles import COLORS, FONTS, DEFAULT_VAULT_NAME
from gui.widgets import (
    ModernButton, DropZone, FileSelector, Card,
    ModernCombobox, ModernCheckbox, HelpTooltip, DND_AVAILABLE
)

# Try to import drag and drop support
try:
    from tkinterdnd2 import TkinterDnD
except ImportError:
    TkinterDnD = None


class CSVConverterApp:
    """Main application window for the CSV converter."""

    def __init__(self, root):
        self.root = root
        self.root.title("TrueKey Migration Tool")
        self.root.geometry("520x840")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS['bg'])
        
        # Set custom icon
        self._set_app_icon()

        self.use_custom_vault = tk.BooleanVar(value=False)
        self.export_notes = tk.BooleanVar(value=False)

        self._setup_styles()
        self._create_widgets()
    
    def _set_app_icon(self):
        """Set the application icon."""
        try:
            # Try to load icon.ico or icon.png from the same directory
            from pathlib import Path
            script_dir = Path(__file__).parent
            
            # Try .ico first (Windows native format)
            ico_path = script_dir / "icon.ico"
            if ico_path.exists():
                self.root.iconbitmap(str(ico_path))
                return
            
            # Try .png format
            png_path = script_dir / "icon.png"
            if png_path.exists():
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(png_path)
                    photo = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, photo)
                    return
                except ImportError:
                    pass  # PIL not available
            
            # Create a simple programmatic icon as fallback
            self._create_default_icon()
            
        except Exception as e:
            print(f"Could not set icon: {e}")
            # Continue without icon if there's an error
    
    def _create_default_icon(self):
        """Create a simple default icon programmatically."""
        try:
            # Create a small PhotoImage icon (key symbol)
            icon_size = 32
            icon = tk.PhotoImage(width=icon_size, height=icon_size)
            
            # Fill with primary color background
            primary_color = COLORS['primary']
            # Convert hex to rgb
            r = int(primary_color[1:3], 16)
            g = int(primary_color[3:5], 16)
            b = int(primary_color[5:7], 16)
            
            # Fill background
            for x in range(icon_size):
                for y in range(icon_size):
                    # Create a circular background
                    dx = x - icon_size // 2
                    dy = y - icon_size // 2
                    if dx * dx + dy * dy < (icon_size // 2) ** 2:
                        icon.put(f'#{r:02x}{g:02x}{b:02x}', (x, y))
            
            # Draw a simple key shape in white
            white = '#ffffff'
            # Key circle (top)
            for x in range(10, 18):
                for y in range(8, 16):
                    dx = x - 14
                    dy = y - 12
                    if 9 < dx * dx + dy * dy < 25:
                        icon.put(white, (x, y))
            
            # Key shaft (vertical line)
            for y in range(12, 24):
                icon.put(white, (14, y))
                icon.put(white, (15, y))
            
            # Key teeth
            for x in range(12, 18, 2):
                icon.put(white, (x, 22))
                icon.put(white, (x, 23))
            
            self.root.iconphoto(True, icon)
        except Exception as e:
            print(f"Could not create default icon: {e}")

    def _setup_styles(self):
        """Configure ttk styles for a modern look."""
        style = ttk.Style()
        style.theme_use('clam')

        # Frame styles
        style.configure('TFrame', background=COLORS['bg'])
        style.configure('Card.TFrame', background=COLORS['card'])

        # Label styles
        style.configure('TLabel', background=COLORS['bg'], foreground=COLORS['text'])
        style.configure('Card.TLabel', background=COLORS['card'])
        style.configure('Title.TLabel', font=FONTS['title'], foreground=COLORS['text'])
        style.configure('Subtitle.TLabel', font=FONTS['subtitle'], foreground=COLORS['text_secondary'])
        style.configure('Status.TLabel', font=FONTS['small'], foreground=COLORS['text_muted'])

        # Checkbutton styles
        style.configure(
            'TCheckbutton',
            background=COLORS['bg'],
            foreground=COLORS['text'],
            font=FONTS['label']
        )
        style.configure(
            'Card.TCheckbutton',
            background=COLORS['card'],
            foreground=COLORS['text'],
            font=FONTS['label']
        )

        # Entry styles
        style.configure('TEntry', padding=10)
        style.map('TEntry',
            fieldbackground=[('disabled', COLORS['border']), ('!disabled', COLORS['input_bg'])],
        )

        # Button styles
        style.configure(
            'Secondary.TButton',
            font=FONTS['label'],
            padding=(16, 8),
        )

        # Progressbar
        style.configure(
            'TProgressbar',
            background=COLORS['primary'],
            troughcolor=COLORS['border'],
            thickness=6
        )

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container with padding
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Header
        self._create_header(main_container)

        # Main card
        card = Card(main_container, padding=20)
        card.pack(fill=tk.X, pady=(16, 0))

        # Input file section with drop zone
        input_label_frame = ttk.Frame(card, style='Card.TFrame')
        input_label_frame.pack(anchor=tk.W, pady=(0, 8))
        
        input_label = ttk.Label(
            input_label_frame,
            text="Input File (TrueKey Export)",
            font=FONTS['label_bold'],
            style='Card.TLabel'
        )
        input_label.pack(side=tk.LEFT)
        
        # Add help tooltip
        help_tooltip = HelpTooltip(
            input_label_frame,
            text="In TrueKey, go to Settings → App Settings → Export Data\nClick continue and enter master password\nSave the CSV to your computer",
            size=16
        )
        help_tooltip.pack(side=tk.LEFT, padx=(6, 0))

        self.drop_zone = DropZone(
            card,
            on_drop=self._on_input_change,
            on_click=self._browse_input,
            width=424,
            height=90
        )
        self.drop_zone.pack(pady=(0, 12))

        # Format selection (moved before output file)
        format_label = ttk.Label(
            card,
            text="Output Format",
            font=FONTS['label_bold'],
            style='Card.TLabel'
        )
        format_label.pack(anchor=tk.W, pady=(0, 6))

        format_frame = ttk.Frame(card, style='Card.TFrame')
        format_frame.pack(fill=tk.X, pady=(0, 12))

        self.format_combo = ModernCombobox(
            format_frame,
            values=['proton', 'lastpass', '1password'],
            default='proton',
            display_map={
                'proton': 'Proton Pass',
                'lastpass': 'LastPass',
                '1password': '1Password'
            },
            on_change=lambda v: self._on_format_change(),
            width=180,
            height=42
        )
        self.format_combo.pack(side=tk.LEFT)

        format_desc = ttk.Label(
            format_frame,
            text="Choose target password manager",
            font=FONTS['small'],
            foreground=COLORS['text_muted'],
            style='Card.TLabel'
        )
        format_desc.pack(side=tk.LEFT, padx=(12, 0))

        # Output file selector (moved after format)
        self.output_selector = FileSelector(
            card,
            "Output File (Logins)",
            on_change=self._on_file_change,
            save_mode=True
        )
        self.output_selector.pack(fill=tk.X, pady=(0, 12))

        # Separator
        ttk.Separator(card, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        # Options section
        options_label = ttk.Label(card, text="Options", font=FONTS['label_bold'], style='Card.TLabel')
        options_label.pack(anchor=tk.W, pady=(8, 12))

        # Export notes checkbox
        self.export_notes_cb = ModernCheckbox(
            card,
            text="Export notes to separate file",
            variable=self.export_notes,
            command=self._toggle_notes_export,
            width=424
        )
        self.export_notes_cb.pack(anchor=tk.W)

        # Notes file selector (hidden initially)
        self.notes_selector = FileSelector(
            card,
            "Output File (Notes)",
            on_change=self._on_file_change,
            save_mode=True
        )

        # Store reference to card for later use
        self.card = card

        # Custom vault checkbox
        self.vault_cb = ModernCheckbox(
            card,
            text="Use custom vault name (default: \"Personal\")",
            variable=self.use_custom_vault,
            command=self._toggle_vault_entry,
            width=424
        )
        # Don't pack initially - let _on_format_change() handle it

        # Vault entry frame (hidden initially)
        self.vault_frame = ttk.Frame(card, style='Card.TFrame')

        vault_label = ttk.Label(
            self.vault_frame,
            text="Vault name:",
            font=FONTS['small'],
            style='Card.TLabel'
        )
        vault_label.pack(side=tk.LEFT)

        self.vault_entry = ttk.Entry(self.vault_frame, font=FONTS['label'], state='disabled')
        self.vault_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        self.vault_entry.insert(0, DEFAULT_VAULT_NAME)
        
        # Initialize vault visibility based on default format
        self._on_format_change()

        # Progress section
        progress_frame = ttk.Frame(main_container)
        progress_frame.pack(fill=tk.X, pady=(18, 0))

        self.status_label = ttk.Label(
            progress_frame,
            text="Drop a file or click to browse",
            style='Status.TLabel'
        )
        self.status_label.pack()

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.pack(pady=(8, 0), fill=tk.X)

        # Convert button
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=(18, 0))

        self.convert_button = ModernButton(
            button_frame,
            text="Convert",
            command=self._convert,
            width=160,
            height=46
        )
        self.convert_button.pack()
        self.convert_button.set_enabled(False)

        # Footer
        footer_text = "Converts TrueKey CSV exports to Proton Pass, LastPass, or 1Password"
        if DND_AVAILABLE:
            footer_text += " | Drag & drop enabled"
        footer = ttk.Label(
            main_container,
            text=footer_text,
            style='Status.TLabel'
        )
        footer.pack(pady=(16, 0))

    def _create_header(self, parent):
        """Create the header section."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X)

        title = ttk.Label(
            header_frame,
            text="TrueKey Migration Tool",
            style='Title.TLabel'
        )
        title.pack(anchor=tk.W)

        subtitle = ttk.Label(
            header_frame,
            text="Export to Proton Pass, LastPass, or 1Password",
            style='Subtitle.TLabel'
        )
        subtitle.pack(anchor=tk.W, pady=(4, 0))

    def _browse_input(self):
        """Open file browser for input file."""
        filename = filedialog.askopenfilename(
            title="Select Input CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.drop_zone.set_file(filename)
            self._on_input_change(filename)

    def _on_input_change(self, filepath):
        """Handle input file selection."""
        # Auto-suggest output filenames
        input_path = Path(filepath)

        if not self.output_selector.get_file():
            suggested_output = input_path.parent / f"{input_path.stem}_converted_logins.csv"
            self.output_selector.set_file(str(suggested_output))

        if self.export_notes.get() and not self.notes_selector.get_file():
            suggested_notes = input_path.parent / f"{input_path.stem}_converted_notes.csv"
            self.notes_selector.set_file(str(suggested_notes))

        self._check_ready()

    def _on_file_change(self, filepath):
        """Handle file selection changes."""
        self._check_ready()

    def _toggle_notes_export(self):
        """Show or hide the notes file selector."""
        if self.export_notes.get():
            self.notes_selector.pack(fill=tk.X, pady=(12, 0), after=self.export_notes_cb)

            # Auto-suggest notes filename
            input_file = self.drop_zone.get_file()
            if input_file and not self.notes_selector.get_file():
                input_path = Path(input_file)
                suggested_notes = input_path.parent / f"{input_path.stem}_notes.csv"
                self.notes_selector.set_file(str(suggested_notes))
        else:
            self.notes_selector.pack_forget()
        
        # Reposition vault options to maintain correct order
        self._on_format_change()

        self._check_ready()

    def _on_format_change(self, event=None):
        """Handle format selection change."""
        format_selected = self.format_combo.get()
        
        # Always unpack first to ensure correct ordering
        self.vault_cb.pack_forget()
        self.vault_frame.pack_forget()
        
        # Only show vault options for Proton Pass
        if format_selected == 'proton':
            # Pack after notes selector if export notes is checked, otherwise after export notes checkbox
            # Use checkbox state instead of winfo_ismapped() to avoid timing issues
            if self.export_notes.get():
                after_widget = self.notes_selector
            else:
                after_widget = self.export_notes_cb
            
            self.vault_cb.pack(anchor=tk.W, pady=(8, 0), after=after_widget)
            # Only show vault_frame if checkbox is ticked
            if self.use_custom_vault.get():
                self.vault_frame.pack(fill=tk.X, pady=(8, 0), padx=(24, 0), after=self.vault_cb)
    
    def _toggle_vault_entry(self):
        """Show/hide and enable/disable the vault name entry."""
        if self.use_custom_vault.get():
            # Show the vault entry frame and enable the entry
            self.vault_frame.pack(fill=tk.X, pady=(8, 0), padx=(24, 0), after=self.vault_cb)
            self.vault_entry.config(state='normal')
            self.vault_entry.focus()
            self.vault_entry.select_range(0, tk.END)
        else:
            # Hide the vault entry frame
            self.vault_frame.pack_forget()
            self.vault_entry.config(state='disabled')

    def _get_vault_name(self) -> str:
        """Get the vault name to use."""
        if self.use_custom_vault.get():
            custom_name = self.vault_entry.get().strip()
            return custom_name if custom_name else DEFAULT_VAULT_NAME
        return DEFAULT_VAULT_NAME

    def _check_ready(self):
        """Check if all required files are selected."""
        input_ok = self.drop_zone.get_file() is not None
        output_ok = self.output_selector.get_file() is not None
        notes_ok = not self.export_notes.get() or self.notes_selector.get_file() is not None

        ready = input_ok and output_ok and notes_ok
        self.convert_button.set_enabled(ready)

        if ready:
            self.status_label.config(text="Ready to convert", foreground=COLORS['text_secondary'])
        else:
            self.status_label.config(text="Drop a file or click to browse", foreground=COLORS['text_muted'])

    def _update_progress(self, message: str):
        """Update the progress label."""
        self.status_label.config(text=message, foreground=COLORS['primary'])
        self.root.update_idletasks()

    def _show_result(self, result: dict):
        """Display the conversion result."""
        self.progress_bar.stop()
        self.convert_button.set_enabled(True)

        if result['success']:
            message = (
                f"Conversion completed!\n\n"
                f"Total rows: {result['total_rows']}\n"
                f"Logins: {result['login_rows']}\n"
            )

            if result['notes_file']:
                message += f"Notes: {result['note_rows']}\n"

            message += (
                f"Passwords cleaned: {result['password_cleaned']}\n"
                f"Rows with issues: {result['problem_count']}"
            )

            messagebox.showinfo("Success", message)
            self.status_label.config(text="Conversion complete!", foreground=COLORS['success'])
        else:
            messagebox.showerror("Error", f"Conversion failed:\n{result['error']}")
            self.status_label.config(text="Conversion failed", foreground=COLORS['error'])

    def _convert(self):
        """Start the CSV conversion."""
        self.convert_button.set_enabled(False)
        self.status_label.config(text="Converting...", foreground=COLORS['primary'])
        self.progress_bar.start(10)

        vault_name = self._get_vault_name()
        export_notes = self.export_notes.get()
        output_format = self.format_combo.get()

        def run_conversion():
            convert_csv(
                self.drop_zone.get_file(),
                self.output_selector.get_file(),
                self.notes_selector.get_file(),
                vault_name,
                export_notes,
                progress_callback=self._update_progress,
                result_callback=self._show_result,
                output_format=output_format
            )

        thread = threading.Thread(target=run_conversion, daemon=True)
        thread.start()


def create_root():
    """Create the root window with drag and drop support if available."""
    if DND_AVAILABLE:
        return TkinterDnD.Tk()
    else:
        return tk.Tk()
