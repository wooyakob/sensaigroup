document.addEventListener("DOMContentLoaded", function() {
    // File Drop Zone
    const dropzone = document.getElementById("dropzone");
    let selectedFile; // Temporary storage for the selected file

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
        handleFile(event.dataTransfer.files[0]);
    });

    // File Input Change
    document.getElementById("fileInput").addEventListener("change", event => {
        handleFile(event.target.files[0]);
    });

    function handleFile(file) {
        const allowedTypes = ["application/pdf", "text/plain", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];
        if (allowedTypes.includes(file.type)) {
            selectedFile = file;
            dropzone.innerText = "Selected File: " + selectedFile.name;  // Display the file name in the dropzone
        } else {
            alert("Only PDF, TXT, DOC, and DOCX files are allowed.");
            selectedFile = null;
        }
    }

    document.querySelector('form[action="/add_product"]').addEventListener("submit", (event) => {
        if (selectedFile) {
            event.preventDefault();
            uploadFile(selectedFile).then(() => {
                event.target.submit();
            }).catch(error => {
                console.error("Error uploading file:", error);
                alert("Error uploading file. Please try again.");
            });
        }
    });

    // AJAX Upload
    function uploadFile(file) {
        return new Promise((resolve, reject) => {
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
                if (data.error) {
                    alert(data.error);
                    reject(data.error);
                } else if (data.text_file) {
                    document.getElementById("textFilePath").value = data.text_file;
                    resolve();
                } else {
                    reject(new Error('Unknown error occurred.'));
                }
            })
            .catch(reject);
        });
    }
});