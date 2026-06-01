from flask import Flask, render_template, request
import numpy as np
import pickle

app = Flask(__name__)

# Load trained model
model = pickle.load(open('model/model.pkl', 'rb'))

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=['POST'])
def predict():

    spx = float(request.form['SPX'])
    uso = float(request.form['USO'])
    slv = float(request.form['SLV'])
    eurusd = float(request.form['EURUSD'])

    features = np.array([[spx, uso, slv, eurusd]])

    prediction = model.predict(features)

    output = round(prediction[0], 2)

    return render_template(
        "index.html",
        prediction_text=f"Predicted Gold Price: {output}"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)