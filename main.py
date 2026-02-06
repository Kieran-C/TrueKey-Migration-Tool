"""TrueKey to Proton Pass CSV Converter - Entry point."""

from gui import CSVConverterApp, create_root


def main():
    """Launch the CSV converter application."""
    root = create_root()
    CSVConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
