from flask import Flask, request, jsonify
from bot.db.cur import conn

app = Flask(__name__)


@app.route('/add_currency', methods=['POST'])
def add_currency():
    try:
        data = request.get_json()
        currency_name = data['currency_name']
        rate = data['rate']

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
            result = cur.fetchone()

            if result:
                return jsonify({"error": "Currency already exists"}), 400
            else:
                cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (currency_name, rate))
                conn.commit()
                return jsonify({"message": "Currency added successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/delete_currency', methods=['POST'])
def delete_currency():
    try:
        data = request.get_json()
        currency_name = data['currency_name']

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
            result = cur.fetchone()

            if not result:
                return jsonify({"error": "Currency not found"}), 404
            else:
                cur.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
                conn.commit()
                return jsonify({"message": "Currency deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/update_currency', methods=['POST'])
def update_currency():
    try:
        data = request.get_json()
        currency_name = data['currency_name']
        rate = data['rate']

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
            result = cur.fetchone()

            if not result:
                return jsonify({"error": "Currency not found"}), 404
            else:
                cur.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (rate, currency_name))
                conn.commit()
                return jsonify({"message": "Currency rate updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5001)
