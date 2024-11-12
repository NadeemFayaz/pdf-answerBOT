import React, { useState } from "react";
import "./AskQuestion.css";

function AskQuestion() {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [pdfFile, setPdfFile] = useState(null);
    const [chatHistory, setChatHistory] = useState([]);

    const handleFileChange = (e) => {
        setPdfFile(e.target.files[0]);
    };

    const handleAsk = async () => {
        if (!pdfFile || !question) {
            alert("Please upload a PDF file and enter a question.");
            return;
        }

        const formData = new FormData();
        formData.append("file", pdfFile);
        formData.append("question", question);

        try {
            const response = await fetch("http://127.0.0.1:8000/ask", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                setAnswer(`Error: ${errorData.error}`);
                return;
            }

            const data = await response.json();
            const newChat = {
                question: question,
                answer: data.answer || "No relevant answer found.",
            };

            setChatHistory([...chatHistory, newChat]);
            setAnswer(data.answer || "No relevant answer found.");
            setQuestion(""); // Clear question input

        } catch (error) {
            setAnswer("An error occurred while fetching the answer.");
        }
    };

    return (
        <div className="ask-question-container">
            <div className="upload-section">
                <input type="file" accept=".pdf" onChange={handleFileChange} />
            </div>
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
        </div>
    );
}

export default AskQuestion;
