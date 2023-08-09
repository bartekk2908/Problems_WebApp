// Pobranie referencji do edytora tekstu i inputu do wyboru obrazków
const editor = document.getElementById("editor");
const imageInput = document.getElementById("imageInput");

// Obsługa wstawiania obrazków po wybraniu pliku
imageInput.addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = document.createElement("img");
            img.src = e.target.result;
            editor.appendChild(img);
        };
        reader.readAsDataURL(file);
    }
});

// Obsługa wstawiania obrazków po przeciągnięciu i upuszczeniu
editor.addEventListener("dragover", function (e) {
    e.preventDefault();
});
editor.addEventListener("drop", function (e) {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = document.createElement("img");
            img.src = e.target.result;
            editor.appendChild(img);
        };
        reader.readAsDataURL(file);
    }
});
