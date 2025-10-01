import React, { useState } from "react";
import axios from "axios";

function App() {
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [snippet, setSnippet] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setSelectedFile(file);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setSnippet(res.data.snippet || "");
      if (file.type.startsWith("image/")) {
        setPreviewUrl(URL.createObjectURL(file));
      } else {
        setPreviewUrl(null);
      }
    } catch (err) {
      console.error(err);
      alert("File upload failed");
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return alert("Enter a question first");
    setLoading(true);

    const formData = new FormData();
    formData.append("question", question);

    try {
      const res = await axios.post("http://localhost:8000/ask", formData);
      const answer = res.data.answer;
      setChatHistory([...chatHistory, { question, answer }]);
      setQuestion("");
    } catch (err) {
      console.error(err);
      alert("Error asking question");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setChatHistory([]);
    setSelectedFile(null);
    setPreviewUrl(null);
    setSnippet("");
    setQuestion("");
  };

  return (
    <div style={{ maxWidth: 800, margin: "20px auto", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ color: "#2b6cb0", marginBottom: 20 }}>Multi-Modal Assistant</h1>

      <input type="file" accept=".txt,.pdf,.png,.jpg,.jpeg" onChange={handleFileChange} />

      {previewUrl && (
        <div style={{ marginTop: 10 }}>
          <img
            src={previewUrl}
            alt="Preview"
            style={{
              maxHeight: 300,
              borderRadius: 8,
              border: "1px solid #ccc",
              objectFit: "contain",
              boxShadow: "0 2px 6px rgba(0,0,0,0.2)",
            }}
          />
        </div>
      )}

      {snippet && (
        <div style={{ marginTop: 15, padding: 10, backgroundColor: "#f0f4f8", borderRadius: 6 }}>
          <strong>File Snippet:</strong>
          <p style={{ whiteSpace: "pre-wrap" }}>{snippet}</p>
        </div>
      )}

      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question..."
        style={{
          width: "100%",
          padding: 8,
          borderRadius: 4,
          border: "1px solid #ccc",
          minHeight: 60,
          marginTop: 10,
        }}
      />

      <div style={{ marginTop: 10 }}>
        <button
          onClick={handleAsk}
          style={{
            backgroundColor: "#4299e1",
            color: "white",
            border: "none",
            padding: "6px 12px",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          Ask
        </button>
        <button
          onClick={handleClear}
          style={{
            marginLeft: 10,
            backgroundColor: "#f56565",
            color: "white",
            border: "none",
            padding: "6px 12px",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          Clear
        </button>
      </div>

      {loading && <p style={{ color: "#3182ce" }}>Processing, please wait...</p>}

      {chatHistory.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <h3>Chat History:</h3>
          {chatHistory.map((item, idx) => (
            <div
              key={idx}
              style={{
                marginBottom: 12,
                backgroundColor: "#fefcbf",
                padding: 10,
                borderRadius: 6,
                border: "1px solid #f6e05e",
                whiteSpace: "pre-wrap",
              }}
            >
              <p><strong>Q:</strong> {item.question}</p>
              <p><strong>A:</strong> {item.answer}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
