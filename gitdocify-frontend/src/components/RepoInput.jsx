import React, { useState } from "react";

function RepoInput({ onSubmit }) {
  const [repoUrl, setRepoUrl] = useState("");
  const [maxCommits, setMaxCommits] = useState(10);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!repoUrl) return alert("Enter a repository URL!");
    onSubmit(repoUrl, parseInt(maxCommits));
  };

  return (
    <form className="repo-form" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Enter GitHub repo URL..."
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
      />
      <input
        type="number"
        value={maxCommits}
        onChange={(e) => setMaxCommits(e.target.value)}
        min="1"
        max="50"
      />
      <button type="submit">Generate Documentation</button>
    </form>
  );
}

export default RepoInput;
