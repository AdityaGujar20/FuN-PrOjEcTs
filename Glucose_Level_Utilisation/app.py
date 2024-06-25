from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ANALYZED_FOLDER = 'analyzed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ANALYZED_FOLDER'] = ANALYZED_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        return redirect('/')
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        analyzed_file_path = analyze_file(file_path)
        return send_file(analyzed_file_path, as_attachment=True)

def analyze_file(file_path):
    df = pd.read_csv(file_path)
    df['Subject_ID'] = df['Subject_ID'].str.split('.').str[0]
    df = df.dropna()
    df['Carb'] = df['RQ']*338.47-237.64
    df['EE'] = (((3.9*df['VO2'])+(1.1*df['VCO2']))*1440)*70/1000
    df['EE1'] = df['EE']*20/100
    df['EEA'] = df['EE'] - df['EE1']
    df['RQ-A'] = (df['RQ']-0.2)/0.8
    df['Carb-Oxid'] = df['RQ']*338.47-237.64
    df['EE_A-Carb'] = (df['EE']*(df['Carb-Oxid']/100))-(df['EE1']*(df['Carb-Oxid']/100))
    df['L of CO2/d_carb'] = df['EE_A-Carb']/5.05
    df['CO2 ml/min'] = df['L of CO2/d_carb']*1000/1440
    df['Kcal/min from glucose'] = (df['CO2 ml/min']*5.05)/1000
    df['Glucose utilise mg/min'] = df['Kcal/min from glucose']*1000/4
    df['Ratio UT/GT'] = df['Glucose utilise mg/min'] / df['GT_BGL']
    
    output_filename = 'analyzed_' + os.path.basename(file_path)
    output_path = os.path.join(app.config['ANALYZED_FOLDER'], output_filename)
    df.to_csv(output_path, index=False)
    return output_path

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(ANALYZED_FOLDER):
        os.makedirs(ANALYZED_FOLDER)
    app.run(debug=True)
