import React, { useState } from 'react';

function UploadPDF() {
    const [file, setFile] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        const formData = new FormData();
        formData.append("file", file);
    
        try {
            const response = await fetch("http://127.0.0.1:8000/upload", {
                method: "POST",
                body: formData,
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
    
            const data = await response.json();
            alert(data.message);
        } catch (error) {
            console.error("Error:", error);
            alert("Failed to upload the PDF. Please try again.");
        }
    };
    
    

    return (
        <div>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload PDF</button>
        </div>
    );
}

export default UploadPDF;
