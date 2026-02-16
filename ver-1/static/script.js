// HTML elementlerini seç
const form = document.getElementById("uploadForm");
const fileInput = document.getElementById("excel_file");
const messageDiv = document.getElementById("message");
const fileNameDiv = document.getElementById("fileName"); // Dosya adı gösterecek div

// Dosya seçildiğinde adı göster
fileInput.addEventListener("change", function() {
    if (fileInput.files.length > 0) {
        fileNameDiv.textContent = "Seçilen dosya: " + fileInput.files[0].name;
    } else {
        fileNameDiv.textContent = "Henüz dosya seçilmedi";
    }
});

// Form gönderildiğinde PDF oluştur
form.addEventListener("submit", async function(e) {
    e.preventDefault();

    if (!fileInput.files.length) {
        messageDiv.textContent = "Lütfen bir Excel dosyası seçin!";
        return;
    }

    const formData = new FormData();
    formData.append("excel_file", fileInput.files[0]);

    messageDiv.textContent = "Rapor hazırlanıyor, lütfen bekleyin...";

    try {
        const response = await fetch("/upload-excel", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Dosya yüklenirken bir hata oluştu.");
        }

        // PDF dosyasını indir
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "Finansal_Analiz_Raporu.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        messageDiv.textContent = "PDF başarıyla indirildi!";
    } catch (err) {
        messageDiv.textContent = "Hata: " + err.message;
    }
});
