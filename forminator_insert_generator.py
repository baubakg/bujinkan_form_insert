#!/usr/bin/env python3
"""
Forminator Insert Query Generator
Generates MySQL INSERT queries for WordPress Forminator plugin form entries.
"""

from datetime import datetime
from typing import Dict, List, Optional


class ForminatorInsertGenerator:
    """Generate MySQL INSERT queries for Forminator form entry metadata."""
    
    TABLE_NAME = "wp_frmt_form_entry_meta"
    
    def __init__(self):
        """Initialize the generator."""
        pass
    
    @staticmethod
    def php_serialize_string(value: str) -> str:
        """
        Create a PHP serialized string.
        Format: s:length:"value"
        Note: PHP uses byte length for UTF-8 strings
        """
        byte_length = len(value.encode('utf-8'))
        return f's:{byte_length}:"{value}"'
    
    @staticmethod
    def php_serialize_name(first_name: str, last_name: str) -> str:
        """
        Create a PHP serialized array for name field.
        Format: a:2:{s:10:"first-name";s:X:"FirstName";s:9:"last-name";s:Y:"LastName";}
        """
        first_serialized = ForminatorInsertGenerator.php_serialize_string(first_name)
        last_serialized = ForminatorInsertGenerator.php_serialize_string(last_name)
        return f'a:2:{{s:10:"first-name";{first_serialized};s:9:"last-name";{last_serialized};}}'
    
    @staticmethod
    def php_serialize_calculation(amount: float, currency_symbol: str = "€") -> str:
        """
        Create a PHP serialized array for calculation field.
        Format: a:2:{s:6:"result";d:20;s:17:"formatting_result";s:6:"€ 20";}
        """
        # Format the amount string
        formatted_amount = f"{currency_symbol} {int(amount)}"
        formatted_serialized = ForminatorInsertGenerator.php_serialize_string(formatted_amount)
        
        # Build the serialized array
        return f'a:2:{{s:6:"result";d:{amount};s:17:"formatting_result";{formatted_serialized};}}'
    
    @staticmethod
    def php_serialize_stripe(transaction_id: str, amount: str, currency: str = "EUR", 
                            mode: str = "live", product_name: str = "Plan 1", 
                            payment_type: str = "One Time", status: str = "COMPLETED") -> str:
        """
        Create a PHP serialized array for Stripe payment data.
        Format: a:9:{s:4:"mode";s:4:"live";s:12:"product_name";...}
        """
        # Calculate the transaction link
        transaction_link = f"https://dashboard.stripe.com/payments/{transaction_id}"
        
        parts = [
            's:4:"mode";' + ForminatorInsertGenerator.php_serialize_string(mode),
            's:12:"product_name";' + ForminatorInsertGenerator.php_serialize_string(product_name),
            's:12:"payment_type";' + ForminatorInsertGenerator.php_serialize_string(payment_type),
            's:6:"amount";' + ForminatorInsertGenerator.php_serialize_string(amount),
            's:8:"quantity";' + ForminatorInsertGenerator.php_serialize_string("1"),
            's:8:"currency";' + ForminatorInsertGenerator.php_serialize_string(currency),
            's:14:"transaction_id";' + ForminatorInsertGenerator.php_serialize_string(transaction_id),
            's:16:"transaction_link";' + ForminatorInsertGenerator.php_serialize_string(transaction_link),
            's:6:"status";' + ForminatorInsertGenerator.php_serialize_string(status),
        ]
        
        return 'a:9:{' + ';'.join(parts) + ';}'
    
    @staticmethod
    def escape_sql_string(value: str) -> str:
        """Escape special characters for SQL string values."""
        # Escape single quotes and backslashes
        return value.replace('\\', '\\\\').replace("'", "\\'")
    
    def generate_insert_query(self, meta_id: int, entry_id: int, meta_key: str, 
                             meta_value: str, date_created: Optional[str] = None) -> str:
        """
        Generate a single INSERT query for a form entry meta field.
        
        Args:
            meta_id: Unique meta ID
            entry_id: Form entry ID
            meta_key: Field key (e.g., 'name-1', 'email-1')
            meta_value: Field value (can be serialized PHP array)
            date_created: Creation timestamp (defaults to current datetime)
        
        Returns:
            MySQL INSERT query string
        """
        if date_created is None:
            date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Escape the meta_value for SQL
        escaped_value = self.escape_sql_string(meta_value)
        
        query = (
            f"INSERT INTO `{self.TABLE_NAME}` "
            f"(`meta_id`, `entry_id`, `meta_key`, `meta_value`, `date_created`, `date_updated`) "
            f"VALUES "
            f"({meta_id}, {entry_id}, '{meta_key}', '{escaped_value}', '{date_created}', '0000-00-00 00:00:00');"
        )
        
        return query
    
    def generate_entry_inserts(
        self,
        entry_id: int,
        meta_id_start: int,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        grade: str,
        dojo_name: str,
        birth_date: str,
        gender: str,
        stripe_transaction_id: str,
        stripe_amount: str,
        party: bool = False,
        t_shirt: bool = False,
        t_shirt_size: Optional[str] = None,
        date_created: Optional[str] = None,
        currency: str = "EUR"
    ) -> List[str]:
        """
        Generate all INSERT queries for a complete form entry.
        
        Args:
            entry_id: Form entry ID
            meta_id_start: Starting meta ID (will be incremented for each field)
            first_name: First name of the person
            last_name: Last name of the person
            email: Email address
            phone: Phone number
            grade: Grade/rank (e.g., "10 Dan")
            dojo_name: Name of the dojo
            birth_date: Birth date (format: DD/MM/YYYY)
            gender: Gender - "M" for "Masculin / Male", "F" for "Féminin / Female"
            stripe_transaction_id: Stripe transaction ID
            stripe_amount: Amount paid (e.g., "375.00")
            party: Include "Fête Finale / Final Party" in checkbox-2 (default: False)
            t_shirt: Include "T-Shirt" in checkbox-2 and related fields (default: False)
            t_shirt_size: T-shirt size (e.g., "M", "L", "XL") - only used when t_shirt=True
            date_created: Creation timestamp (defaults to current datetime)
            currency: Currency code (default: "EUR")
        
        Returns:
            List of MySQL INSERT query strings
        """
        if date_created is None:
            date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert gender code to full text
        gender_map = {
            'M': 'Masculin / Male',
            'F': 'Féminin / Female'
        }
        gender_value = gender_map.get(gender, gender)  # Use mapped value or original if not M/F
        
        queries = []
        current_meta_id = meta_id_start
        
        # Generate the submission date in DD/MM/YYYY format for hidden-2
        if date_created:
            # Parse the date_created and convert to DD/MM/YYYY format
            from datetime import datetime as dt
            dt_obj = dt.strptime(date_created, '%Y-%m-%d %H:%M:%S')
            submission_date = dt_obj.strftime('%d/%m/%Y')
        else:
            submission_date = datetime.now().strftime('%d/%m/%Y')
        
        # 1. Hidden field (hidden-1) - Entry ID
        queries.append(self.generate_insert_query(
            current_meta_id, entry_id, 'hidden-1', str(entry_id), date_created
        ))
        current_meta_id += 1
        
        # 2. Hidden field (hidden-2) - Submission Date (DD/MM/YYYY)
        queries.append(self.generate_insert_query(
            current_meta_id, entry_id, 'hidden-2', submission_date, date_created
        ))
        current_meta_id += 1
        
        # 3. Calculation-1 field (always present - 20 if t_shirt, 0 otherwise)
        calculation_amount = 20 if t_shirt else 0
        calculation_value = self.php_serialize_calculation(calculation_amount)
        queries.append(self.generate_insert_query(
            current_meta_id, entry_id, 'calculation-1', calculation_value, date_created
        ))
        current_meta_id += 1
        
        # 4. Calculation-2 field (always present - stripe amount)
        calculation2_value = self.php_serialize_calculation(float(stripe_amount))
        queries.append(self.generate_insert_query(
            current_meta_id, entry_id, 'calculation-2', calculation2_value, date_created
        ))
        current_meta_id += 1
        
        # 5. Name field (name-1) - PHP serialized array
        name_value = self.php_serialize_name(first_name, last_name)
        queries.append(self.generate_insert_query(
            current_meta_id, entry_id, 'name-1', name_value, date_created
        ))
        current_meta_id += 1
        
        # 6. Email field (email-1)
        queries.append(self.generate_insert_query(
            current_meta_id, entry_id, 'email-1', email, date_created
        ))
        current_meta_id += 1
        
        # 7. Phone field (phone-1)
        queries.append(self.generate_insert_query(
            current_meta_id, entry_id, 'phone-1', phone, date_created
        ))
        current_meta_id += 1
        
        # 8. Grade field (select-1)
        queries.append(self.generate_insert_query(
            current_meta_id, entry_id, 'select-1', grade, date_created
        ))
        current_meta_id += 1
        
        # 9. Dojo Name field (text-3)
        queries.append(self.generate_insert_query(
            current_meta_id, entry_id, 'text-3', dojo_name, date_created
        ))
        current_meta_id += 1
        
        # 10. Birth Date field (date-1)
        queries.append(self.generate_insert_query(
            current_meta_id, entry_id, 'date-1', birth_date, date_created
        ))
        current_meta_id += 1
        
        # 11. Gender field (select-2) - only when t_shirt is True
        if t_shirt:
            queries.append(self.generate_insert_query(
                current_meta_id, entry_id, 'select-2', gender_value, date_created
            ))
            current_meta_id += 1
        
        # 12. T-Shirt Size field (select-3) - only when t_shirt is True and t_shirt_size is provided
        if t_shirt and t_shirt_size:
            queries.append(self.generate_insert_query(
                current_meta_id, entry_id, 'select-3', t_shirt_size, date_created
            ))
            current_meta_id += 1
        
        # 13. Select-4 field (conditional - only when t_shirt is True)
        if t_shirt:
            queries.append(self.generate_insert_query(
                current_meta_id, entry_id, 'select-4', '1', date_created
            ))
            current_meta_id += 1
        
        # 14. Select-5 field (always "1")
        queries.append(self.generate_insert_query(
            current_meta_id, entry_id, 'select-5', '1', date_created
        ))
        current_meta_id += 1
        
        # 15. Checkbox-2 field (optional - party and/or t-shirt)
        if party or t_shirt:
            checkbox_values = []
            if party:
                checkbox_values.append('Fête Finale / Final Party')
            if t_shirt:
                checkbox_values.append('T-Shirt')
            checkbox_value = ', '.join(checkbox_values)
            queries.append(self.generate_insert_query(
                current_meta_id, entry_id, 'checkbox-2', checkbox_value, date_created
            ))
            current_meta_id += 1
        
        # 16. Stripe payment field (stripe-ocs-1) - PHP serialized array
        stripe_value = self.php_serialize_stripe(stripe_transaction_id, stripe_amount, currency)
        queries.append(self.generate_insert_query(
            current_meta_id, entry_id, 'stripe-ocs-1', stripe_value, date_created
        ))
        current_meta_id += 1
        
        return queries
    
    def generate_multiple_entries(self, entries: List[Dict]) -> List[str]:
        """
        Generate INSERT queries for multiple form entries.
        
        Args:
            entries: List of dictionaries containing entry data.
                    Each dict should have keys: entry_id, meta_id_start, first_name,
                    last_name, email, phone, grade, dojo_name, birth_date, gender,
                    stripe_transaction_id, stripe_amount, and optionally date_created, currency
        
        Returns:
            List of all MySQL INSERT query strings
        """
        all_queries = []
        
        for entry in entries:
            queries = self.generate_entry_inserts(
                entry_id=entry['entry_id'],
                meta_id_start=entry['meta_id_start'],
                first_name=entry['first_name'],
                last_name=entry['last_name'],
                email=entry['email'],
                phone=entry['phone'],
                grade=entry['grade'],
                dojo_name=entry['dojo_name'],
                birth_date=entry['birth_date'],
                gender=entry['gender'],
                stripe_transaction_id=entry['stripe_transaction_id'],
                stripe_amount=entry['stripe_amount'],
                date_created=entry.get('date_created'),
                currency=entry.get('currency', 'EUR')
            )
            all_queries.extend(queries)
            all_queries.append('')  # Add empty line between entries
        
        return all_queries


