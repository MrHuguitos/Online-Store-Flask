document.addEventListener("DOMContentLoaded", function() {
    // Abrir e fechar o dialog de confirmação de dados
    const button = document.querySelector(".avaliacao-geral")
    const modal = document.querySelector("dialog")
    const buttonClose = document.querySelector(".fechar")

    button.onclick = function() {
        modal.showModal()
    }
    buttonClose.onclick = function() {
        modal.close()
    }
});