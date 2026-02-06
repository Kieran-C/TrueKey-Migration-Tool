"""CSV conversion logic for TrueKey to Proton Pass format."""

import csv
import re
from pathlib import Path
from typing import Callable, Optional


def read_csv_with_multiline_notes(file_handle) -> list[str]:
    """
    Read CSV file handling multi-line notes.

    Notes can span multiple lines until we hit tk-csv-v2.
    Assumes file handle is already positioned after the header.
    """
    rows = []
    current_line = None

    for line in file_handle:
        line = line.rstrip('\n\r')

        if not line.strip():
            continue

        if current_line is not None:
            current_line += '\n' + line

            if line.endswith('tk-csv-v2'):
                rows.append(current_line)
                current_line = None
        else:
            if line.endswith('tk-csv-v2'):
                rows.append(line)
            else:
                current_line = line

    return rows


def parse_truekey_line(line: str, fieldnames: list[str]) -> dict:
    """Parse a TrueKey CSV line into a dictionary."""
    parts = line.split(',')

    if parts[0].lower() == 'note':
        return _parse_note_line(parts)
    else:
        return _parse_login_line(parts, fieldnames)


def _parse_note_line(parts: list[str]) -> dict:
    """Parse a note entry from TrueKey CSV."""
    if parts[-1] == 'tk-csv-v2':
        parts = parts[:-1]

    name = ''
    name_index = -1
    for i in range(len(parts) - 1, 0, -1):
        if parts[i].strip():
            name = parts[i].strip()
            name_index = i
            break

    content_parts = []
    if name_index > 8:
        content_parts = parts[8:name_index]
    elif name_index == -1 and len(parts) > 8:
        content_parts = parts[8:]

    filtered_content = []
    for p in content_parts:
        if p.strip() and p.strip() not in ['e3622b', '14766677']:
            if not p.strip().isdigit():
                filtered_content.append(p)

    content = '\n'.join(filtered_content)

    return {'kind': 'note', 'name': name, 'content': content}


def _parse_login_line(parts: list[str], fieldnames: list[str]) -> dict:
    """Parse a login entry from TrueKey CSV."""
    # Remove tk-csv-v2 marker if present
    if parts and parts[-1] == 'tk-csv-v2':
        parts = parts[:-1]
    
    # Remove trailing empty fields
    while parts and parts[-1] == '':
        parts = parts[:-1]
    
    num_fields = len(fieldnames)

    if len(parts) < num_fields:
        parts.extend([''] * (num_fields - len(parts)))
    elif len(parts) > num_fields:
        last_field = parts[-1]
        first_field = parts[0]
        middle_parts = parts[1:-1]
        fields_needed = num_fields - 2

        if len(middle_parts) > fields_needed:
            password_idx = fieldnames.index('password') if 'password' in fieldnames else -1

            if password_idx > 0:
                before_password = middle_parts[:password_idx - 1]
                after_password_count = fields_needed - password_idx
                after_password = middle_parts[-(after_password_count):] if after_password_count > 0 else []
                password_parts = middle_parts[
                    password_idx - 1:-(after_password_count) if after_password_count > 0 else len(middle_parts)
                ]
                password_value = ','.join(password_parts)
                parts = [first_field] + before_password + [password_value] + after_password + [last_field]
            else:
                parts = [first_field] + middle_parts[:fields_needed] + [last_field]
        else:
            parts = [first_field] + middle_parts + [last_field]

    return dict(zip(fieldnames, parts[:num_fields]))


