import { useState, useRef, useEffect } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I am Pybot, your Travel Assistant. Ask me about the weather anywhere, or what to pack!",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const sendMessage = async (e: any) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg }),
      });

      if (!response.ok) throw new Error("API Error");
      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, the server encountered an error.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        padding: "20px",
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          textAlign: "center",
          marginBottom: "20px",
          paddingBottom: "20px",
          borderBottom: "1px solid #333",
        }}
      >
        <h2 style={{ margin: 0, color: "#fff", fontSize: "24px" }}>
          ✈️ Pybot Travel Assistant ✈️
        </h2>
      </div>

      <div
        style={{
          flex: 1,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: "16px",
          paddingRight: "10px",
        }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <div
              style={{
                maxWidth: "75%",
                padding: "14px 18px",
                borderRadius: "12px",
                backgroundColor: msg.role === "user" ? "#2b2b2b" : "#1e1e1e",
                color: msg.role === "user" ? "#e0e0e0" : "#c5c5c5",
                border:
                  msg.role === "user" ? "1px solid #444" : "1px solid #2a2a2a",
                boxShadow: "0 4px 6px rgba(0,0,0,0.3)",
                lineHeight: "1.5",
                fontSize: "15px",
                whiteSpace: "pre-wrap",
              }}
            >
              <div
                style={{
                  fontSize: "11px",
                  fontWeight: "bold",
                  color: msg.role === "user" ? "#4a9eff" : "#00c896",
                  marginBottom: "6px",
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                }}
              >
                {msg.role === "user" ? "You" : "AI Assistant"}
              </div>

              {msg.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ display: "flex", justifyContent: "flex-start" }}>
            <div
              style={{
                backgroundColor: "#1e1e1e",
                border: "1px solid #2a2a2a",
                padding: "12px 18px",
                borderRadius: "12px",
                color: "#888",
                fontSize: "14px",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <span className="dot-pulse">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ marginTop: "20px" }}>
        <form
          onSubmit={sendMessage}
          style={{
            display: "flex",
            backgroundColor: "#1e1e1e",
            borderRadius: "24px",
            padding: "6px 10px",
            border: "1px solid #333",
            boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
          }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message here..."
            style={{
              flex: 1,
              padding: "12px",
              background: "transparent",
              border: "none",
              color: "#fff",
              fontSize: "15px",
              outline: "none",
            }}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            style={{
              padding: "0 20px",
              background: isLoading ? "#444" : "#4a9eff",
              color: "#fff",
              border: "none",
              borderRadius: "18px",
              cursor: isLoading ? "default" : "pointer",
              fontWeight: "bold",
              transition: "background 0.2s",
            }}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
