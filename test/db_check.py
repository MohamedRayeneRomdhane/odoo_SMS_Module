#!/usr/bin/env python3
"""
Direct database check script
"""
import os
import sys

# Add the Odoo path
sys.path.insert(0, '/usr/lib/python3/dist-packages')

try:
    import psycopg2
    
    # Database connection parameters
    conn = psycopg2.connect(
        host='db',
        database='test',
        user='odoo',
        password='odoo'
    )
    
    cursor = conn.cursor()
    
    print("=== SMS History Database Check ===")
    
    # Check if SMS history table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'sms_tunisiesms_history'
        );
    """)
    table_exists = cursor.fetchone()[0]
    print(f"SMS History table exists: {table_exists}")
    
    if table_exists:
        # Check total records
        cursor.execute("SELECT COUNT(*) FROM sms_tunisiesms_history;")
        total_records = cursor.fetchone()[0]
        print(f"Total SMS history records: {total_records}")
        
        if total_records > 0:
            # Show recent records
            cursor.execute("""
                SELECT 
                    h.id,
                    h.name,
                    h.sms,
                    h.to,
                    h.date_create,
                    h.user_id,
                    u.name as user_name
                FROM sms_tunisiesms_history h
                LEFT JOIN res_users u ON h.user_id = u.id
                ORDER BY h.date_create DESC
                LIMIT 5;
            """)
            
            records = cursor.fetchall()
            print("\nRecent SMS History Records:")
            for record in records:
                print(f"  ID: {record[0]}, Name: {record[1]}, SMS: {record[2][:50]}...")
                print(f"    To: {record[3]}, Date: {record[4]}, User: {record[6]}")
    
    # Check user access permissions
    cursor.execute("SELECT COUNT(*) FROM res_smsserver_group_rel;")
    access_count = cursor.fetchone()[0]
    print(f"\nUsers with SMS access: {access_count}")
    
    # Check specific user (Mitchell Admin is typically user ID 2)
    cursor.execute("""
        SELECT u.id, u.name, 
               CASE WHEN r.uid IS NOT NULL THEN 'YES' ELSE 'NO' END as has_access
        FROM res_users u
        LEFT JOIN res_smsserver_group_rel r ON u.id = r.uid
        WHERE u.active = true
        ORDER BY u.id;
    """)
    
    users = cursor.fetchall()
    print("\nUser Access Status:")
    for user in users:
        print(f"  User ID: {user[0]}, Name: {user[1]}, SMS Access: {user[2]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    
print("\n=== Check Complete ===")
