from flask import Flask, request, render_template
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Carregar os dados
        data = pd.read_csv(filepath)
        
        # Calcular Resíduos Per Capita
        data['Resíduos Per Capita'] = data['Volume(kg)'] / data['Populacao']
        
        # Calcular Caminhões Per Capita
        data['Caminhões Per Capita'] = data['Quantidade de caminhões por dia'] / data['Populacao']
        
        # Arredondar os valores para 2 casas decimais
        data['Resíduos Per Capita'] = data['Resíduos Per Capita'].round(2)
        data['Caminhões Per Capita'] = data['Caminhões Per Capita'].round(2)
        
        # Filtrar resíduos recicláveis
        reciclaveis = data[data['Reciclável'] == 'Sim']['Volume(kg)'].sum()
        
        # Volume total de resíduos
        total_residuos = data['Volume(kg)'].sum()
        
        # Calcular Percentual de Resíduos Recicláveis
        percentual_reciclaveis = (reciclaveis / total_residuos) * 100
        
        # Gráfico de Barras - Volume de Resíduos por Tipo
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Tipo do resíduo', y='Volume(kg)', data=data, ci=None)
        plt.title('Volume de Resíduos por Tipo')
        plt.xlabel('Tipo do Resíduo')
        plt.ylabel('Volume (kg)')
        bar_graph = io.BytesIO()
        plt.savefig(bar_graph, format='png')
        bar_graph.seek(0)
        bar_graph_url = base64.b64encode(bar_graph.getvalue()).decode('utf8')
        
        # Gráfico de Pizza - Percentual de Resíduos Recicláveis
        plt.figure(figsize=(8, 8))
        reciclaveis_data = [reciclaveis, total_residuos - reciclaveis]
        labels = ['Recicláveis', 'Não Recicláveis']
        plt.pie(reciclaveis_data, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title('Percentual de Resíduos Recicláveis')
        pie_chart = io.BytesIO()
        plt.savefig(pie_chart, format='png')
        pie_chart.seek(0)
        pie_chart_url = base64.b64encode(pie_chart.getvalue()).decode('utf8')
        
        # Preparar os resultados
        table_data = data[['Localização', 'Resíduos Per Capita', 'Caminhões Per Capita']].head(10).to_dict(orient='records')
        results = {
            'percentual_reciclaveis': f'{percentual_reciclaveis:.2f}',
            'table': table_data,
            'bar_graph': bar_graph_url,
            'pie_chart': pie_chart_url
        }
        
        return render_template('index.html', results=results)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)