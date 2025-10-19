import React from "react";
import { Light as SyntaxHighlighter } from "react-syntax-highlighter";
import { github } from "react-syntax-highlighter/dist/esm/styles/hljs";
import { Collapse } from "react-collapse";

function CommitViewer({ commits }) {
  const [openCommit, setOpenCommit] = React.useState(null);
  const [openFile, setOpenFile] = React.useState(null);

  return (
    <div className="commit-list">
      {commits.map((commit, i) => (
        <div key={i} className="commit-card">
          <div
            className="commit-header"
            onClick={() => setOpenCommit(openCommit === i ? null : i)}
          >
            <h3>{commit.sha} — {commit.summary}</h3>
            <p><strong>{commit.author}</strong> • {new Date(commit.date).toLocaleString()}</p>
          </div>

          <Collapse isOpened={openCommit === i}>
            <div className="commit-details">
              <p><strong>Message:</strong> {commit.message}</p>
              <p><strong>Notes:</strong></p>
              <pre className="notes">{commit.code_notes}</pre>

              <div className="file-section">
                {commit.files.map((file, j) => (
                  <div key={j} className="file-card">
                    <div
                      className="file-header"
                      onClick={() => setOpenFile(openFile === `${i}-${j}` ? null : `${i}-${j}`)}
                    >
                      <h4>{file.file}</h4>
                    </div>

                    <Collapse isOpened={openFile === `${i}-${j}`}> 
                      <div className="code-diff">
                        <div>
                          <h5>Before</h5>
                          <SyntaxHighlighter language="javascript" style={github}>
                            {file.before || "// No previous code"}
                          </SyntaxHighlighter>
                        </div>

                        <div>
                          <h5>After</h5>
                          <SyntaxHighlighter language="javascript" style={github}>
                            {file.after || "// No new code"}
                          </SyntaxHighlighter>
                        </div>
                      </div>
                    </Collapse>
                  </div>
                ))}
              </div>
            </div>
          </Collapse>
        </div>
      ))}
    </div>
  );
}

export default CommitViewer;