def main():
    """Example usage of the ForminatorInsertGenerator."""
    generator = ForminatorInsertGenerator()
    
    # Example entry data
    example_entry = {
        'entry_id': 668,
        'meta_id_start': 6031,
        'first_name': 'Xander',
        'last_name': 'Beemer',
        'email': 'xjbeemer@hotmail.com',
        'phone': '+31 613865831',
        'grade': '6 Dan',
        'dojo_name': 'Miko Dojo',
        'birth_date': '02/03/1973',
        'gender': 'M',  # "M" for Male, "F" for Female
        'stripe_transaction_id': 'pi_3RnbxeBvS0tjVNMi1g2TFBHk',
        'stripe_amount': '350.00',
        'party': True,  # Include "Fête Finale / Final Party" in checkbox-2
        't_shirt': True,  # Include "T-Shirt" in checkbox-2 and related fields
        't_shirt_size': 'L',  # T-shirt size (only used when t_shirt=True)
        # currency defaults to 'EUR' - no need to specify
    }
    
    # Generate queries for the example entry
    queries = generator.generate_entry_inserts(**example_entry)
    
    # Print the queries
    print("-- Forminator Form Entry Meta INSERT Queries")
    print(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"-- Entry ID: {example_entry['entry_id']}")
    print()
    
    for query in queries:
        print(query)
    
    print()
    print(f"-- Total queries generated: {len(queries)}")
    


if __name__ == '__main__':
    main()

