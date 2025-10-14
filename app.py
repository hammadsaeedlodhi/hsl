from flask import Flask, jsonify, request
import mysql.connector
import os

app = Flask(__name__)

# ✅ Configure MySQL connection
db_config = {
    "host": "your-aws-rds-endpoint.amazonaws.com",
    "user": "your_username",
    "password": "your_password",
    "database": "your_database"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# ✅ Health check route
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

# ✅ Get all accounts
@app.route('/accounts', methods=['GET'])
def get_accounts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Account LIMIT 10")
        accounts = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(accounts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Add new account
@app.route('/accounts', methods=['POST'])
def add_account():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """INSERT INTO Account (Name, Industry, Rating, Phone, Country, Active)
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (
            data.get('Name'),
            data.get('Industry'),
            data.get('Rating'),
            data.get('Phone'),
            data.get('Country'),
            data.get('Active')
        )
        cursor.execute(sql, values)
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"message": "Account added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Main entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
