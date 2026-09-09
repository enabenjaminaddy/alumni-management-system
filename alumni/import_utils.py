import csv
import io
from decimal import Decimal, InvalidOperation

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from alumni.models import AlumniProfile, EMPLOYMENT_STATUS_CHOICES

EMPLOYMENT_VALUES = {c[0] for c in EMPLOYMENT_STATUS_CHOICES}
REQUIRED_HEADERS = {'email', 'first_name', 'last_name'}
META_KEYS = frozenset({'import_action', 'row_number'})


def _normalize_header(name):
    return (name or '').strip().lower().replace(' ', '_')


def _parse_bool(value):
    if value is None or str(value).strip() == '':
        return False
    return str(value).strip().lower() in ('1', 'true', 'yes', 'y')


def _parse_decimal(value, field_name, row_errors):
    if value is None or str(value).strip() == '':
        return Decimal('0.00')
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        row_errors.append(f'Invalid {field_name}: {value}')
        return Decimal('0.00')


def _parse_year(value, row_errors):
    if value is None or str(value).strip() == '':
        return None
    try:
        year = int(str(value).strip())
        if year < 1950 or year > 2100:
            row_errors.append(f'Graduation year out of range: {year}')
            return None
        return year
    except ValueError:
        row_errors.append(f'Invalid graduation year: {value}')
        return None


def parse_alumni_csv(file_obj):
    """Parse CSV and return (valid_rows, errors)."""
    raw = file_obj.read()
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8-sig')

    reader = csv.DictReader(io.StringIO(raw))
    if not reader.fieldnames:
        return [], [{'row': 0, 'messages': ['CSV has no header row.']}]

    headers = {_normalize_header(h) for h in reader.fieldnames if h}
    missing = REQUIRED_HEADERS - headers
    if missing:
        return [], [{
            'row': 0,
            'messages': [f'Missing required columns: {", ".join(sorted(missing))}'],
        }]

    reader.fieldnames = [_normalize_header(h) for h in reader.fieldnames]

    rows = []
    errors = []
    seen_emails = set()

    for index, raw_row in enumerate(reader, start=2):
        row_errors = []
        email = (raw_row.get('email') or '').strip().lower()
        first_name = (raw_row.get('first_name') or '').strip()
        last_name = (raw_row.get('last_name') or '').strip()

        if not email:
            row_errors.append('Email is required')
        else:
            try:
                validate_email(email)
            except ValidationError:
                row_errors.append(f'Invalid email: {email}')
            if email in seen_emails:
                row_errors.append(f'Duplicate email in file: {email}')
            seen_emails.add(email)

        if not first_name:
            row_errors.append('First name is required')
        if not last_name:
            row_errors.append('Last name is required')

        employment = (raw_row.get('employment_status') or '').strip().lower()
        if employment and employment not in EMPLOYMENT_VALUES:
            row_errors.append(
                f'Invalid employment_status: {employment}. '
                f'Use: {", ".join(sorted(EMPLOYMENT_VALUES))}'
            )

        data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': (raw_row.get('phone_number') or '').strip() or None,
            'current_address': (raw_row.get('current_address') or '').strip() or None,
            'graduation_year': _parse_year(raw_row.get('graduation_year'), row_errors),
            'course_studied': (raw_row.get('course_studied') or '').strip() or None,
            'employment_status': employment or None,
            'company_name': (raw_row.get('company_name') or '').strip() or None,
            'company_location': (raw_row.get('company_location') or '').strip() or None,
            'skills_acquired': (raw_row.get('skills_acquired') or '').strip() or None,
            'work_experience': (raw_row.get('work_experience') or '').strip() or None,
            'monthly_savings': _parse_decimal(
                raw_row.get('monthly_savings'), 'monthly_savings', row_errors
            ),
            'monthly_investment': _parse_decimal(
                raw_row.get('monthly_investment'), 'monthly_investment', row_errors
            ),
            'mentorship_interest': _parse_bool(raw_row.get('mentorship_interest')),
            'networking_interest': _parse_bool(raw_row.get('networking_interest')),
        }

        existing = AlumniProfile.objects.filter(email=email).exists() if email else False
        data['import_action'] = 'update' if existing else 'create'
        data['row_number'] = index

        if row_errors:
            errors.append({'row': index, 'messages': row_errors, 'email': email})
        else:
            rows.append(data)

    return rows, errors


def commit_alumni_rows(rows):
    """Create or update profiles by email. Returns (created, updated)."""
    created = 0
    updated = 0
    for data in rows:
        payload = {k: v for k, v in data.items() if k not in META_KEYS}
        email = payload.pop('email')
        for money_field in ('monthly_savings', 'monthly_investment'):
            if money_field in payload and not isinstance(payload[money_field], Decimal):
                try:
                    payload[money_field] = Decimal(str(payload[money_field]))
                except (InvalidOperation, ValueError):
                    payload[money_field] = Decimal('0.00')
        obj, was_created = AlumniProfile.objects.update_or_create(
            email=email,
            defaults=payload,
        )
        if was_created:
            created += 1
        else:
            updated += 1
    return created, updated
