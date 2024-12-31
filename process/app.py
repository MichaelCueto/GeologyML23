from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS 
import os
import plotly.express as px
from predict import use_predict  # Importa tu lógica de predicción

# Inicialización de Flask
app = Flask(__name__, static_folder="../static", template_folder="../templates")
CORS(app)

# Asegúrate de que exista la carpeta de subidas
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

# Ruta para servir la página principal
@app.route("/")
def index():
    return render_template("index.html")

# Ruta para manejar la subida de archivos
@app.route("/uploads", methods=["POST"])
def upload_files():
    try:
        if "csv" not in request.files:
            return jsonify({"error": "Falta el archivo CSV"}), 400

        # Guardar el archivo CSV
        csv_file = request.files["csv"]
        csv_path = os.path.join(UPLOAD_FOLDER, secure_filename(csv_file.filename))
        csv_file.save(csv_path)

        # Guardar los modelos
        model_files = request.files.getlist("models")
        model_paths = []
        for model_file in model_files:
            if model_file.filename.endswith(".pkl"):
                model_path = os.path.join(UPLOAD_FOLDER, secure_filename(model_file.filename))
                model_file.save(model_path)
                model_paths.append(model_path)

        # Confirmar subida
        return jsonify({"csv_path": csv_path, "model_paths": model_paths})
    except Exception as e:
        return jsonify({"error": f"Error al subir los archivos: {str(e)}"}), 500

# Ruta para procesar los archivos
@app.route("/process", methods=["POST"])
def process_files():
    try:
        data = request.json
        csv_path = data.get("csv_path")
        model_paths = data.get("model_paths")
        feature_to_plot = data.get("feature", "SPI") # SPI es el valor por defecto

        if not csv_path or not model_paths:
            return jsonify({"error": "Faltan rutas para procesar"}), 400

        # Verificar que los archivos existen
        if not os.path.exists(csv_path):
            return jsonify({"error": f"El archivo CSV no existe: {csv_path}"}), 400

        for model_path in model_paths:
            if not os.path.exists(model_path):
                return jsonify({"error": f"El modelo no existe: {model_path}"}), 400

        print(f"Procesando archivo CSV: {csv_path}")
        print(f"Procesando modelos: {model_paths}")
        # Procesar los archivos con la lógica de predicción

        # Realizar las predicciones
        predictor = use_predict(root_data=csv_path, root_model=os.path.dirname(model_paths[0]))
        resultados = predictor.Use_Model_RF()


        # Guardar los resultados como un CSV
        predictions_path = os.path.join(UPLOAD_FOLDER, 'predicciones.csv')
        resultados.to_csv(predictions_path, index=False)
        print(f"Resultados guardados en: {predictions_path}")

        # Crear gráfico 3D con Plotly
        if feature_to_plot == 'SPI':
            feature = 'SPI'
        elif feature_to_plot == 'BWI':
            feature = 'BWI'
        else: 
            return jsonify({"error": f"Feature inválido: {feature_to_plot}"}), 400

        fig = px.scatter_3d(resultados, x='X', y='Y', z='Z', color=feature,
                            title=f'Grafico 3D para {feature}',
                            labels={feature: feature},
                            color_continuous_scale='Viridis')
        graph_json = fig.to_json()

        return jsonify({
            "message" : "Procesamiento exitoso",
            "graph": graph_json,
            "predictions_path": predictions_path})

    except Exception as e:
        return jsonify({"error": f"Error al procesar los archivos: {str(e)}"}), 500

# Ruta para descargar resultados
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "Archivo no encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)