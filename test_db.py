import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='HDFCBank',
        charset='latin1'  # ← Add this
    )
    print("✅ Database connection successful!")
    
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    print("Tables:", tables)
    
    connection.close()
except Exception as e:
    print("❌ Error:", e)