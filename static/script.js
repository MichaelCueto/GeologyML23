document.addEventListener("DOMContentLoaded", () => {
  const fileUploadForm = document.getElementById("files-upload");
  const resultsPlots = document.getElementById("results-plots");
  const notifications = document.getElementById("notifications");

  // Función para mostrar notificaciones temporales
  function showNotification(message) {
    const notifications = document.getElementById("notifications");
    if (!notifications) {
      console.error("Contenedor de notificaciones no encontrado.");
      return;
    }

    const notification = document.createElement("div");
    notification.className = "notification";
    notification.textContent = message;

    notifications.appendChild(notification);

    setTimeout(() => {
      notifications.removeChild(notification);
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
        console.log("Resultados del procesamiento:", data);
        showNotification("Procesamiento completado con éxito.");
      })
      .catch((error) => {
        console.error("Error en el flujo de archivos:", error);
        alert(`Error: ${error.message}`);
      });
  });
});