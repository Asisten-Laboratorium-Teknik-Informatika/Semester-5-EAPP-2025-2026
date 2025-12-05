// --- LOGIC GAMBAR ---
let fileBase64 = null; // Menyimpan data gambar
let fileName = null;

function bacaGambar(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            // PERBAIKAN: Sesuaikan ID dengan yang ada di add.html dan edit.html
            let imgPreview = document.getElementById('preview');
            let iconCam = document.getElementById('icon-cam');

            if(imgPreview) {
                imgPreview.src = e.target.result;
                imgPreview.style.display = 'block';
            }
            
            if(iconCam) {
                iconCam.style.display = 'none';
            }
            
            // Simpan data untuk dikirim ke python
            fileBase64 = e.target.result;
            fileName = input.files[0].name;
        };
        reader.readAsDataURL(input.files[0]);
    }
}