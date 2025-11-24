#!/usr/bin/env python3
"""
Example usage of the ForminatorInsertGenerator.
Demonstrates how to generate MySQL INSERT queries for Forminator form entries.
"""

from datetime import datetime
from forminator_insert_generator import ForminatorInsertGenerator


def main():
    """Example usage of the ForminatorInsertGenerator."""
    generator = ForminatorInsertGenerator()
    
    # Example entry data
    example_entry = {
        'entry_id': 338,
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '+33 6 12 34 56 78',
        'grade': 'Daishihan',
        'dojo_name': 'Example Dojo',
        'birth_date': '15/06/1980',
        'gender': 'M',  # "M" for Male, "F" for Female
        'stripe_transaction_id': 'pi_1A2B3C4D5E6F7G8H9I0J1K2L',
        'stripe_amount': '450.00',
        'party': True,  # Include "Fête Finale / Final Party" in checkbox-2
        't_shirt': False,  # Include "T-Shirt" in checkbox-2 and related fields
        't_shirt_size': 'S',  # T-shirt size (only used when t_shirt=True)
        'party_participants': '2',  # Number of party participants (only used when party=True)
        'date_created': '15/06/2025',
        'ffst_id': 'M000000',  # Optional - adds text-1 field when set
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

