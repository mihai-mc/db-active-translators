async function getLatestArtifactUrl() {
  try {
    const repo = "mihai-mc/db-active-translators";
    const artifactName = "generated-docx";

    const runRes = await fetch(
      `https://api.github.com/repos/${repo}/actions/runs?status=completed&per_page=1`
    );
    const runs = await runRes.json();

    if (!runs.workflow_runs || runs.workflow_runs.length === 0) {
      throw new Error("No completed runs found");
    }

    const runId = runs.workflow_runs[0].id;
    const artifactsRes = await fetch(
      `https://api.github.com/repos/${repo}/actions/runs/${runId}/artifacts`
    );
    const artifacts = await artifactsRes.json();

    const artifact = artifacts.artifacts.find(a => a.name === artifactName);
    if (!artifact) {
      throw new Error(`Artifact '${artifactName}' not found`);
    }

    return {
      url: artifact.archive_download_url,
      timestamp: runs.workflow_runs[0].completed_at
    };
  } catch (error) {
    console.error("Error fetching artifact:", error);
    throw error;
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  const btn = document.getElementById('download-btn');
  const statusText = document.getElementById('status-text');

  try {
    const { url, timestamp } = await getLatestArtifactUrl();
    btn.href = url;
    btn.textContent = "Download Translator List";
    btn.style.opacity = "1";
    btn.style.cursor = "pointer";

    const date = new Date(timestamp).toLocaleDateString();
    statusText.textContent = `Last updated: ${date}`;
  } catch (error) {
    btn.textContent = "Error loading";
    btn.style.cursor = "not-allowed";
    statusText.innerHTML = `<span class="error">Could not fetch latest artifact. Try again later.</span>`;
  }
});