import React, { useEffect, useState } from "react";
import "./AskQuestion.css";

function AskQuestion() {
    const [question, setQuestion] = useState("");
    const [pdfFile, setPdfFile] = useState(null);
    const [chatHistory, setChatHistory] = useState([]);
    const [fileId, setFileId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const apiUrl = process.env.REACT_APP_API_URL;

    useEffect(() => {
        const fetchUploadedFiles = async () => {
            try {
                const response = await fetch(`${apiUrl}/files`);
                if (response.ok) {
                    const data = await response.json();
                    setUploadedFiles(data);
                }
            } catch (error) {
                console.error("Fetch error:", error);
            }
        };
        fetchUploadedFiles();
    }, []);

    useEffect(() => {
        console.log(uploadedFiles);
    }, [uploadedFiles]);


    const handleFileChange = (e) => {
        setPdfFile(e.target.files[0]);
    };


    const handleDelete = async (fileId) => {
        try {   
            const response = await fetch(`${apiUrl}/files/${fileId}`, {
                method: "DELETE",
            });

            if (response.ok) {
                const newFiles = uploadedFiles.filter((file) => file.id !== fileId);
                setUploadedFiles(newFiles);
            }

        } catch (error) {
            console.error("Fetch error:", error);
        }
    };

    const Upload = async () => {
        if(!pdfFile) {
            alert("Please upload a PDF file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", pdfFile);

        setLoading(true);
        try{
            const res = await fetch(`${apiUrl}/upload`, {
                method: "POST",
                body: formData,
            })

            if (res.ok) {
                const data = await res.json();
                setFileId(data.Id);
            } else {
                alert("An error occurred while uploading the file.");
            }
         } finally {
            setLoading(false);
        }
    };

    const handleAsk = async () => {
        if (loading) {
            return;
        }

        if (!fileId) {
            alert("Please upload the PDF file first.");
            return;
        }

        const formData = new FormData();
        formData.append("file_id", fileId);
        formData.append("question", question);

        setLoading(true);

        const currentChatHistory = [...chatHistory];
        const newChat = { question, answer: "Loading..." };

        setChatHistory([...currentChatHistory, newChat]);
        setQuestion("");

        try {
            const response = await fetch(`${apiUrl}/ask`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                const errorMsg = errorData.detail || "An error occurred.";
                setChatHistory([...currentChatHistory, { question, answer: `Error: ${errorMsg}` }]);
                return;
            }

            const data = await response.json();
            const answerText = data.answer || "No relevant answer found.";

            const newAnswer = { question, answer: answerText };
            setChatHistory([...currentChatHistory, newAnswer]);
        } catch (error) {
            console.error("Fetch error:", error);
            setChatHistory([...currentChatHistory, { question, answer: "An error occurred while fetching the answer." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="ask-question-container">
            {!fileId ? (
                <div>                    
                    <div>
                        <h2>Upload a FIle</h2>
                        <input type="file" accept=".pdf" onChange={handleFileChange} />
                    <button onClick={Upload} disabled={loading}>
                        {loading? "Uploadin..." : "Upload"}
                    </button>
                </div>
                    <div>
                        <h2>Uploaded Files</h2>
                        <ul>
                            {uploadedFiles?.map((file) => (
                                <li key={file.id} >
                                    <div onClick={() => setFileId(file.id)}>
                                        {file.name}
                                    </div>
                                    <button onClick={() => handleDelete(file.id)}>
                                        Delete
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

            ) : (
                <div className="chat-box">
                    <div className="chat-history">
                        {chatHistory.map((chat, index) => (
                            <div key={index} className="chat-message">
                                <div className="question">You: {chat.question}</div>
                                <div className="answer">AI: {chat.answer}</div>
                            </div>
                        ))}
                    </div>
                    <div className="input-section">
                        <input
                            type="text"
                            placeholder="Ask a question..."
                            value={question}
                            disabled={loading}
                            onChange={(e) => setQuestion(e.target.value)}
                        />
                        <button onClick={handleAsk} disabled={loading}>
                            {loading ? "Asking..." : "Ask"}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default AskQuestion; 