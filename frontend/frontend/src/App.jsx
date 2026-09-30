import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);

  const [loading, setLoading] = useState(false);

  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState("");
  const [message, setMessage] = useState("");
 const [messages, setMessages] = useState([]);
// const [loading, setLoading] = useState(false);

  // ============================
  // Upload PDF
  // ============================

  async function uploadPDF() {
    if (!file) {
      setMessage("Please select a PDF.");
      return;
    }

    setUploading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Upload failed."
        );
      }

      setUploadedFile(data.filename);

      setMessage(
        `PDF ready — ${data.chunks} chunks created`
      );
    } catch (error) {
      console.error("Upload error:", error);

      setMessage(
        error.message || "Upload failed."
      );
    } finally {
      setUploading(false);
    }
  }

  // ============================
  // Ask Question
  // ============================

  async function askQuestion() {

  if (!question.trim() || loading) {
    return;
  }

  const userQuestion = question;

  setQuestion("");
  setLoading(true);

  try {

    const response = await fetch(
      "http://127.0.0.1:8000/ask",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          question: userQuestion
        })
      }
    );

    const data = await response.json();

    setMessages((previous) => [
      ...previous,
      {
        question: userQuestion,
        answer: data.answer,
        sources: data.sources,
        filename: data.filename
      }
    ]);

  } catch (error) {

    setMessages((previous) => [
      ...previous,
      {
        question: userQuestion,
        answer: "Something went wrong. Please try again.",
        sources: []
      }
    ]);

  } finally {

    setLoading(false);

  }
}

  // ============================
  // Enter key
  // ============================

  function handleKeyDown(e) {
    if (e.key === "Enter") {
      askQuestion();
    }
  }

  return (
    <div className="app">

      {/* ============================
          SIDEBAR
      ============================ */}

      <aside className="sidebar">

        <div className="logo">
          ✦ RAGIFY
        </div>

        <div className="upload-section">

          <h3>Your Documents</h3>

          <label className="upload-box">

            <span>＋</span>

            <strong>
              {file
                ? file.name
                : "Upload PDF"}
            </strong>

            <small>
              PDF files up to your project limit
            </small>

            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={(e) => {
                const selectedFile =
                  e.target.files?.[0];

                setFile(selectedFile || null);
                setMessage("");
              }}
            />

          </label>

          {/* Uploaded file */}

          {uploadedFile && (
            <div className="file-card">
              📄 {uploadedFile}
            </div>
          )}

          {/* Process button */}

          <button
            className="upload-button"
            onClick={uploadPDF}
            disabled={uploading || !file}
          >
            {uploading
              ? "Processing..."
              : "Process PDF"}
          </button>

          {/* Status */}

          {message && (
            <p className="status">
              {message}
            </p>
          )}

        </div>

      </aside>


      {/* ============================
          MAIN CONTENT
      ============================ */}

      <main className="main">

        <div className="header">

          <span className="badge">
            ● AI DOCUMENT ASSISTANT
          </span>

          <h1>
            Ask your documents.
          </h1>

          <p>
            Upload a PDF and get answers
            grounded in your content.
          </p>

        </div>


        {/* ============================
            CHAT / ANSWER
        ============================ */}

   <div className="chat-area">

  {messages.length === 0 && (
    <div className="empty-state">

      <div className="empty-icon">
        ✦
      </div>

      <h2>
        Ask anything about your PDF
      </h2>

      <p>
        Your answers are generated using
        information retrieved from your document.
      </p>

    </div>
  )}


  {messages.map((message, index) => (

    <div className="message-group" key={index}>

      {/* User */}

      <div className="user-message">

        <div className="avatar">
          You
        </div>

        <div>
          <p>{message.question}</p>
        </div>

      </div>


      {/* AI */}

      <div className="ai-message">

        <div className="avatar ai-avatar">
          ✦
        </div>

        <div className="answer-content">

          <span className="ai-label">
            RAGIFY AI
          </span>

          <p>
            {message.answer}
          </p>

        </div>

      </div>


      {/* Sources */}

      {message.sources.length > 0 && (

        <div className="sources">

          <h4>
            Sources used
          </h4>

          <div className="source-grid">

            {message.sources.map(
              (source, sourceIndex) => (

                <div
                  className="source-card"
                  key={sourceIndex}
                >

                  <div className="source-number">
                    {sourceIndex + 1}
                  </div>

                  <div>
                    <strong>
                      Retrieved context
                    </strong>

                    <p>
                      {source.slice(0, 150)}
                      {source.length > 150 ? "..." : ""}
                    </p>
                  </div>

                </div>

              )
            )}

          </div>

        </div>

      )}

    </div>

  ))}


  {/* Loading */}

  {loading && (

    <div className="ai-message">

      <div className="avatar ai-avatar">
        ✦
      </div>

      <div className="typing">

        <span></span>
        <span></span>
        <span></span>

      </div>

    </div>

  )}

</div>


        {/* ============================
            QUESTION INPUT
        ============================ */}

        <div className="question-box">

          <input
            type="text"
            value={question}
            onChange={(e) =>
              setQuestion(e.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about your document..."
            disabled={loading}
          />

          <button
            onClick={askQuestion}
            disabled={
              loading || !question.trim()
            }
          >
            {loading ? "..." : "➤"}
          </button>

        </div>

      </main>

    </div>
  );
}

export default App;
