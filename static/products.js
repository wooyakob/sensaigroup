document.addEventListener("DOMContentLoaded", function() {

    // File Drop Zone
    const dropzone = document.getElementById("dropzone");
    
    dropzone.addEventListener("dragover", event => {
        event.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", event => {
        event.preventDefault();
        dropzone.classList.remove("dragover");
        const file = event.dataTransfer.files[0];
        if(file.type === "application/pdf") {
            uploadFile(file);
        } else {
            alert("Only PDF files are allowed.");
        }
    });

    // File Input Change
    document.getElementById("fileInput").addEventListener("change", event => {
        const file = event.target.files[0];
        if(file.type === "application/pdf") {
            uploadFile(file);
        } else {
            alert("Only PDF files are allowed.");
        }
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
            console.log(data);
            if (data.error) {
                alert(data.error);
            } else if (data.text) {
                alert(data.text);
            } else if (data.text_file) {
                document.getElementById("textFilePath").value = data.text_file;
                alert("File uploaded and processed successfully.");
            }
        })
        .catch(error => {
            console.error("Error uploading file:", error);
        });
    }

});