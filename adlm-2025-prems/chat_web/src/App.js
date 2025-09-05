import ChatForm from './ChatForm';
import ChatMessages from './ChatMessages';

import React from "react";

export default function App() {
  // placeholder sample data just to visualize the ui (remove later)
  const sampleMessages = [
    { id: 1, role: "assistant", text: "Hi! Ask me anything." },
    { id: 2, role: "user", text: "Give me a quick example." },
    { id: 3, role: "assistant", text: "Sure—this is just a UI skeleton." },
  ];

  return (
    <div className="container min-vh-100 d-flex flex-column py-3">
      <header className="mb-3">
        <h1 className="h4 mb-0">ADLM 2025</h1>
        <small className="text-muted">Desciption here.</small>
      </header>

      <div className="card shadow-sm flex-grow-1 d-flex">
        <div className="card-body p-0 d-flex flex-column" style={{ minHeight: 0 }}>
          <ChatMessages messages={sampleMessages} />
          <div className="border-top p-3">
            <ChatForm
              placeholder="Send a message…"
              onSubmit={(value) => {
                // set up later
                console.log("submit:", value);
              }}
            />
          </div>
        </div>
      </div>
      <footer className="text-center text-muted small mt-3">
        PREMS 2025 ADLM Submission
      </footer>
    </div>
  );
}

