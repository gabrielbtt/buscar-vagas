document.addEventListener("DOMContentLoaded", () => {
  const addProfileBtn = document.getElementById("add-profile-btn");
  const profilesContainer = document.getElementById("profiles-container");
  const profileTemplate = document.getElementById("profile-template");
  const runNowBtn = document.getElementById("run-now-btn");
  const runResult = document.getElementById("run-result");

  if (addProfileBtn) {
    addProfileBtn.addEventListener("click", () => {
      const newId = "new_" + Date.now();
      const content = profileTemplate.innerHTML.replace(/NEWID/g, newId);
      const div = document.createElement("div");
      div.innerHTML = content;
      profilesContainer.appendChild(div.firstElementChild);
    });
  }

  if (runNowBtn) {
    runNowBtn.addEventListener("click", async () => {
      runNowBtn.disabled = true;
      runNowBtn.textContent = "Buscando...";
      runResult.textContent = "Processando...";
      runResult.style.color = "var(--text)";

      try {
        const response = await fetch("/ui/run-now", { method: "POST" });
        const result = await response.json();
        
        runResult.textContent = `Sucesso! Encontradas: ${result.fetched_jobs}, Novas: ${result.notified_jobs}`;
        runResult.style.color = "#28a745";
        
        // Recarregar após 3 segundos para mostrar as novas vagas se houver
        setTimeout(() => {
          window.location.reload();
        }, 3000);
      } catch (error) {
        console.error("Erro ao buscar vagas:", error);
        runResult.textContent = "Erro na busca.";
        runResult.style.color = "#dc3545";
      } finally {
        runNowBtn.disabled = false;
        runNowBtn.textContent = "Buscar agora";
      }
    });
  }
});
