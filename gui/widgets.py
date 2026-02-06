"""Custom UI widgets for the TrueKey converter application."""

import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

from gui.styles import COLORS, FONTS, FONT_FAMILY

# Try to import drag and drop support
try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class ModernButton(tk.Canvas):
    """A modern styled button with hover effects."""

    def __init__(self, parent, text, command, primary=True, **kwargs):
        self.width = kwargs.pop('width', 140)
        self.height = kwargs.pop('height', 42)

        super().__init__(
            parent,
            width=self.width,
            height=self.height,
            bg=COLORS['bg'],
            highlightthickness=0,
            **kwargs
        )

        self.command = command
        self.text = text
        self.primary = primary
        self.enabled = True
        self.hovered = False

        self._draw()

        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)

    def _get_color(self):
        if self.primary:
            if not self.enabled:
                return COLORS['primary_disabled']
            if self.hovered:
                return COLORS['primary_hover']
            return COLORS['primary']
        else:
            # Secondary button colors
            if not self.enabled:
                return COLORS['border']
            if self.hovered:
                return COLORS['drop_zone']
            return COLORS['input_bg']

    def _draw(self):
        self.delete('all')
        color = self._get_color()

        # Draw rounded rectangle
        radius = 8
        border_color = COLORS['border'] if not self.primary else ''
        outline_width = 1 if not self.primary else 0
        self.create_round_rect(
            2, 2, self.width - 2, self.height - 2, 
            radius, 
            fill=color, 
            outline=border_color,
            width=outline_width
        )

        # Draw text
        text_color = 'white' if self.primary else COLORS['text']
        self.create_text(
            self.width // 2,
            self.height // 2,
            text=self.text,
            fill=text_color,
            font=FONTS['label']
        )

    def create_round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_enter(self, event):
        if self.enabled:
            self.hovered = True
            self._draw()
            self.config(cursor='hand2')

    def _on_leave(self, event):
        self.hovered = False
        self._draw()
        self.config(cursor='')

    def _on_click(self, event):
        if self.enabled and self.command:
            self.command()

    def set_enabled(self, enabled):
        self.enabled = enabled
        self._draw()
        self.config(cursor='' if not enabled else 'hand2')


class DropZone(tk.Canvas):
    """A drag and drop zone for file input."""

    def __init__(self, parent, on_drop=None, on_click=None, **kwargs):
        self.zone_width = kwargs.pop('width', 400)
        self.zone_height = kwargs.pop('height', 100)

        super().__init__(
            parent,
            width=self.zone_width,
            height=self.zone_height,
            bg=COLORS['card'],
            highlightthickness=0,
            **kwargs
        )

        self.on_drop = on_drop
        self.on_click = on_click
        self.file_path = None
        self.is_hovering = False

        self._draw()

        self.bind('<Button-1>', self._handle_click)
        self.bind('<Enter>', lambda e: self.config(cursor='hand2'))
        self.bind('<Leave>', lambda e: self.config(cursor=''))

        # Set up drag and drop if available
        if DND_AVAILABLE:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<DropEnter>>', self._on_drag_enter)
            self.dnd_bind('<<DropLeave>>', self._on_drag_leave)
            self.dnd_bind('<<Drop>>', self._on_drop)

    def _draw(self):
        self.delete('all')

        # Background
        bg_color = COLORS['drop_zone_active'] if self.is_hovering else COLORS['drop_zone']
        border_color = COLORS['primary'] if self.is_hovering else COLORS['drop_zone_border']

        # Draw rounded rectangle with dashed border
        self._draw_dashed_rounded_rect(
            4, 4, self.zone_width - 4, self.zone_height - 4,
            radius=12,
            fill=bg_color,
            outline=border_color,
            dash=(6, 4)
        )

        if self.file_path:
            # Show file name
            filename = Path(self.file_path).name
            self.create_text(
                self.zone_width // 2,
                self.zone_height // 2 - 8,
                text=filename,
                fill=COLORS['text'],
                font=FONTS['label_bold']
            )
            self.create_text(
                self.zone_width // 2,
                self.zone_height // 2 + 12,
                text="Click to change file",
                fill=COLORS['text_muted'],
                font=FONTS['drop_zone_small']
            )
        else:
            # Show drop instructions
            if DND_AVAILABLE:
                main_text = "Drop CSV file here"
                sub_text = "or click to browse"
            else:
                main_text = "Click to select CSV file"
                sub_text = ""

            self.create_text(
                self.zone_width // 2,
                self.zone_height // 2 - (8 if sub_text else 0),
                text=main_text,
                fill=COLORS['text_secondary'],
                font=FONTS['drop_zone']
            )
            if sub_text:
                self.create_text(
                    self.zone_width // 2,
                    self.zone_height // 2 + 14,
                    text=sub_text,
                    fill=COLORS['text_muted'],
                    font=FONTS['drop_zone_small']
                )

    def _draw_dashed_rounded_rect(self, x1, y1, x2, y2, radius, fill, outline, dash):
        # Fill
        points = self._get_rounded_rect_points(x1, y1, x2, y2, radius)
        self.create_polygon(points, smooth=True, fill=fill, outline='')

        # Dashed border - draw as lines along the rectangle edges
        self._draw_dashed_border(x1, y1, x2, y2, radius, outline, dash)

    def _get_rounded_rect_points(self, x1, y1, x2, y2, radius):
        return [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]

    def _draw_dashed_border(self, x1, y1, x2, y2, radius, color, dash):
        # Top edge
        self.create_line(x1 + radius, y1, x2 - radius, y1, fill=color, dash=dash, width=2)
        # Right edge
        self.create_line(x2, y1 + radius, x2, y2 - radius, fill=color, dash=dash, width=2)
        # Bottom edge
        self.create_line(x2 - radius, y2, x1 + radius, y2, fill=color, dash=dash, width=2)
        # Left edge
        self.create_line(x1, y2 - radius, x1, y1 + radius, fill=color, dash=dash, width=2)

        # Corners (as arcs)
        self.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2,
                       start=90, extent=90, style='arc', outline=color, width=2)
        self.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2,
                       start=0, extent=90, style='arc', outline=color, width=2)
        self.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2,
                       start=270, extent=90, style='arc', outline=color, width=2)
        self.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2,
                       start=180, extent=90, style='arc', outline=color, width=2)

    def _on_drag_enter(self, event):
        self.is_hovering = True
        self._draw()
        return event.action

    def _on_drag_leave(self, event):
        self.is_hovering = False
        self._draw()
        return event.action

    def _on_drop(self, event):
        self.is_hovering = False

        # Parse the dropped file path
        file_path = event.data
        # Handle Windows paths that may be wrapped in braces
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]

        # Only accept CSV files
        if file_path.lower().endswith('.csv'):
            self.set_file(file_path)
            if self.on_drop:
                self.on_drop(file_path)
        else:
            messagebox.showwarning("Invalid File", "Please drop a CSV file.")
            self._draw()

        return event.action

    def _handle_click(self, event):
        if self.on_click:
            self.on_click()

    def set_file(self, filepath):
        self.file_path = filepath
        self._draw()

    def get_file(self):
        return self.file_path


