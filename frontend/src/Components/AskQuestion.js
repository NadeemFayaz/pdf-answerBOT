import React, { useState } from "react";
import "./AskQuestion.css";

function AskQuestion() {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [pdfFile, setPdfFile] = useState(null);
    const [chatHistory, setChatHistory] = useState([]);
    const [fileId, setFileId] = useState(null);

    const handleFileChange = (e) => {
        setPdfFile(e.target.files[0]);
    };

    const Upload = async () => {
        if(!pdfFile) {
            alert("Please upload a PDF file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", pdfFile);

        const res = await fetch("http://127.0.0.1:8000/upload", {
            method: "POST",
            body: formData,
        })

        if (res.ok) {
            const data = await res.json();
            setFileId(data.Id);
        } else {
            alert("An error occurred while uploading the file.");
        }
    };


    const handleAsk = async () => {
    if (!pdfFile || !question.trim()) {
        alert("Please upload a PDF file and enter a question.");
        return;
    }

    if(!fileId) {
        alert("Please upload the PDF file first.");
        return;
    }

    const formData = new FormData();

    formData.append("question", question);
    formData.append("file_id", fileId);

    try {
        const response = await fetch("http://127.0.0.1:8000/ask", {
            method: "POST",
            body: formData,
        });

        // Enhanced error handling
        if (!response.ok) {
            const errorData = await response.json();
            const errorMsg = errorData.detail || "An error occurred.";
            setAnswer(`Error: ${errorMsg}`);
            return;
        }

        const data = await response.json();
        const answerText = data.answer || "No relevant answer found.";

        const newChat = {
            question: question,
            answer: answerText,
        };

        setChatHistory([...chatHistory, newChat]);
        setAnswer(answerText);
        setQuestion(""); // Clear the input field

    } catch (error) {
        console.error("Fetch error:", error);
        setAnswer("An error occurred while fetching the answer.");
    }
};

    return (
        <div className="ask-question-container">
            {!fileId ? (
                <div>
                <input type="file" accept=".pdf" onChange={handleFileChange} />
                <button onClick={Upload}>
                    Upload
                </button>
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
                        onChange={(e) => setQuestion(e.target.value)}
                    />
                    <button onClick={handleAsk}>Ask</button>
                </div>
            </div>
            )}
        </div>
    );
}

export default AskQuestion;
