from flask import Flask, render_template, request, jsonify, send_from_directory, session
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import plotly.express as px
from predict import use_predict

# Inicialización de Flask
app = Flask(__name__, static_folder="../static", template_folder="../templates")
app.secret_key = "your_secret_key"  # Necesario para usar sesiones
CORS(app)

# Configuración de carpeta de subidas
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ruta para la página principal (subida de archivos)
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

        model_files = request.files.getlist("model")
        model_paths = []
        for model_file in model_files:
            if model_file.filename.endswith(".pkl"):
                model_path = os.path.join(UPLOAD_FOLDER, secure_filename(model_file.filename))
                model_file.save(model_path)
                model_paths.append(model_path)
                print(f"Modelo guardado en: {model_path}")

        # Guardar en la sesión
        session["csv_path"] = csv_path
        session['model_paths'] = model_paths

        print(f"CSV guardado en: {csv_path}")
        print(f"Modelos guardados en: {model_paths}")

        return jsonify({"csv_path": csv_path, "model_paths": model_paths})
    except Exception as e:
        return jsonify({"error": f"Error al subir los archivos: {str(e)}"}), 500

# Ruta para procesar los archivos
@app.route("/process", methods=["POST"])
def process_files():
    try:
        # Recuperar los datos de la sesión y del JSON enviado
        csv_path = session.get("csv_path")
        feature_to_plot = request.json.get("feature", "SPI")

        print(f"csv_path desde la sesión: {csv_path}")
        print(f"Feature solicitado: {feature_to_plot}")

        if not csv_path:
            print("Error: Faltan rutas para procesar (csv_path es None)")
            return jsonify({"error": "Falta la ruta del archivo CSV"}), 400

        # Resto de la lógica...
        predictor = use_predict(root_data=csv_path, root_model=UPLOAD_FOLDER)
        resultados = predictor.Use_Model_RF()

        predictions_path = os.path.join(UPLOAD_FOLDER, "predicciones.csv")
        resultados.to_csv(predictions_path, index=False)

        # Crear gráfico 3D
        fig = px.scatter_3d(resultados, x="X", y="Y", z="Z", color=feature_to_plot,
                            title=f"Gráfico 3D para {feature_to_plot}",
                            labels={feature_to_plot: feature_to_plot},
                            color_continuous_scale="Viridis")
        graph_json = fig.to_json()

        return jsonify({
            "message": "Procesamiento exitoso",
            "graph": graph_json,
            "predictions_path": os.path.join(UPLOAD_FOLDER, "predicciones.csv"),
        })

    except Exception as e:
        print(f"Error en /process: {e}")
        return jsonify({"error": f"Error al procesar los archivos: {str(e)}"}), 500

# Ruta para servir la página del gráfico 3D
@app.route("/plot3d")
def plot3d():
    return render_template("plot3d.html")

# Ruta para descargar los resultados
@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "Archivo no encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)