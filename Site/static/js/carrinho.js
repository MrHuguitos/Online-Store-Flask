document.addEventListener("DOMContentLoaded", function() {
    const updateQuantity = (element, increment) => {
        const quantityElement = element.parentElement.querySelector("span");
        let quantity = parseInt(quantityElement.textContent);
        if (increment) {
            quantity++;
        } else {
            if (quantity > 1) quantity--; // Ensure quantity doesn't go below 1
        }
        quantityElement.textContent = quantity;

        // Make an AJAX call to update the quantity in the backend
        const productId = element.dataset.productId;
        fetch('/update-quantity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({product_id: productId, quantity: quantity})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateTotal();
            } else {
                console.error('Error updating quantity:', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };

    const updateTotal = () => {
        let total = 0;
        document.querySelectorAll(".carrinho-item").forEach(item => {
            const priceElement = item.querySelector(".preco p");
            const quantityElement = item.querySelector(".contador span");
            const price = parseFloat(priceElement.textContent.replace('R$ ', '').replace(',', '.'));
            const quantity = parseInt(quantityElement.textContent);
            total += price * quantity;
        });
        document.querySelector(".pagar").textContent = `Pagar R$ ${total.toFixed(2).replace('.', ',')}`;
    };

    document.querySelectorAll(".bx-plus").forEach(element => {
        element.addEventListener("click", () => {
            updateQuantity(element, true);
        });
    });

    document.querySelectorAll(".bx-minus").forEach(element => {
        element.addEventListener("click", () => {
            updateQuantity(element, false);
        });
    });

    // Initial calculation of the total
    updateTotal();

    // Abrir e fechar o dialog de confirmação de dados
    const button = document.querySelector(".pagar")
    const modal = document.querySelector("dialog")
    const buttonClose = document.querySelector(".fechar")

    button.onclick = function() {
        modal.showModal()
    }
    buttonClose.onclick = function() {
        modal.close()
    }
});