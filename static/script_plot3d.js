document.addEventListener("DOMContentLoaded", () => {
  const resultsPlots = document.getElementById("results-plots");
  const toggleFeature = document.getElementById("toggle-feature");
  const featureLabel = document.getElementById("feature-label");
  const downloadButton = document.getElementById("download-button");
  const backButton = document.getElementById("back-button");

  let currentFeature = "SPI";

  function fetchAndRenderGraph(feature) {
    fetch("http://localhost:5001/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feature }),
    })
      .then((response) => {
        if (!response.ok) throw new Error("Error al actualizar el gráfico.");
        return response.json();
      })
      .then((data) => {
        const graphData = JSON.parse(data.graph);
        Plotly.react(resultsPlots, graphData.data, graphData.layout);

        // Configurar botón de descarga
        downloadButton.onclick = () => {
          window.location.href = `/download/${data.predictions_path.split("/").pop()}`;
        };
      })
      .catch((error) => {
        console.error(error);
        alert("Error al actualizar el gráfico.");
      });
  }

  // Renderizar gráfico inicial
  fetchAndRenderGraph(currentFeature);

  // Cambiar entre SPI y BWI
  toggleFeature.addEventListener("change", () => {
    currentFeature = toggleFeature.checked ? "BWI" : "SPI";
    featureLabel.textContent = currentFeature;
    fetchAndRenderGraph(currentFeature);
  });

  // Volver a la página principal
  backButton.addEventListener("click", () => {
    window.location.href = "/";
  });
});