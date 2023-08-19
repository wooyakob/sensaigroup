document.addEventListener("DOMContentLoaded", function() {

    // File Drop Zone
    const dropzone = document.getElementById("dropzone");
    dropzone.addEventListener("dragover", event => {
        event.preventDefault();
        dropzone.classList.add("hover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("hover");
    });

    dropzone.addEventListener("drop", event => {
        event.preventDefault();
        dropzone.classList.remove("hover");
        const file = event.dataTransfer.files[0];
        uploadFile(file);
    });

    // File Input Change
    document.getElementById("fileInput").addEventListener("change", event => {
        const file = event.target.files[0];
        uploadFile(file);
    });

    // AJAX Upload
    function uploadFile(file) {
        const formData = new FormData();
        formData.append("file", file);
        
        fetch("/upload_endpoint", {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // Handle the response data here
            console.log(data);
            if (data.error) {
                alert(data.error);
            } else if (data.text) {
                alert(data.text);
            }
        })
        .catch(error => {
            console.error("Error uploading file:", error);
        });
    }

});