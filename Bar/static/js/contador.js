document.addEventListener('DOMContentLoaded', () => {
    const plusButtons = document.querySelectorAll('.plus');
    const minusButtons = document.querySelectorAll('.minus');
    const numSpans = document.querySelectorAll('.num');
    const cantidadInputs = document.querySelectorAll('.cantidad-input');

    plusButtons.forEach((button, index) => {
        button.addEventListener("click", () => {
            let value = parseInt(numSpans[index].innerText) + 1;
            numSpans[index].innerText = value.toString().padStart(2, '0');
            cantidadInputs[index].value = value;
        });
    });

    minusButtons.forEach((button, index) => {
        button.addEventListener("click", () => {
            let value = parseInt(numSpans[index].innerText);
            if (value > 1) {
                value -= 1;
                numSpans[index].innerText = value.toString().padStart(2, '0');
                cantidadInputs[index].value = value;
            }
        });
    });
});
