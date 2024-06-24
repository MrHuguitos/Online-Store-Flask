document.addEventListener("DOMContentLoaded", function() {
    // Seleciona o botão e o elemento onde os novos campos serão adicionados
    const botaoAdicionar = document.getElementById("adicionarCampo");
    const containerCampos = document.getElementById("camposExistentes");

    // Adiciona um ouvinte de evento para o botão
    botaoAdicionar.addEventListener("click", function() {
        // Cria um novo campo de input
        const novoCampo = document.createElement("input");
        novoCampo.type = "tel";
        novoCampo.name = "phone";
        novoCampo.id = "phone";
        novoCampo.placeholder = "(XX) XXXXX-XXXX";
        novoCampo.maxLength = "15";
        
        
        novoCampo.addEventListener("input", function() {
            formatarTelefone(novoCampo); // Chama a função formatarTelefone passando o campo atual
        });

        // Adiciona o novo campo ao contêiner
        containerCampos.appendChild(novoCampo);
    });

    // Função para formatar o telefone
    function formatarTelefone(input) {
        // Obtém o valor atual do input
        let valor = input.value;

        // Remove tudo que não é número do valor atual
        valor = valor.replace(/\D/g, "");

        // Verifica se o valor possui mais de 11 caracteres para formatar como celular
        if (valor.length > 12) {
            valor = valor.replace(/^(\d{2})(\d{5})(\d{4}).*/, "($1) $2-$3");
        } else {
            valor = valor.replace(/^(\d{2})(\d{5})(\d{4}).*/, "($1) $2-$3");
        }

        // Atualiza o valor do input formatado
        input.value = valor;
    }
});