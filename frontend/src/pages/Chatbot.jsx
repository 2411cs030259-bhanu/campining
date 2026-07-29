import React, { useState, useRef, useEffect } from "react";
import AppLayout from "../components/AppLayout";
import * as api from "../api/api";

const SUGGESTED_QUESTIONS = [
  "What is CTR?",
  "What is ROAS?",
  "What is CPC?",
  "How can I improve campaigns?",
  "How do I generate reports?",
];

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! Ask me about CTR, ROAS, CPC, CPA, or how to improve campaigns." },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text) => {
    const question = text.trim();
    if (!question || sending) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setSending(true);

    try {
      const res = await api.askChatbot(question);
      setMessages((prev) => [...prev, { role: "bot", text: res.data.answer }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: err.message || "Sorry, something went wrong." },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <AppLayout>
      <div className="page-header">
        <h1>Marketing Chatbot</h1>
        <p className="page-subtitle">Ask quick questions about marketing metrics and this platform.</p>
      </div>

      <div className="chatbot-suggestions">
        {SUGGESTED_QUESTIONS.map((q) => (
          <button key={q} className="chip" onClick={() => sendMessage(q)}>
            {q}
          </button>
        ))}
      </div>

      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble chat-bubble-${m.role}`}>
            {m.text}
          </div>
        ))}
        <div ref={scrollRef} />
      </div>

      <form
        className="chat-input-row"
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage(input);
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
        />
        <button className="btn btn-primary" type="submit" disabled={sending}>
          Send
        </button>
      </form>
    </AppLayout>
  );
}
