const modalPhotoInput = document.getElementById("modal-photo-input");
const modalPhotoPreview = document.getElementById("modal-photo-preview");

if (modalPhotoInput && modalPhotoPreview) {
    modalPhotoInput.addEventListener("change", function () {
        const file = modalPhotoInput.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (event) {
            modalPhotoPreview.src = event.target.result;
        };
        reader.readAsDataURL(file);
    });
}