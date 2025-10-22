# Forminator Insert Query Generator

A Python tool for generating MySQL INSERT queries for WordPress Forminator plugin form entries.

## Overview

This tool generates properly formatted MySQL INSERT queries for the `wp_frmt_form_entry_meta` table used by the Forminator WordPress plugin. It handles PHP serialization for complex fields like names and Stripe payment data.

## Features

- ✅ Generates MySQL INSERT queries for Forminator form entries
- ✅ Handles PHP serialization for name fields (first-name, last-name)
- ✅ Handles PHP serialization for Stripe payment data (transaction ID, amount, etc.)
- ✅ Automatic meta_id incrementing
- ✅ Automatic timestamp generation or custom date/time
- ✅ Supports single or multiple entries
- ✅ SQL string escaping for safety
- ✅ Export to SQL file for database import

## Fields Supported

The generator creates INSERT queries for the following Forminator form fields:

| Field | Meta Key | Type | Description |
|-------|----------|------|-------------|
| Hidden Entry ID | `hidden-1` | String | Contains the entry_id value |
| Hidden Submission Date | `hidden-2` | String | Form submission date (DD/MM/YYYY format) |
| Calculation-1 | `calculation-1` | Serialized Array | T-shirt fee - €20 if `t_shirt=True`, €0 otherwise (always added) |
| Calculation-2 | `calculation-2` | Serialized Array | Stripe payment amount (always added) |
| Name | `name-1` | Serialized Array | First name and last name |
| Email | `email-1` | String | Email address |
| Phone | `phone-1` | String | Phone number |
| Grade | `select-1` | String | Grade/rank (e.g., "10 Dan") |
| Dojo Name | `text-3` | String | Name of the dojo |
| Birth Date | `date-1` | String | Birth date (DD/MM/YYYY format) |
| Gender | `select-2` | String | Gender - "M" or "F" (only inserted when `t_shirt=True`) |
| T-Shirt Size | `select-3` | String | T-shirt size (e.g., "M", "L", "XL") - only when `t_shirt=True` |
| Select-4 | `select-4` | String | Set to "1" when `t_shirt=True` (automatically added) |
| Select-5 | `select-5` | String | Always set to "1" (automatically added) |
| Party/T-Shirt Checkbox | `checkbox-2` | String | Optional: "Fête Finale / Final Party", "T-Shirt", or both (comma-separated) |
| Stripe Payment | `stripe-ocs-1` | Serialized Array | Transaction ID, amount, currency, status |

## Installation

No installation required. Just download the script:

```bash
git clone <repository-url>
cd bujinkan_forminator_insert
```

## Usage

### Quick Start

```python
from forminator_insert_generator import ForminatorInsertGenerator

# Create generator instance
generator = ForminatorInsertGenerator()

# Generate queries for a single entry
queries = generator.generate_entry_inserts(
    entry_id=664,
    meta_id_start=5973,
    first_name='Lamine',
    last_name='Djama',
    email='lamine-djama@outlook.com',
    phone='+33 6 95 48 74 91',
    grade='10 Dan',
    dojo_name='Aucun',
    birth_date='21/11/1991',
    gender='M',  # "M" for Male, "F" for Female
    stripe_transaction_id='pi_3SJb3zBvS0tjVNMi1aciMK9e',
    stripe_amount='375.00',
    party=True,  # Optional: Include "Fête Finale / Final Party" in checkbox-2
    t_shirt=True,  # Optional: Include "T-Shirt" in checkbox-2 and related fields
    t_shirt_size='L'  # Optional: T-shirt size (only used when t_shirt=True)
    # currency defaults to 'EUR' - no need to specify
)

# Print the queries
for query in queries:
    print(query)
```

### Generate Multiple Entries

```python
entries = [
    {
        'entry_id': 665,
        'meta_id_start': 6000,
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '+1 555 123 4567',
        'grade': '5 Dan',
        'dojo_name': 'Tokyo Dojo',
        'birth_date': '15/03/1985',
        'gender': 'Masculin / Male',
        'stripe_transaction_id': 'pi_1234567890',
        'stripe_amount': '300.00',
    },
    # Add more entries...
]

all_queries = generator.generate_multiple_entries(entries)
```

### Save to SQL File

```python
with open('forminator_inserts.sql', 'w', encoding='utf-8') as f:
    f.write("-- Forminator INSERT Queries\n\n")
    for query in all_queries:
        f.write(query + '\n')
```

