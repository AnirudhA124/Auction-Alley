import cx_Oracle

try:
    # Replace 'username', 'password', and 'host:port' with your actual Oracle connection details
    connection = cx_Oracle.connect('system', '1234', 'localhost:1521/XE')

    # Create a cursor
    cursor = connection.cursor()

    # Execute SQL query to create user_table
    cursor.execute("""
    CREATE TABLE user_table (
        name VARCHAR(255)
    )
    """)

    print("Table 'user_table' created successfully.")

    # Commit the transaction
    connection.commit()

except cx_Oracle.DatabaseError as e:
    # Handle any database errors
    print("Database error:", e)

finally:
    # Close the cursor and connection
    if cursor:
        cursor.close()
    if connection:
        connection.close()
