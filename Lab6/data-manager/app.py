from flask import Flask, request, jsonify
from bot.db.cur import conn

app = Flask(__name__)


@app.route('/get_currencies', methods=['GET'])
def get_currencies():
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT currency_name, rate FROM currencies")
            currencies = cur.fetchall()
            return jsonify({"currencies": currencies}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/convert_currency')
def convert_currency():
    try:
        currency_name = request.args.get('currency_name')
        amount = float(request.args.get('amount'))
        print(f"Currency name: {currency_name}")
        print(f"Amount: {amount}")

        with conn.cursor() as cur:
            cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))
            result = cur.fetchone()
            print(f"Result: {result}")

            if not result:
                return jsonify({"error": "Currency not found"}), 404
            else:
                rate = result[0]
                print(f"Rate: {rate}")
                converted_amount = amount * float(rate)
                print(f"Converted amount: {converted_amount}")
                return jsonify({"converted_amount": converted_amount}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5002)
