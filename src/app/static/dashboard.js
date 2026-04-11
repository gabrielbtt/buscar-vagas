document.addEventListener("DOMContentLoaded", () => {
  const runNowBtn = document.getElementById("run-now-btn");
  const runResult = document.getElementById("run-result");

  if (!runNowBtn || !runResult) {
    return;
  }

  runNowBtn.addEventListener("click", async () => {
    runNowBtn.disabled = true;
    runNowBtn.textContent = "Buscando...";
    runResult.textContent = "Executando coleta manual...";

    try {
      const response = await fetch("/ui/run-now", { method: "POST" });
      const result = await response.json();
      runResult.textContent = result.message;
      setTimeout(() => {
        window.location.reload();
      }, 1800);
    } catch (error) {
      console.error("Erro ao buscar vagas:", error);
      runResult.textContent = "Falha na execucao manual. Veja o log da aplicacao.";
    } finally {
      runNowBtn.disabled = false;
      runNowBtn.textContent = "Buscar agora";
    }
  });
});
