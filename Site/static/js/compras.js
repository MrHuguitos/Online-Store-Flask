document.addEventListener("DOMContentLoaded", function() {
    const botoesAvaliar = document.querySelectorAll('.avaliar');
    const modais = document.querySelectorAll('dialog');
    const botoesFechar = document.querySelectorAll('.fechar');

    // Adicionar eventos para cada botão de avaliar
    botoesAvaliar.forEach((botao, index) => {
        botao.addEventListener('click', () => {
            modais[index].showModal();
        });
    });

    // Adicionar eventos para cada botão de fechar
    botoesFechar.forEach((botaoFechar, index) => {
        botaoFechar.addEventListener('click', () => {
            modais[index].close();
        });
    });

    // Adicionar eventos para as estrelas de avaliação
    const estrelas = document.querySelectorAll('.estrelas');
    estrelas.forEach((grupoEstrelas) => {
        const radios = grupoEstrelas.querySelectorAll('input[type="radio"]');
        const labels = grupoEstrelas.querySelectorAll('.star');
        let selectedStarIndex = -1;

        // Função para destacar todas as estrelas até o índice `i`
        const highlightStars = (i) => {
            for (let j = 0; j <= i; j++) {
                labels[j].style.color = 'var(--cor_estrela_2)';
            }
            for (let j = i + 1; j < labels.length; j++) {
                labels[j].style.color = '#ddd';
            }
        };

        // Função para restaurar as cores das estrelas
        const resetStars = () => {
            if (selectedStarIndex >= 0) {
                highlightStars(selectedStarIndex);
            } else {
                labels.forEach(label => {
                    label.style.color = '#ddd';
                });
            }
        };

        labels.forEach((label, i) => {
            label.addEventListener('mouseover', () => {
                highlightStars(i);
            });

            label.addEventListener('mouseout', () => {
                resetStars();
            });

            label.addEventListener('click', () => {
                selectedStarIndex = i;
                radios[i].checked = true;
                highlightStars(i);
            });
        });

        resetStars(); // Inicialização para garantir que as estrelas corretas estejam destacadas inicialmente
    });
});