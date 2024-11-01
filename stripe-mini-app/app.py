from flask import Flask, render_template, jsonify, request
import stripe
import os
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Set your secret key here
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@app.route('/')
def index():
    # Get the public key from environment variables
    stripe_publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
    return render_template('index.html', stripe_pb_key = stripe_publishable_key)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    # The amount in cents
    amount = int(request.form['amount']) * 100  
    try:
        # Create a new Checkout Session for the order
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': 'Deposit',
                        },
                        'unit_amount': amount,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://localhost:5000/success',
            cancel_url='http://localhost:5000/cancel',
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

if __name__ == '__main__':
    app.run(port=5000)
