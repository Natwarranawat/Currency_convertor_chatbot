from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()

        # Check if required parameters are present in the request
        if not data or 'queryResult' not in data or 'parameters' not in data['queryResult']:
            return jsonify({'fulfillmentText': "Invalid request, missing parameters."})

        try:
            source_currency = data['queryResult']['parameters']['unit-currency']['currency']
            amount = data['queryResult']['parameters']['unit-currency']['amount']
            target_currency = data['queryResult']['parameters']['currency-name']

            # Fetch conversion factor and calculate the final amount
            cf = fetch_conversion_factor(source_currency, target_currency)
            final_amount = amount * cf
            final_amount = round(final_amount, 2)

            response = {
                'fulfillmentText': "{} {} is {} {}".format(amount, source_currency, final_amount, target_currency)
            }
            return jsonify(response)

        except KeyError:
            return jsonify({'fulfillmentText': "Error processing the request, check the currency format."})
        except Exception as e:
            return jsonify({'fulfillmentText': f"An error occurred: {str(e)}"})

    # Optional response for GET requests (for testing)
    return "Send a POST request with valid currency data."


def fetch_conversion_factor(source, target):
    url = "https://free.currconv.com/api/v7/convert?q={}_{}&compact=ultra&apiKey=3d0e0b0905b4f20dad21".format(source, target)

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Error fetching conversion rate.")
    
    data = response.json()

    conversion_key = '{}_{}'.format(source, target)
    if conversion_key not in data:
        raise Exception("Invalid currency conversion data.")
    
    return data[conversion_key]


if __name__ == "__main__":
    app.run(debug=True)
