// Botões "Copiar" do Pix
document.querySelectorAll("[data-copiar]").forEach((botao) => {
  botao.addEventListener("click", async () => {
    const aviso = document.querySelector(".copiado");
    try {
      await navigator.clipboard.writeText(botao.dataset.copiar);
      aviso.textContent = "Copiado! Agora é só colar no app do seu banco.";
    } catch {
      aviso.textContent = "Não deu para copiar. Selecione a chave acima e copie.";
    }
  });
});
