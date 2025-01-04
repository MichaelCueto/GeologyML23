document.addEventListener("DOMContentLoaded", () => {
  const fileUploadForm = document.getElementById("files-upload");

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
  function showNotification(message, type = "success") {
    const notifications = ensureNotificationContainer();

    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.backgroundColor = type === "error" ? "#e74c3c" : "#2ecc71";
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

  // Subir archivos y procesarlos
  fileUploadForm.addEventListener("submit", (event) => {
    event.preventDefault();

    // Validar archivos seleccionados
    const csvFile = document.getElementById("csv-file").files[0];
    const modelFiles = document.getElementById("model-folder").files;

    if (!csvFile) {
      showNotification("Por favor, selecciona un archivo CSV.", "error");
      return;
    }

    if (modelFiles.length === 0) {
      showNotification("Por favor, selecciona al menos un modelo (.pkl).", "error");
      return;
    }

    // Preparar los archivos en FormData
    const formData = new FormData();
    formData.append("csv", csvFile);
    console.log("Archivo CSV seleccionado:", csvFile.name);

    for (const file of modelFiles) {
      if (file.name.endsWith(".pkl")) {
        formData.append("model", file); // Clave "model" para los archivos .pkl
        console.log("Modelo añadido:", file.name);
      } else {
        console.warn(`Archivo ignorado (no es .pkl): ${file.name}`);
      }
    }

    // Enviar archivos al backend para subirlos
    fetch("http://localhost:8081/uploads", {
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

        // Guardar las rutas relevantes en el sessionStorage para usar en la página de gráficos
        sessionStorage.setItem("csvPath", data.csv_path);
        sessionStorage.setItem("modelPaths", JSON.stringify(data.model_paths));

        // Redirigir a plot3d.html
        window.location.href = "/plot3d";
      })
      .catch((error) => {
        console.error("Error al subir archivos:", error);
        showNotification(`Error: ${error.message}`, "error");
      });
  });
});