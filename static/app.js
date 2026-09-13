const $ = (id) => document.getElementById(id);
function el(tag, text, cls) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (cls) node.className = cls;
  return node;
}
$("demo").onclick = () => {
  $("resume").value = "Synthetic candidate\nBuilt an n8n workflow with Google Sheets and webhooks.\nUsed Python and SQL to clean sample records.\nStudied probability and linear algebra.";
  $("job").value = "Synthetic vacancy\nBuild n8n workflows and connect Google Sheets using webhooks.\nUse Python and SQL for data processing.\nDocument changes in Git and write unit tests.\nDocker is a plus.";
  $("results").replaceChildren();
  $("status").textContent = "Synthetic example loaded. Select Compare skills.";
};
$("form").onsubmit = async (event) => {
  event.preventDefault();
  $("submit").disabled = true;
  $("results").replaceChildren();
  $("status").className = "";
  $("status").textContent = "Comparing skill mentions…";
  try {
    const response = await fetch("/api/analyze", {method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({resume:$("resume").value,job:$("job").value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Comparison failed.");
    const summary = el("div", undefined, "card");
    summary.append(el("span", "Mention coverage", "badge"),
      el("div", data.coverage_percent === null ? "Not available" : data.coverage_percent + "%", "score"),
      el("p", data.matched.length + " of " + data.recognized_job_skills + " recognized job skills appear in the resume."));
    $("results").append(summary);
    const columns = el("div", undefined, "grid");
    for (const [title, items, matched] of [
      ["Matching evidence", data.matched, true],
      ["Not found in your resume", data.not_found_in_resume, false]]) {
      const card = el("div", undefined, "card");
      card.append(el("h2", title));
      if (!items.length) card.append(el("p", "No items in this category."));
      for (const item of items) {
        const row = el("div", undefined, "evidence");
        row.append(el("strong", item.skill));
        if (matched) row.append(el("p", "Resume: " + item.resume_evidence));
        row.append(el("p", "Job: " + item.job_evidence, "muted"));
        card.append(row);
      }
      columns.append(card);
    }
    $("results").append(columns);
    if (data.other_resume_skills.length) {
      const other = el("div", undefined, "card");
      other.append(el("h2", "Other skills mentioned in your resume"));
      data.other_resume_skills.forEach(s => other.append(el("span", s, "tag")));
      $("results").append(other);
    }
    $("status").textContent = "Comparison complete. Review the evidence in context.";
  } catch (error) {
    $("status").className = "error";
    $("status").textContent = error.message;
  } finally { $("submit").disabled = false; }
};