def convert_csv(
    input_file: str,
    output_file: str,
    notes_file: Optional[str],
    vault_name: str,
    export_notes: bool,
    progress_callback: Optional[Callable[[str], None]] = None,
    result_callback: Optional[Callable[[dict], None]] = None,
    output_format: str = 'proton'
) -> dict:
    """
    Convert CSV from TrueKey format to password manager format.

    Args:
        input_file: Path to the TrueKey CSV export
        output_file: Path for the converted logins CSV
        notes_file: Path for the notes CSV (if exporting notes)
        vault_name: Name of the vault to assign entries to
        export_notes: Whether to export notes to a separate file
        progress_callback: Optional callback for progress updates
        result_callback: Optional callback for the final result
        output_format: Output format ('proton', 'lastpass', or '1password')

    Returns:
        Dictionary with conversion results
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            header_line = infile.readline().strip()
            fieldnames = header_line.split(',')
            rows = read_csv_with_multiline_notes(infile)

        # Define output fields based on format
        if output_format == 'lastpass':
            output_fieldnames = ['url', 'username', 'password', 'extra', 'name', 'grouping', 'fav', 'totp']
        elif output_format == '1password':
            output_fieldnames = ['name', 'url', 'username', 'password']
        else:  # proton
            output_fieldnames = ['name', 'url', 'email', 'username', 'password', 'note', 'totp', 'vault']

        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames, quoting=csv.QUOTE_ALL)
            # 1Password has no header row
            if output_format != '1password':
                writer.writeheader()

            notes_writer = None
            notesfile = None
            if export_notes and notes_file:
                notesfile = open(notes_file, 'w', encoding='utf-8', newline='')
                # Define notes fields based on format
                if output_format == 'lastpass':
                    notes_fieldnames = ['url', 'username', 'password', 'extra', 'name', 'grouping', 'fav']
                elif output_format == '1password':
                    notes_fieldnames = ['name', 'content']
                else:  # proton
                    notes_fieldnames = ['name', 'content']
                notes_writer = csv.DictWriter(notesfile, fieldnames=notes_fieldnames, quoting=csv.QUOTE_ALL)
                # 1Password has no header row
                if output_format != '1password':
                    notes_writer.writeheader()

            try:
                stats = _process_rows(
                    rows, fieldnames, writer, notes_writer,
                    vault_name, export_notes, progress_callback, output_format
                )
            finally:
                if notesfile:
                    notesfile.close()

        result = {
            'success': True,
            'total_rows': stats['total_rows'],
            'login_rows': stats['login_rows'],
            'note_rows': stats['note_rows'],
            'password_cleaned': stats['password_cleaned'],
            'problem_count': stats['problem_count'],
            'output_file': output_file,
            'notes_file': notes_file if export_notes else None
        }

        if result_callback:
            result_callback(result)

        return result

    except Exception as e:
        result = {'success': False, 'error': str(e)}
        if result_callback:
            result_callback(result)
        return result


def _process_rows(
    rows: list[str],
    fieldnames: list[str],
    writer: csv.DictWriter,
    notes_writer: Optional[csv.DictWriter],
    vault_name: str,
    export_notes: bool,
    progress_callback: Optional[Callable[[str], None]],
    output_format: str = 'proton'
) -> dict:
    """Process all CSV rows and write to output files."""
    total_rows = 0
    login_rows = 0
    note_rows = 0
    password_cleaned = 0
    problem_count = 0

    for line in rows:
        if not line.strip():
            continue

        total_rows += 1

        if progress_callback and total_rows % 10 == 0:
            progress_callback(f"Processing row {total_rows}...")

        row = parse_truekey_line(line, fieldnames)

        if row.get('kind', '').lower() == 'note':
            if export_notes and notes_writer:
                if output_format == 'lastpass':
                    notes_row = {
                        'url': '',
                        'username': '',
                        'password': '',
                        'extra': row.get('content', ''),
                        'name': row.get('name', 'Untitled Note'),
                        'grouping': '',
                        'fav': ''
                    }
                elif output_format == '1password':
                    notes_row = {
                        'name': row.get('name', 'Untitled Note'),
                        'content': row.get('content', '')
                    }
                else:  # proton
                    notes_row = {
                        'name': row.get('name', 'Untitled Note'),
                        'content': row.get('content', '')
                    }
                notes_writer.writerow(notes_row)
                note_rows += 1
        else:
            name = row.get('name', '').strip()
            url = row.get('url', '').strip()
            login = row.get('login', '').strip()
            password = row.get('password', '')
            note = row.get('note', '').strip()

            original_password = password
            password = re.sub(r'\s+', '', password)

            if original_password != password and password:
                password_cleaned += 1

            skip_reasons = []
            if not name:
                skip_reasons.append("no name")
            if not login:
                skip_reasons.append("no login")
            if not password:
                skip_reasons.append("no password")
            if not url:
                skip_reasons.append("no url")

            if output_format == 'lastpass':
                output_row = {
                    'url': url,
                    'username': login,
                    'password': password,
                    'extra': '',
                    'name': name,
                    'grouping': '',
                    'fav': '',
                    'totp': ''
                }
            elif output_format == '1password':
                output_row = {
                    'name': name,
                    'url': url,
                    'username': login,
                    'password': password
                }
            else:  # proton
                output_row = {
                    'name': name,
                    'url': url,
                    'email': login,
                    'username': login,
                    'password': password,
                    'note': note,
                    'totp': '',
                    'vault': vault_name
                }

            writer.writerow(output_row)
            login_rows += 1

            if skip_reasons:
                problem_count += 1

    return {
        'total_rows': total_rows,
        'login_rows': login_rows,
        'note_rows': note_rows,
        'password_cleaned': password_cleaned,
        'problem_count': problem_count
    }
