const params = new URLSearchParams(window.location.search);
const DOC_ID = params.get("doc_id") || "";
const DOC_TITLE = params.get("title") || "Course";
const START_NODE_ID = params.get("node_id") || "";
const USER_ID = localStorage.getItem("iveri_uid") || "default_user";
const STATE_KEY = `course_state_${DOC_ID}`;

const COURSE = {
  structure: [],
  nodeContent: {},
  nodeById: new Map(),
  parentById: new Map(),
  selectedNodeId: "",
  expanded: new Set(),
};

function el(id) { return document.getElementById(id); }
function esc(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function loadSavedState() {
  try {
    const raw = localStorage.getItem(STATE_KEY);
    if (!raw) return;
    const s = JSON.parse(raw);
    COURSE.selectedNodeId = s.selectedNodeId || "";
    COURSE.expanded = new Set(s.expanded || []);
  } catch (_) {}
}

function saveState() {
  localStorage.setItem(STATE_KEY, JSON.stringify({
    selectedNodeId: COURSE.selectedNodeId,
    expanded: Array.from(COURSE.expanded),
  }));
}

function renderMd(text) {
  if (typeof text !== "string") return esc(String(text || ""));
  let safe = esc(text);

  safe = safe
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/^## (.+)$/gm, "<h2>$1</h2>")
    .replace(/^# (.+)$/gm, "<h1>$1</h1>");

  // Render bullet lists
  const lines = safe.split("\n");
  let html = "";
  let inUl = false;
  for (const raw of lines) {
    const line = raw.trimEnd();
    if (/^\s*[-*]\s+/.test(line)) {
      if (!inUl) {
        html += "<ul>";
        inUl = true;
      }
      html += `<li>${line.replace(/^\s*[-*]\s+/, "")}</li>`;
    } else {
      if (inUl) {
        html += "</ul>";
        inUl = false;
      }
      if (!line.trim()) {
        html += "<br>";
      } else if (/^<h[1-3]>/.test(line)) {
        html += line;
      } else {
        html += `<p>${line}</p>`;
      }
    }
  }
  if (inUl) html += "</ul>";
  return html;
}

function findNode(nodeId) {
  return COURSE.nodeById.get(nodeId) || null;
}

function firstUsableNode() {
  for (const id of COURSE.nodeById.keys()) {
    if ((COURSE.nodeContent[id] || "").trim().length > 0) {
      return COURSE.nodeById.get(id) || null;
    }
  }
  return null;
}

function hydrateNodeIndex(nodes) {
  COURSE.nodeById.clear();
  COURSE.parentById.clear();
  const stack = [...(nodes || [])];
  while (stack.length) {
    const node = stack.pop();
    COURSE.nodeById.set(node.id, node);
    for (const child of (node.children || [])) {
      COURSE.parentById.set(child.id, node.id);
      stack.push(child);
    }
  }
}

function expandAllParents(nodeId) {
  let cur = nodeId;
  while (cur) {
    const parent = COURSE.parentById.get(cur);
    if (!parent) break;
    COURSE.expanded.add(parent);
    cur = parent;
  }
}

function firstContentDescendant(startId) {
  const start = findNode(startId);
  if (!start) return null;
  const stack = [...(start.children || [])];
  while (stack.length) {
    const n = stack.shift();
    if (((COURSE.nodeContent[n.id] || "").trim().length > 0)) return n;
    if (n.children && n.children.length) stack.push(...n.children);
  }
  return null;
}

function expandAllFolders(nodes) {
  const stack = [...(nodes || [])];
  while (stack.length) {
    const n = stack.pop();
    if (n.children && n.children.length) COURSE.expanded.add(n.id);
    for (const ch of (n.children || [])) stack.push(ch);
  }
}

function renderTree() {
  const container = el("courseTree");
  const rows = [];

  function walk(nodes, depth) {
    (nodes || []).forEach(node => {
      const hasChildren = (node.children || []).length > 0;
      const expanded = COURSE.expanded.has(node.id);
      const selected = COURSE.selectedNodeId === node.id ? "selected" : "";
      const indentClass = `tree-indent-${Math.min(depth, 3)}`;
      rows.push(`
        <div class="tree-row ${indentClass} ${selected}" data-id="${node.id}" data-has-children="${hasChildren ? "1" : "0"}" data-toggle="${hasChildren ? "1" : "0"}">
          <span class="tree-toggle">${hasChildren ? (expanded ? "▾" : "▸") : "·"}</span>
          <span>${esc(node.heading)}</span>
        </div>
      `);
      if (hasChildren && expanded) walk(node.children, depth + 1);
    });
  }

  walk(COURSE.structure, 1);
  container.innerHTML = rows.join("") || "<p>No headings detected.</p>";
}

function selectNode(nodeId) {
  const node = findNode(nodeId);
  if (!node) return;

  // If user clicked a folder node (no content), jump to first subtopic with content.
  const content = (COURSE.nodeContent[nodeId] || "").trim();
  if (!content && node.children && node.children.length) {
    const childWithContent = firstContentDescendant(nodeId);
    if (childWithContent) {
      expandAllParents(childWithContent.id);
      COURSE.selectedNodeId = childWithContent.id;
      saveState();
      renderTree();
      return selectNode(childWithContent.id);
    }
  }

  COURSE.selectedNodeId = nodeId;
  saveState();
  updateTreeSelection();

  el("sectionTitle").textContent = node.heading || "Section";
  el("sectionContent").innerHTML = renderMd(content || "No section content available.");
}

function updateTreeSelection() {
  const active = document.querySelector(".tree-row.selected");
  if (active) active.classList.remove("selected");
  const next = document.querySelector(`.tree-row[data-id="${COURSE.selectedNodeId}"]`);
  if (next) next.classList.add("selected");
}

async function runAction(action) {
  if (!COURSE.selectedNodeId) return;
  const output = el("aiOutput");
  output.style.display = "block";
  output.innerHTML = "Generating...";
  try {
    const res = await fetch("/api/course/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ doc_id: DOC_ID, node_id: COURSE.selectedNodeId, action }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Action failed");
    output.innerHTML = `<h3>${action === "summarize" ? "Summary" : "Detailed Explanation"}</h3>${renderMd(data.answer || "")}`;
  } catch (e) {
    output.innerHTML = `<p style="color:#b91c1c">${esc(e.message)}</p>`;
  }
}

function appendMentor(role, text) {
  const box = el("mentorMsgs");
  const d = document.createElement("div");
  d.className = `mentor-msg ${role}`;
  d.innerHTML = renderMd(text);
  box.appendChild(d);
  box.scrollTop = box.scrollHeight;
}

async function sendMentor() {
  const inp = el("mentorInput");
  const q = (inp.value || "").trim();
  if (!q) return;
  inp.value = "";
  appendMentor("user", q);
  appendMentor("ai", "Thinking...");
  const pending = el("mentorMsgs").lastElementChild;
  try {
    const res = await fetch("/api/course/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        doc_id: DOC_ID,
        question: q,
        node_id: COURSE.selectedNodeId || "",
        user_id: USER_ID,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Chat failed");
    pending.innerHTML = renderMd(data.answer || "");
  } catch (e) {
    pending.innerHTML = `<span style="color:#b91c1c">${esc(e.message)}</span>`;
  }
}

async function init() {
  if (!DOC_ID) {
    el("courseTitle").textContent = "Invalid course link (missing doc_id).";
    return;
  }

  el("courseTitle").textContent = DOC_TITLE || DOC_ID;
  loadSavedState();

  const res = await fetch(`/api/course/${encodeURIComponent(DOC_ID)}/structure`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to load course structure");
  COURSE.nodeContent = data.node_content || {};
  COURSE.structure = data.structure || [];
  hydrateNodeIndex(COURSE.structure);

  if (!COURSE.expanded.size) {
    // Show full hierarchy expanded by default (like earlier behavior).
    expandAllFolders(COURSE.structure);
  }

  let selected = findNode(START_NODE_ID) || findNode(COURSE.selectedNodeId) || firstUsableNode() || (COURSE.structure[0] || null);
  if (selected) {
    // If the selected node has no content, choose nearest descendant with content.
    const hasContent = ((COURSE.nodeContent[selected.id] || "").trim().length > 0);
    if (!hasContent) {
      const desc = firstContentDescendant(selected.id) || firstUsableNode();
      if (desc) selected = desc;
    }
    COURSE.selectedNodeId = selected.id;
    expandAllParents(selected.id);
  }
  renderTree();
  if (COURSE.selectedNodeId) selectNode(COURSE.selectedNodeId);

  el("courseTree").addEventListener("click", (e) => {
    const row = e.target.closest(".tree-row");
    if (!row) return;
    const id = row.dataset.id;
    const hasChildren = row.dataset.hasChildren === "1";
    const onToggle = e.target.closest(".tree-toggle");
    if (hasChildren && onToggle) {
      if (COURSE.expanded.has(id)) COURSE.expanded.delete(id);
      else COURSE.expanded.add(id);
      saveState();
      renderTree();
      return;
    }
    if (hasChildren && !COURSE.expanded.has(id)) COURSE.expanded.add(id);
    selectNode(id);
  });

  el("btnSummarize").addEventListener("click", () => runAction("summarize"));
  el("btnExplain").addEventListener("click", () => runAction("explain"));

  el("mentorFab").addEventListener("click", () => {
    const panel = el("mentorPanel");
    panel.style.display = panel.style.display === "none" ? "flex" : "none";
  });
  el("mentorClose").addEventListener("click", () => { el("mentorPanel").style.display = "none"; });
  el("mentorSend").addEventListener("click", sendMentor);
  el("mentorInput").addEventListener("keydown", (e) => { if (e.key === "Enter") sendMentor(); });
}

init().catch((e) => {
  el("sectionContent").innerHTML = `<p style="color:#b91c1c">${esc(e.message)}</p>`;
});
