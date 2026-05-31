import { useState, useEffect } from "react";

function App() {
  const [status, setStatus] = useState(null);
  const [benchmarks, setBenchmarks] = useState(null);
  const [logs, setLogs] = useState([]);
  const [message, setMessage] = useState("");

  const loadData = async () => {
    try {
      const statusRes = await fetch("http://localhost:8080/status");
      const statusData = await statusRes.json();
      setStatus(statusData);

      const benchmarkRes = await fetch("http://localhost:8080/benchmarks");
      const benchmarkData = await benchmarkRes.json();
      setBenchmarks(benchmarkData);

      const logsRes = await fetch("http://localhost:8080/logs");
      const logsData = await logsRes.json();
      setLogs(logsData.logs || []);
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    }
  };

  useEffect(() => {
    loadData();

    const interval = setInterval(() => {
      loadData();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const callEndpoint = async (endpoint, actionName) => {
    try {
      const response = await fetch(
        `http://localhost:8080/${endpoint}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      setMessage(
        data.message || (actionName + " completed successfully")
      );

      loadData();
    } catch (error) {
      console.error(error);

      setMessage(
        actionName +
          " failed. Backend endpoint may not exist yet."
      );
    }
  };

  const cardStyle = {
    background: "#1a1a1a",
    padding: "20px",
    borderRadius: "8px",
    border: "1px solid #333",
  };

  const buttonStyle = {
    background: "#00ff88",
    color: "#000",
    border: "none",
    padding: "10px 15px",
    borderRadius: "5px",
    cursor: "pointer",
    fontWeight: "bold",
  };

  return (
    <div
      style={{
        background: "#0f0f0f",
        color: "#fff",
        minHeight: "100vh",
        padding: "20px",
        fontFamily: "monospace",
      }}
    >
      <h1
        style={{
          color: "#00ff88",
          textAlign: "center",
          marginBottom: "30px",
        }}
      >
        🤖 Autonomous AI Engineering System
      </h1>

      {message && (
        <div
          style={{
            background: "#222",
            border: "1px solid #00ff88",
            padding: "10px",
            marginBottom: "20px",
            borderRadius: "5px",
          }}
        >
          {message}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(250px,1fr))",
          gap: "20px",
          marginBottom: "20px",
        }}
      >
        <div style={cardStyle}>
          <h3 style={{ color: "#00ff88" }}>System Status</h3>
          <p>Status: {status?.status || "Loading..."}</p>
          <p>Version: {status?.version || "-"}</p>
          <p>Checkpoint: {status?.checkpoint || "student_v0"}</p>
        </div>

        <div style={cardStyle}>
          <h3 style={{ color: "#00ff88" }}>Benchmarks</h3>
          <p>Total Tasks: {benchmarks?.total_tasks ?? "-"}</p>
          <p>Passed: {benchmarks?.passed ?? "-"}</p>
          <p>Accuracy: {benchmarks?.accuracy ?? "-"}%</p>
        </div>

        <div style={cardStyle}>
          <h3 style={{ color: "#00ff88" }}>Student Model</h3>
          <p>Model: TinyLlama 1.1B</p>
          <p>Status: Active</p>
          <p>Teacher: Llama3 70B (Groq)</p>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(300px,1fr))",
          gap: "20px",
          marginBottom: "20px",
        }}
      >
        <div style={cardStyle}>
          <h3 style={{ color: "#00ff88" }}>Teacher Activity</h3>
          <p>
            Current Task:{" "}
            {status?.current_task || "Reviewing Student Output"}
          </p>
          <p>
            Dataset Entries: {status?.dataset_entries || 0}
          </p>
          <p>
            Memory Records: {status?.memory_records || 0}
          </p>
        </div>

        <div style={cardStyle}>
          <h3 style={{ color: "#00ff88" }}>Training Progress</h3>
          <p>
            Checkpoint: {status?.checkpoint || "student_v0"}
          </p>
          <p>Epoch: {status?.epoch || 0}</p>
          <p>Loss: {status?.loss || "-"}</p>
        </div>
      </div>

      <div style={cardStyle}>
        <h3 style={{ color: "#00ff88" }}>System Controls</h3>

        <div
          style={{
            display: "flex",
            gap: "10px",
            flexWrap: "wrap",
          }}
        >
          <button
            style={buttonStyle}
            onClick={() =>
              callEndpoint(
                "run_benchmark",
                "Benchmark"
              )
            }
          >
            Run Benchmark
          </button>

          <button
            style={buttonStyle}
            onClick={() =>
              callEndpoint(
                "generate_dataset",
                "Dataset Generation"
              )
            }
          >
            Generate Dataset
          </button>

          <button
            style={buttonStyle}
            onClick={() =>
              callEndpoint(
                "start_training",
                "Training"
              )
            }
          >
            Start Training
          </button>

          <button
            style={buttonStyle}
            onClick={() =>
              callEndpoint(
                "pause_system",
                "Pause System"
              )
            }
          >
            Pause System
          </button>
        </div>
      </div>

      <br />

      <div style={cardStyle}>
        <h3 style={{ color: "#00ff88" }}>Live Training Logs</h3>

        {logs.length === 0 ? (
          <p style={{ color: "#888" }}>
            No logs available.
          </p>
        ) : (
          logs.map((log, index) => (
            <div
              key={index}
              style={{
                borderBottom: "1px solid #333",
                padding: "10px 0",
              }}
            >
              <p style={{ color: "#888" }}>
                {log.timestamp || "No timestamp"}
              </p>

              <p>
                Prompt: {log.prompt}
              </p>

              <p style={{ color: "#00ff88" }}>
                Score: {log.evaluation_score}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;