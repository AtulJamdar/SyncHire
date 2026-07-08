"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [status, setStatus] = useState("Loading...");

  useEffect(() => {
    fetch("http://localhost:8000/health")
      .then((res) => res.json())
      .then((data) => setStatus(data.status || "Unknown"))
      .catch(() => setStatus("Offline"));
  }, []);

  return (
    <div style={{
      fontFamily: "system-ui, sans-serif",
      padding: "2rem",
      maxWidth: "600px",
      margin: "0 auto"
    }}>
      <h1>Job Finder AI</h1>
      <p>Frontend is running successfully.</p>
      <p>Backend API Status: <strong>{status}</strong></p>
    </div>
  );
}
