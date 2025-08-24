#!/usr/bin/env python3
"""
Create a SQLite database with Stripe balance_transactions table
Populate it with 2000+ synthetic transactions
"""

import sqlite3
import json
import requests
from datetime import datetime

def create_balance_transactions_table():
    """Create the balance_transactions table with Stripe schema"""
    
    # Connect to SQLite database (creates file if doesn't exist)
    conn = sqlite3.connect('stripe_transactions.db')
    cursor = conn.cursor()
    
    # Drop table if exists
    cursor.execute('DROP TABLE IF EXISTS balance_transactions')
    
    # Create balance_transactions table with Stripe schema
    cursor.execute('''
        CREATE TABLE balance_transactions (
            id VARCHAR(255) PRIMARY KEY,
            object VARCHAR(50) DEFAULT 'balance_transaction',
            amount INTEGER NOT NULL,
            currency VARCHAR(3) NOT NULL,
            created INTEGER NOT NULL,
            type VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'available',
            reporting_category VARCHAR(100),
            fee INTEGER DEFAULT 0,
            fee_details TEXT,
            net INTEGER,
            source_id VARCHAR(255),
            charge_id VARCHAR(255),
            payout_id VARCHAR(255),
            automatic_transfer_id VARCHAR(255),
            description TEXT,
            exchange_rate DECIMAL(10, 6),
            metadata TEXT
        )
    ''')
    
    # Create indexes separately
    cursor.execute('CREATE INDEX idx_created ON balance_transactions(created)')
    cursor.execute('CREATE INDEX idx_type ON balance_transactions(type)')
    cursor.execute('CREATE INDEX idx_status ON balance_transactions(status)')
    cursor.execute('CREATE INDEX idx_source ON balance_transactions(source_id)')
    cursor.execute('CREATE INDEX idx_payout ON balance_transactions(payout_id)')
    
    print("✅ Created balance_transactions table")
    
    # Create additional Stripe tables
    
    # balance_transaction_fee_details table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS balance_transaction_fee_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            balance_transaction_id VARCHAR(255),
            amount INTEGER,
            currency VARCHAR(3),
            type VARCHAR(50),  -- stripe_fee, tax, etc.
            description TEXT,
            FOREIGN KEY (balance_transaction_id) REFERENCES balance_transactions(id)
        )
    ''')
    
    # charges table (simplified)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS charges (
            id VARCHAR(255) PRIMARY KEY,
            amount INTEGER,
            currency VARCHAR(3),
            created INTEGER,
            customer_id VARCHAR(255),
            description TEXT,
            status VARCHAR(50),
            card_brand VARCHAR(50),
            card_last4 VARCHAR(4),
            failure_code VARCHAR(100),
            failure_message TEXT,
            metadata TEXT
        )
    ''')
    
    # refunds table (simplified)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS refunds (
            id VARCHAR(255) PRIMARY KEY,
            amount INTEGER,
            currency VARCHAR(3),
            created INTEGER,
            charge_id VARCHAR(255),
            reason VARCHAR(50),
            status VARCHAR(50),
            balance_transaction_id VARCHAR(255),
            metadata TEXT
        )
    ''')
    
    print("✅ Created additional Stripe tables (charges, refunds, fee_details)")
    
    conn.commit()
    return conn

def populate_with_api_data(conn):
    """Fetch data from API and populate database"""
    
    cursor = conn.cursor()
    
    try:
        # Fetch transactions from API
        print("🔄 Fetching transactions from API...")
        response = requests.get('http://localhost:8000/data/transactions/all')
        data = response.json()
        
        transactions = data['transactions']
        print(f"📊 Retrieved {len(transactions)} transactions")
        
        # Insert transactions into database
        for txn in transactions:
            # Insert into balance_transactions
            cursor.execute('''
                INSERT INTO balance_transactions (
                    id, object, amount, currency, created, type, status,
                    fee, net, description, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                txn['id'],
                txn['object'],
                txn['amount'],
                txn['currency'],
                txn['created'],
                txn['type'],
                txn['status'],
                txn.get('fee', 0),
                txn.get('net', txn['amount']),
                txn.get('description', ''),
                json.dumps(txn.get('metadata', {}))
            ))
            
            # If it's a charge, also insert into charges table
            if txn['type'] == 'charge':
                cursor.execute('''
                    INSERT OR IGNORE INTO charges (
                        id, amount, currency, created, description, status, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    'ch_' + txn['id'][4:],  # Convert txn_ to ch_
                    txn['amount'],
                    txn['currency'],
                    txn['created'],
                    txn.get('description', ''),
                    'succeeded',
                    json.dumps(txn.get('metadata', {}))
                ))
            
            # If it's a refund, insert into refunds table
            elif txn['type'] == 'refund':
                cursor.execute('''
                    INSERT OR IGNORE INTO refunds (
                        id, amount, currency, created, reason, status, 
                        balance_transaction_id, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    're_' + txn['id'][4:],  # Convert txn_ to re_
                    abs(txn['amount']),  # Refunds are positive in refunds table
                    txn['currency'],
                    txn['created'],
                    'requested_by_customer',
                    'succeeded',
                    txn['id'],
                    json.dumps(txn.get('metadata', {}))
                ))
        
        conn.commit()
        print(f"✅ Inserted {len(transactions)} transactions into database")
        
        # Show statistics
        cursor.execute("SELECT COUNT(*) FROM balance_transactions")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT type, COUNT(*) FROM balance_transactions GROUP BY type")
        type_counts = cursor.fetchall()
        
        print("\n📊 Database Statistics:")
        print(f"Total balance_transactions: {total}")
        print("\nBreakdown by type:")
        for type_name, count in type_counts:
            print(f"  - {type_name}: {count}")
        
        # Sample queries
        print("\n🔍 Sample Queries:")
        
        # Recent transactions
        cursor.execute('''
            SELECT id, amount/100.0 as amount_dollars, type, 
                   datetime(created, 'unixepoch') as created_date
            FROM balance_transactions 
            ORDER BY created DESC 
            LIMIT 5
        ''')
        
        print("\nMost recent transactions:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: ${row[1]:.2f} ({row[2]}) - {row[3]}")
        
        # Daily totals
        cursor.execute('''
            SELECT 
                date(created, 'unixepoch') as day,
                SUM(CASE WHEN type='charge' THEN amount ELSE 0 END)/100.0 as charges,
                SUM(CASE WHEN type='refund' THEN amount ELSE 0 END)/100.0 as refunds,
                SUM(net)/100.0 as net_total
            FROM balance_transactions
            GROUP BY date(created, 'unixepoch')
            ORDER BY day DESC
            LIMIT 5
        ''')
        
        print("\nDaily totals (last 5 days):")
        for row in cursor.fetchall():
            print(f"  {row[0]}: Charges=${row[1]:.2f}, Refunds=${row[2]:.2f}, Net=${row[3]:.2f}")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        print("Make sure the API is running at http://localhost:8000")
    
    return conn

def main():
    """Main function"""
    print("🚀 Creating Stripe balance_transactions database\n")
    
    # Create database and tables
    conn = create_balance_transactions_table()
    
    # Populate with API data
    populate_with_api_data(conn)
    
    # Close connection
    conn.close()
    
    print("\n✅ Database created: stripe_transactions.db")
    print("\n📝 You can now query the database with SQL:")
    print("   sqlite3 stripe_transactions.db")
    print('   SELECT * FROM balance_transactions LIMIT 10;')

if __name__ == "__main__":
    main()