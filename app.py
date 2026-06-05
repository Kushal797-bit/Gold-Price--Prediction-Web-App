# app.py — FULL UPGRADED VERSION

import pickle
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
from flask import Flask, render_template, request,jsonify
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

app = Flask(__name__)

# ── Load your model ──────────────────────────────────────────────
model = pickle.load(open('model/model.pkl', 'rb'))

# ── Load dataset to generate the graph ──────────────────────────
# Replace 'gld_price_data.csv' with your actual CSV file name
df = pd.read_csv('gld_price_data.csv')
df.dropna(inplace=True)

# These are the features your model was trained on — adjust if different
X = df[['SPX', 'USO', 'SLV', 'EUR/USD']]
y = df['GLD']

# Split exactly like you did in your notebook
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Get predictions on test set
y_pred = model.predict(X_test)

# ── Calculate metrics ────────────────────────────────────────────
r2  = round(r2_score(y_test, y_pred), 4)
mae = round(mean_absolute_error(y_test, y_pred), 2)
mse = round(mean_squared_error(y_test, y_pred), 2)

# ── Build Actual vs Predicted chart ─────────────────────────────
def build_prediction_graph():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=y_test.values,
        mode='lines',
        name='Actual Price',
        line=dict(color='#00d4aa', width=2)
    ))
    fig.add_trace(go.Scatter(
        y=y_pred,
        mode='lines',
        name='Predicted Price',
        line=dict(color='#ff6b6b', width=2, dash='dash')
    ))
    fig.update_layout(
        title='Actual vs Predicted Gold Prices (Test Set)',
        xaxis_title='Data Points',
        yaxis_title='Gold Price (USD)',
        plot_bgcolor='#1a1a2e',
        paper_bgcolor='#16213e',
        font=dict(color='#e0e0e0'),
        legend=dict(bgcolor='#1a1a2e', bordercolor='#444'),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return pio.to_html(fig, full_html=False)

# ── Build Feature Importance chart ──────────────────────────────
def build_feature_graph():
    features = ['SPX', 'USO', 'SLV', 'EUR/USD']
    importances = model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]

    fig = go.Figure(go.Bar(
        x=[features[i] for i in sorted_idx],
        y=[importances[i] for i in sorted_idx],
        marker_color=['#00d4aa', '#4e9af1', '#ff6b6b', '#ffd700']
    ))
    fig.update_layout(
        title='Feature Importance — What Drives Gold Price?',
        xaxis_title='Feature',
        yaxis_title='Importance Score',
        plot_bgcolor='#1a1a2e',
        paper_bgcolor='#16213e',
        font=dict(color='#e0e0e0'),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return pio.to_html(fig, full_html=False)

# ── Routes ───────────────────────────────────────────────────────
@app.route('/')
def home():
    pred_graph    = build_prediction_graph()
    feature_graph = build_feature_graph()
    return render_template('index.html',
                           pred_graph=pred_graph,
                           feature_graph=feature_graph,
                           r2=r2, mae=mae, mse=mse,
                           prediction=None)

@app.route('/predict', methods=['POST'])
def predict():
    values = [float(x) for x in request.form.values()]
    prediction = round(model.predict([values])[0], 2)

    pred_graph    = build_prediction_graph()
    feature_graph = build_feature_graph()

    return render_template('index.html',
                           pred_graph=pred_graph,
                           feature_graph=feature_graph,
                           r2=r2, mae=mae, mse=mse,
                           prediction=prediction)

@app.route('/predict_api', methods=['GET'])
def predict_api():

    data = request.get_json()

    spx = float(data['SPX'])
    uso = float(data['USO'])
    slv = float(data['SLV'])
    eur_usd = float(data['EUR_USD'])

    prediction = model.predict([[spx, uso, slv, eur_usd]])

    return jsonify({
        "message":"API working"})
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)