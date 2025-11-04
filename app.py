from flask import Flask, jsonify, request
from data_provider import data_provider

app = Flask(__name__)

@app.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        new_data = request.get_json()
        for key, value in new_data.items():
            if hasattr(data_provider, key):
                setattr(data_provider, key, value)
        return jsonify(data_provider.__dict__)
    else:  # GET request
        return jsonify(data_provider.__dict__)

if __name__ == '__main__':
    app.run(debug=True)
