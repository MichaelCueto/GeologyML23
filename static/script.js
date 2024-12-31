document.addEventListener("DOMContentLoaded", () => {
  const fileUploadForm = document.getElementById("files-upload");
  const resultsPlots = document.getElementById("results-plots");
  const uploadScreen = document.getElementById("upload-screen");
  const resultsScreen = document.getElementById("results-screen");
  const downloadButton = document.getElementById("download-button");
  const backButton = document.getElementById("back-button");

  // Asegurarse de que el contenedor de notificaciones esté en el DOM
  function ensureNotificationContainer() {
    let notifications = document.getElementById("notifications");
    if (!notifications) {
      notifications = document.createElement("div");
      notifications.id = "notifications";
      notifications.style.position = "fixed";
      notifications.style.top = "10px";
      notifications.style.right = "10px";
      notifications.style.zIndex = "1000";
      notifications.style.width = "300px";
      document.body.appendChild(notifications);
    }
    return notifications;
  }

  // Función para mostrar notificaciones temporales
  function showNotification(message) {
    const notifications = ensureNotificationContainer();

    const notification = document.createElement("div");
    notification.className = "notification";
    notification.textContent = message;
    notification.style.backgroundColor = "#333";
    notification.style.color = "#fff";
    notification.style.padding = "10px";
    notification.style.marginBottom = "10px";
    notification.style.borderRadius = "5px";
    notification.style.boxShadow = "0px 4px 6px rgba(0, 0, 0, 0.2)";
    notification.style.animation = "fadeOut 3s forwards";

    notifications.appendChild(notification);

    setTimeout(() => {
      if (notifications.contains(notification)) {
        notifications.removeChild(notification);
      }
    }, 3000);
  }

  // Subir archivos y procesarlos al hacer clic en el botón
  fileUploadForm.addEventListener("submit", (event) => {
    event.preventDefault();

    // Validar archivos seleccionados
    const csvFile = document.getElementById("csv-file").files[0];
    const modelFiles = document.getElementById("model-folder").files;

    if (!csvFile) {
      alert("Por favor, selecciona un archivo CSV.");
      return;
    }

    if (modelFiles.length === 0) {
      alert("Por favor, selecciona al menos un modelo (.pkl).");
      return;
    }

    // Preparar los archivos en FormData
    const formData = new FormData();
    formData.append("csv", csvFile);
    console.log("Archivo CSV seleccionado:", csvFile.name);

    for (const file of modelFiles) {
      if (file.name.endsWith(".pkl")) {
        formData.append("models", file);
        console.log("Modelo añadido:", file.name);
      } else {
        console.warn(`Archivo ignorado (no es .pkl): ${file.name}`);
      }
    }

    // Enviar archivos al backend para subirlos
    fetch("http://localhost:5001/uploads", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((errorData) => {
            throw new Error(errorData.error || "Error desconocido al subir los archivos.");
          });
        }
        return response.json();
      })
      .then((data) => {
        console.log("Archivos subidos con éxito:", data);
        showNotification("Archivos subidos correctamente.");

        // Llama automáticamente al endpoint de procesamiento
        return fetch("http://localhost:5001/process", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            csv_path: data.csv_path,
            model_paths: data.model_paths,
          }),
        });
      })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((errorData) => {
            throw new Error(errorData.error || "Error desconocido al procesar los archivos.");
          });
        }
        return response.json();
      })
      .then((data) => {
        // Mostrar resultados
        const graph = JSON.parse(data.graph);
        Plotly.newPlot(resultsPlots, graph.data, graph.layout);

        // Configurar descarga
        downloadButton.onclick = () => {
          window.location.href = `/download/${data.predictions_path.split("/").pop()}`;
        };

        // Cambiar pantalla
        uploadScreen.classList.add("hidden");
        resultsScreen.classList.remove("hidden");
      })
      .catch((error) => {
        console.error("Error en el flujo de archivos:", error);
        alert(`Error: ${error.message}`);
      });
  });

  backButton.addEventListener("click", () => {
    resultsScreen.classList.add("hidden");
    uploadScreen.classList.remove("hidden");
  });
});