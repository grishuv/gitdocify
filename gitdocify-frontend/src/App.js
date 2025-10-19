import { useState, useEffect } from "react";
import axios from "axios";
import pLimit from "p-limit"; // npm install p-limit
import { jsPDF } from "jspdf";
import { Accordion, Spinner, Button, Card } from "react-bootstrap";
import { Light as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomOneDark } from "react-syntax-highlighter/dist/esm/styles/hljs";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [commits, setCommits] = useState([]);
  const [loading, setLoading] = useState(false);
  const [projectTitle, setProjectTitle] = useState("");
  const [projectDescription, setProjectDescription] = useState("");

  // ----------------------------
  // Generate Documentation
  // ----------------------------
  const handleSubmit = async () => {
    if (!repoUrl) return alert("Please enter a GitHub repository URL!");
    setLoading(true);

    try {
      // Extract repo name for title
      const repoName = repoUrl.split("/").slice(-1)[0].replace(".git", "");
      setProjectTitle(repoName);

      // Fetch repo description from GitHub API
      try {
        const apiRes = await axios.get(
          `https://api.github.com/repos/${repoUrl
            .split("github.com/")[1]
            .replace(".git", "")}`
        );
        setProjectDescription(apiRes.data.description || "No description available");
      } catch {
        setProjectDescription("No description available");
      }

      // Fetch commit list first
      const commitRes = await axios.post("http://127.0.0.1:8000/generate_docs", {
        repo_url: repoUrl,
        max_commits: 20,
      });

      const commitsData = commitRes.data.commits || [];

      // ----------------------------
      // Parallel API processing using semaphore
      // ----------------------------
      const limit = pLimit(5); // Max 5 concurrent
      const tasks = commitsData.map((c) =>
        limit(async () => {
          // Here we simulate additional API calls if needed
          // Currently, commits already have AI processed data, so this is optional
          return c;
        })
      );

      const finalCommits = await Promise.all(tasks);
      setCommits(finalCommits);
    } catch (error) {
      console.error(error);
      alert("Error fetching documentation. Please check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  // ----------------------------
  // WebSocket Live Updates
  // ----------------------------
    useEffect(() => {
    if (!repoUrl) return;

    const socket = new WebSocket("ws://127.0.0.1:8000/live_updates");
    

    socket.onopen = () => {
      console.log("✅ WebSocket connected");
      socket.send(JSON.stringify({ repo_url: repoUrl }));
    };

    socket.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      console.log("📡 Live update:", data);

      if (data.message === "New commit detected") {
        alert(`🔥 New commit by ${data.author}: ${data.message_text}`);

        try {
          const res = await axios.post("http://127.0.0.1:8000/generate_docs", {
            repo_url: repoUrl,
            max_commits: 1, // only latest commit
          });

          const newCommit = res.data.commits[0];
          if (newCommit) {
            setCommits(prev => [newCommit, ...prev]); // prepend new commit
          }
        } catch (err) {
          console.error("Error fetching new commit:", err);
        }
      }
    };

    socket.onclose = () => console.log("🔌 WebSocket disconnected");
    socket.onerror = (err) => console.error("WebSocket error:", err);

    return () => socket.close();
  }, [repoUrl]);

  // ----------------------------
  // PDF Download Function
  // ----------------------------
const downloadPDF = () => {
  if (!commits.length) return alert("No commits to generate PDF!");
  
  const pdf = new jsPDF({ orientation: "p", unit: "pt", format: "a4" });
  const margin = 20;
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  let y = margin;

  const lineHeight = 16;
  const sectionSpacing = 12;
  const indent = 10;

  const addText = (text, options = {}) => {
    const lines = pdf.splitTextToSize(text, pageWidth - 2 * margin - (options.indent || 0));
    lines.forEach((line) => {
      if (y + lineHeight > pageHeight - margin) {
        pdf.addPage();
        y = margin;
      }
      pdf.setFont("helvetica", options.bold ? "bold" : "normal");
      pdf.setTextColor(options.color || 0); // default black
      pdf.text(line, margin + (options.indent || 0), y);
      y += lineHeight;
    });
  };

  const addSeparator = () => {
    y += 6;
    pdf.setDrawColor(180);
    pdf.line(margin, y, pageWidth - margin, y);
    y += sectionSpacing;
  };

  // Project Header
  addText(`Project: ${projectTitle}`, { bold: true, color: "#1F4E79" });
  addText(`Description: ${projectDescription}`, { color: "#333333" });
  addText(`Total Commits: ${commits.length}`, { color: "#333333" });
  y += sectionSpacing;

  commits.forEach((c) => {
    addSeparator();
    addText(`Commit: ${c.sha}`, { bold: true, color: "#C00000" });
    addText(`Author: ${c.author} <${c.email}>`, { bold: true, color: "#4B4B4B" });
    addText(`Date: ${c.date}`, { bold: true, color: "#4B4B4B" });
    addText(`Message: ${c.message}`, { color: "#000000" });
    addText(`Summary: ${c.summary}`, { color: "#000000" });
    addText(`Code Notes:`, { bold: true, color: "#333333" });
    addText(c.code_notes || "// No notes", { indent });
    addText("Files Changed:", { bold: true, color: "#1F4E79" });

    c.files.forEach((f) => {
      addText(`File: ${f.file}`, { bold: true, color: "#00796B", indent });
      
      // Background shading for Before code
      if (f.before) {
        pdf.setFillColor(240, 240, 240); // light gray
        const beforeLines = pdf.splitTextToSize(f.before, pageWidth - 2 * margin - 2*indent);
        pdf.rect(margin + indent, y - lineHeight + 2, pageWidth - 2*margin - 2*indent, beforeLines.length * lineHeight, "F");
        addText("Before:\n" + f.before, { indent: indent * 2, color: "#B00020" });
      }

      // Background shading for After code
      if (f.after) {
        pdf.setFillColor(230, 255, 230); // light green
        const afterLines = pdf.splitTextToSize(f.after, pageWidth - 2 * margin - 2*indent);
        pdf.rect(margin + indent, y - lineHeight + 2, pageWidth - 2*margin - 2*indent, afterLines.length * lineHeight, "F");
        addText("After:\n" + f.after, { indent: indent * 2, color: "#006400" });
      }

      y += 6; // spacing between files
    });

    y += 10; // spacing between commits
  });

  pdf.save("gitdocify_documentation.pdf");
};



  // ----------------------------
  // UI
  // ----------------------------
  return (
    <div
      className="container py-5"
      style={{ backgroundColor: "#ffffffff", color: "#4c3e84ff", minHeight: "100vh" }}
    >
      <h1 className="text-center mb-4">🧠 GitDocify Viewer</h1>

      <div className="d-flex mb-4">
        <input
          type="text"
          className="form-control me-2"
          placeholder="Enter GitHub repo URL"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          style={{ backgroundColor: "#2e2e3fff", color: "#b3b6d1ff", border: "1px solid #333" }}
        />
        <button className="btn btn-success me-2" onClick={handleSubmit} disabled={loading}>
          {loading ? <Spinner animation="border" size="sm" /> : "Generate"}
        </button>
        {commits.length > 0 && (
          <button className="btn btn-primary" onClick={downloadPDF}>
            Download PDF
          </button>
        )}
      </div>

      {repoUrl && (
        <p className="text-center text-muted">
          🔄 Live updates enabled for: <b>{repoUrl}</b>
        </p>
      )}

      {commits.length > 0 && (
        <div style={{ padding: "16px", borderBottom: "1px solid #333", marginBottom: "16px" }}>
          <h2>{projectTitle}</h2>
          <p style={{ color: "#aca6b9ff" }}>{projectDescription}</p>
          <p>
            <b>Total Commits:</b> {commits.length}
          </p>
        </div>
      )}

      <Accordion alwaysOpen>
        {commits.map((c, idx) => (
          <Accordion.Item key={c.sha} eventKey={idx.toString()}>
            <Accordion.Header>
              <strong>{c.sha}</strong> — {c.summary}
            </Accordion.Header>
            <Accordion.Body>
              <p><b>Author:</b> {c.author}</p>
              <p><b>Date:</b> {c.date}</p>
              <p><b>Message:</b> {c.message}</p>
              <p><b>Code Notes:</b></p>
              <pre style={{ backgroundColor: "#1e1e1e", padding: "10px", borderRadius: "6px", color: "#fff" }}>
                {c.code_notes || "// No notes"}
              </pre>

              {c.files.map((f, fidx) => (
                <Card key={fidx} style={{ backgroundColor: "#1e1e1e", border: "1px solid #333", marginBottom: "16px" }}>
                  <Card.Header style={{ backgroundColor: "#1b1b1b", color: "#fff" }}>
                    <b>File:</b> {f.file}
                  </Card.Header>
                  <Card.Body className="row">
                    <div className="col-md-6">
                      <h6 style={{ color: "#ff6b6b" }}>Before</h6>
                      <SyntaxHighlighter
                        language="javascript"
                        style={atomOneDark}
                        customStyle={{ borderRadius: "6px", fontSize: "0.85rem", padding: "8px", backgroundColor: "#1e1e1e" }}
                      >
                        {f.before || "// No previous version"}
                      </SyntaxHighlighter>
                    </div>
                    <div className="col-md-6">
                      <h6 style={{ color: "#4ecdc4" }}>After</h6>
                      <SyntaxHighlighter
                        language="javascript"
                        style={atomOneDark}
                        customStyle={{ borderRadius: "6px", fontSize: "0.85rem", padding: "8px", backgroundColor: "#1e1e1e" }}
                      >
                        {f.after || "// No new code"}
                      </SyntaxHighlighter>
                    </div>
                  </Card.Body>
                </Card>
              ))}
            </Accordion.Body>
          </Accordion.Item>
        ))}
      </Accordion>
    </div>
  );
}

export default App;