## Examples

Run the included example scripts:

```bash
# See how the generator works
python3 forminator_insert_generator.py

# Run usage examples
python3 example_usage.py
```

## Method Reference

### `generate_entry_inserts()`

Generate all INSERT queries for a complete form entry.

**Parameters:**
- `entry_id` (int): Form entry ID
- `meta_id_start` (int): Starting meta ID (will be incremented for each field)
- `first_name` (str): First name
- `last_name` (str): Last name
- `email` (str): Email address
- `phone` (str): Phone number
- `grade` (str): Grade/rank (e.g., "10 Dan")
- `dojo_name` (str): Name of the dojo
- `birth_date` (str): Birth date in DD/MM/YYYY format
- `gender` (str): Gender - "M" for "Masculin / Male", "F" for "Féminin / Female"
- `stripe_transaction_id` (str): Stripe transaction ID
- `stripe_amount` (str): Amount paid (e.g., "375.00")
- `party` (bool, optional): Include "Fête Finale / Final Party" in checkbox-2 (defaults to False)
- `t_shirt` (bool, optional): Include "T-Shirt" in checkbox-2 and related fields (defaults to False)
- `t_shirt_size` (str, optional): T-shirt size (e.g., "M", "L", "XL") - only used when t_shirt=True
- `date_created` (str, optional): Custom timestamp (defaults to current datetime)
- `currency` (str, optional): Currency code (defaults to "EUR")

**Returns:**
- List of MySQL INSERT query strings

### `generate_multiple_entries()`

Generate INSERT queries for multiple form entries.

**Parameters:**
- `entries` (List[Dict]): List of entry dictionaries with all required fields

**Returns:**
- List of all MySQL INSERT query strings

## Database Import

After generating the SQL file, import it into your MySQL database:

```bash
mysql -u username -p database_name < forminator_inserts.sql
```

Or use phpMyAdmin:
1. Go to your database
2. Click on the "Import" tab
3. Choose the generated SQL file
4. Click "Go"

## Notes

- The `meta_id` is automatically incremented for each field (12-17 fields per entry depending on options)
- The `date_created` defaults to the current date/time if not specified
- The `date_updated` is always set to `'0000-00-00 00:00:00'` (Forminator default)
- The `currency` defaults to `'EUR'` - no need to specify unless using a different currency
- The `gender` parameter accepts "M" or "F" and automatically converts to "Masculin / Male" or "Féminin / Female"
- The `gender` field (select-2) is only inserted when `t_shirt=True`
- The `calculation-1` field is always added - contains €20 if `t_shirt=True`, €0 otherwise
- The `calculation-2` field is always added - contains the stripe payment amount
- The `party` parameter is optional (defaults to `False`) - set to `True` to include "Fête Finale / Final Party" in checkbox-2
- The `t_shirt` parameter is optional (defaults to `False`) - set to `True` to include "T-Shirt" in checkbox-2 and add related fields (select-2, select-3, select-4, calculation-1=€20)
- The `t_shirt_size` parameter is optional - only used when `t_shirt=True` (e.g., "M", "L", "XL")
- When both `party` and `t_shirt` are `True`, checkbox-2 will contain: "Fête Finale / Final Party, T-Shirt"
- PHP serialization format matches Forminator's exact format
- All strings are properly escaped for SQL safety
- The `hidden-1` field automatically stores the entry_id value
- The `hidden-2` field automatically stores the submission date (derived from `date_created`)
- The `select-3` field (t-shirt size) is only added when `t_shirt=True` and `t_shirt_size` is provided
- The `select-4` field is set to "1" when `t_shirt=True` (automatically added)
- The `select-5` field is always set to "1" (automatically added)

## Template Structure

The generator follows the structure from `wp_frmt_form_entry_meta_clean.json`:

```json
{
    "meta_id": "5973",
    "entry_id": "664",
    "meta_key": "name-1",
    "meta_value": "a:2:{s:10:\"first-name\";s:6:\"Lamine\";s:9:\"last-name\";s:5:\"Djama\";}",
    "date_created": "2025-10-18 14:25:49",
    "date_updated": "0000-00-00 00:00:00"
}
```

## Requirements

- Python 3.6+
- No external dependencies required

## License

MIT License - Feel free to use and modify as needed.

## Support

For issues or questions, please open an issue on the repository.