class FileSelector(ttk.Frame):
    """A modern file selector widget."""

    def __init__(self, parent, label_text, on_change=None, save_mode=False, **kwargs):
        super().__init__(parent, **kwargs)

        self.file_path = None
        self.on_change = on_change
        self.save_mode = save_mode

        # Label
        label = ttk.Label(self, text=label_text, font=FONTS['label_bold'])
        label.pack(anchor=tk.W, pady=(0, 6))

        # Container frame
        container = ttk.Frame(self)
        container.pack(fill=tk.X)

        # Path display
        self.path_var = tk.StringVar(value="No file selected")
        self.path_label = ttk.Label(
            container,
            textvariable=self.path_var,
            font=FONTS['label'],
            foreground=COLORS['text_muted'],
            background=COLORS['input_bg'],
            padding=(12, 10),
            anchor=tk.W
        )
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Browse button
        self.browse_btn = ModernButton(
            container,
            text="Browse",
            command=self._browse,
            primary=False,
            width=90,
            height=36
        )
        self.browse_btn.pack(side=tk.RIGHT, padx=(8, 0))

    def _browse(self):
        if self.save_mode:
            filename = filedialog.asksaveasfilename(
                title="Save CSV File",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
        else:
            filename = filedialog.askopenfilename(
                title="Select CSV File",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

        if filename:
            self.set_file(filename)
            if self.on_change:
                self.on_change(filename)

    def set_file(self, filepath):
        self.file_path = filepath
        self.path_var.set(Path(filepath).name)
        self.path_label.configure(foreground=COLORS['text'])

    def get_file(self):
        return self.file_path


class Card(ttk.Frame):
    """A card-style container."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, style='Card.TFrame', **kwargs)


class ModernCombobox(tk.Canvas):
    """A modern styled dropdown/combobox."""

    def __init__(self, parent, values=None, default=None, on_change=None, display_map=None, **kwargs):
        self.width = kwargs.pop('width', 200)
        self.height = kwargs.pop('height', 40)
        
        super().__init__(
            parent,
            width=self.width,
            height=self.height,
            bg=COLORS['card'],
            highlightthickness=0,
            **kwargs
        )
        
        self.values = values or []
        self.display_map = display_map or {}  # Map value -> display text
        self.selected_value = tk.StringVar(value=default if default else (self.values[0] if self.values else ''))
        self.on_change = on_change
        self.is_open = False
        self.dropdown_window = None
        
        self._draw()
        self.bind('<Button-1>', self._toggle_dropdown)
        self.bind('<Enter>', lambda e: self.config(cursor='hand2'))
        self.bind('<Leave>', lambda e: self.config(cursor=''))
    
    def _draw(self):
        """Draw the combobox."""
        self.delete('all')
        
        # Background
        self.create_round_rect(
            2, 2, self.width - 2, self.height - 2,
            radius=8,
            fill=COLORS['input_bg'],
            outline=COLORS['border']
        )
        
        # Selected text - use display map if available
        selected_val = self.selected_value.get()
        display_text = self.display_map.get(selected_val, selected_val)
        self.create_text(
            16, self.height // 2,
            text=display_text,
            fill=COLORS['text'],
            font=FONTS['label'],
            anchor='w'
        )
        
        # Dropdown arrow (chevron down)
        arrow_x = self.width - 24
        arrow_y = self.height // 2
        arrow_size = 8
        
        # Draw a proper chevron using two lines
        # Left side of chevron
        self.create_line(
            arrow_x, arrow_y - 2,
            arrow_x + arrow_size // 2, arrow_y + 3,
            fill=COLORS['text_secondary'],
            width=2,
            capstyle='round'
        )
        # Right side of chevron
        self.create_line(
            arrow_x + arrow_size // 2, arrow_y + 3,
            arrow_x + arrow_size, arrow_y - 2,
            fill=COLORS['text_secondary'],
            width=2,
            capstyle='round'
        )
    
    def create_round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _toggle_dropdown(self, event):
        """Toggle the dropdown menu."""
        if self.is_open:
            self._close_dropdown()
        else:
            self._open_dropdown()
    
    def _open_dropdown(self):
        """Open the dropdown menu."""
        if self.is_open:
            return
        
        self.is_open = True
        
        # Create dropdown window
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.height
        
        self.dropdown_window = tk.Toplevel(self.master)
        self.dropdown_window.withdraw()
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.configure(bg=COLORS['card'])
        
        # Add shadow effect with border
        container = tk.Frame(
            self.dropdown_window,
            bg=COLORS['border'],
            padx=1,
            pady=1
        )
        container.pack(fill=tk.BOTH, expand=True)
        
        inner_frame = tk.Frame(container, bg=COLORS['card'])
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add options
        for value in self.values:
            display_text = self.display_map.get(value, value)
            btn = tk.Label(
                inner_frame,
                text=display_text,
                bg=COLORS['card'],
                fg=COLORS['text'],
                font=FONTS['label'],
                anchor='w',
                padx=16,
                pady=10,
                cursor='hand2'
            )
            btn.pack(fill=tk.X)
            
            # Hover effects
            def on_enter(e, b=btn):
                b.config(bg=COLORS['drop_zone'])
            
            def on_leave(e, b=btn):
                b.config(bg=COLORS['card'])
            
            def on_click(e, v=value):
                self._select_value(v)
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            btn.bind('<Button-1>', on_click)
        
        # Position and show
        self.dropdown_window.update_idletasks()
        dropdown_height = self.dropdown_window.winfo_reqheight()
        self.dropdown_window.geometry(f"{self.width}x{dropdown_height}+{x}+{y}")
        self.dropdown_window.deiconify()
        
        # Bind click outside to close
        self.dropdown_window.bind('<FocusOut>', lambda e: self._close_dropdown())
        self.master.bind_all('<Button-1>', self._check_click_outside, add='+')
    
    def _close_dropdown(self):
        """Close the dropdown menu."""
        if not self.is_open:
            return
        
        self.is_open = False
        if self.dropdown_window:
            self.master.unbind_all('<Button-1>')
            self.dropdown_window.destroy()
            self.dropdown_window = None
    
    def _check_click_outside(self, event):
        """Check if click was outside dropdown."""
        if self.dropdown_window:
            widget = event.widget
            if widget != self and widget != self.dropdown_window and not str(widget).startswith(str(self.dropdown_window)):
                self._close_dropdown()
    
    def _select_value(self, value):
        """Select a value from dropdown."""
        self.selected_value.set(value)
        self._draw()
        self._close_dropdown()
        
        if self.on_change:
            self.on_change(value)
    
    def get(self):
        """Get the selected value."""
        return self.selected_value.get()
    
    def set(self, value):
        """Set the selected value."""
        if value in self.values:
            self.selected_value.set(value)
            self._draw()


class ModernCheckbox(tk.Canvas):
    """A modern styled checkbox."""
    
    def __init__(self, parent, text, variable=None, command=None, **kwargs):
        self.cb_width = kwargs.pop('width', 400)
        self.cb_height = kwargs.pop('height', 32)
        
        super().__init__(
            parent,
            width=self.cb_width,
            height=self.cb_height,
            bg=COLORS['card'],
            highlightthickness=0,
            **kwargs
        )
        
        self.text = text
        self.variable = variable if variable else tk.BooleanVar(value=False)
        self.command = command
        self.hovered = False
        
        self._draw()
        self.bind('<Button-1>', self._toggle)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _draw(self):
        """Draw the checkbox."""
        self.delete('all')
        
        # Checkbox box
        box_size = 20
        box_x = 0
        box_y = (self.cb_height - box_size) // 2
        
        checked = self.variable.get()
        box_color = COLORS['primary'] if checked else COLORS['input_bg']
        border_color = COLORS['primary'] if checked or self.hovered else COLORS['border']
        
        # Draw rounded box
        self.create_round_rect(
            box_x, box_y, box_x + box_size, box_y + box_size,
            radius=4,
            fill=box_color,
            outline=border_color,
            width=2
        )
        
        # Draw checkmark if checked
        if checked:
            # Checkmark
            check_points = [
                box_x + 5, box_y + 10,
                box_x + 8, box_y + 13,
                box_x + 15, box_y + 6
            ]
            self.create_line(
                check_points,
                fill='white',
                width=2,
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND
            )
        
        # Text label
        self.create_text(
            box_size + 12, self.cb_height // 2,
            text=self.text,
            fill=COLORS['text'],
            font=FONTS['label'],
            anchor='w'
        )
    
    def create_round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _toggle(self, event=None):
        """Toggle checkbox state."""
        self.variable.set(not self.variable.get())
        self._draw()
        if self.command:
            self.command()
    
    def _on_enter(self, event):
        """Handle mouse enter."""
        self.hovered = True
        self._draw()
        self.config(cursor='hand2')
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        self.hovered = False
        self._draw()
        self.config(cursor='')
    
    def get(self):
        """Get checkbox value."""
        return self.variable.get()


class HelpTooltip(tk.Canvas):
    """A question mark icon that shows a tooltip on hover."""
    
    def __init__(self, parent, text, **kwargs):
        self.size = kwargs.pop('size', 18)
        
        super().__init__(
            parent,
            width=self.size,
            height=self.size,
            bg=COLORS['card'],
            highlightthickness=0,
            **kwargs
        )
        
        self.tooltip_text = text
        self.tooltip_window = None
        self.hovered = False
        
        self._draw()
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _draw(self):
        """Draw the question mark icon."""
        self.delete('all')
        
        center = self.size // 2
        radius = self.size // 2 - 1
        
        # Circle background
        color = COLORS['primary'] if self.hovered else COLORS['text_muted']
        self.create_oval(
            1, 1, self.size - 1, self.size - 1,
            fill=color,
            outline=''
        )
        
        # Question mark
        self.create_text(
            center, center,
            text='?',
            fill='white',
            font=(FONT_FAMILY, 11, 'bold')
        )
    
    def _on_enter(self, event):
        """Show tooltip on hover."""
        self.hovered = True
        self._draw()
        self.config(cursor='hand2')
        self._show_tooltip()
    
    def _on_leave(self, event):
        """Hide tooltip on leave."""
        self.hovered = False
        self._draw()
        self.config(cursor='')
        self._hide_tooltip()
    
    def _show_tooltip(self):
        """Display the tooltip window."""
        if self.tooltip_window:
            return
        
        # Calculate position
        x = self.winfo_rootx() + self.size + 5
        y = self.winfo_rooty() - 10
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.master)
        self.tooltip_window.withdraw()
        self.tooltip_window.overrideredirect(True)
        self.tooltip_window.configure(bg=COLORS['text'])
        
        # Add padding frame
        padding_frame = tk.Frame(
            self.tooltip_window,
            bg=COLORS['text'],
            padx=2,
            pady=2
        )
        padding_frame.pack()
        
        # Inner frame with rounded appearance
        inner_frame = tk.Frame(
            padding_frame,
            bg=COLORS['text'],
            padx=12,
            pady=8
        )
        inner_frame.pack()
        
        # Tooltip text
        label = tk.Label(
            inner_frame,
            text=self.tooltip_text,
            bg=COLORS['text'],
            fg='white',
            font=FONTS['small'],
            justify=tk.LEFT,
            wraplength=300
        )
        label.pack()
        
        # Position and show
        self.tooltip_window.update_idletasks()
        tooltip_width = self.tooltip_window.winfo_reqwidth()
        tooltip_height = self.tooltip_window.winfo_reqheight()
        
        # Adjust position if tooltip goes off screen
        screen_width = self.winfo_screenwidth()
        if x + tooltip_width > screen_width:
            x = self.winfo_rootx() - tooltip_width - 5
        
        self.tooltip_window.geometry(f"+{x}+{y}")
        self.tooltip_window.deiconify()
    
    def _hide_tooltip(self):
        """Hide the tooltip window."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


