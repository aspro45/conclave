import { makeReader, write, connectWallet, activeAccount, short, fmtErr }
  from "./shared/genlayer-lite.js";

const CONTRACT = "0x44ccfCdeb1e9667C8548E051eDcf6D734c3fBA59";
const EXPLORER = "https://explorer-studio.genlayer.com/contracts/0x44ccfCdeb1e9667C8548E051eDcf6D734c3fBA59";
const { read } = makeReader(CONTRACT);
const $ = (id) => document.getElementById(id);
const esc = (s) => (s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

let account = null;
let debates = [];
let selected = null;
let positions = [];

function withTimeout(promise, ms, fallback) {
  return Promise.race([
    promise.catch(() => fallback),
    new Promise((resolve) => setTimeout(() => resolve(fallback), ms)),
  ]);
}

$("contractLink").href = "https://explorer-studio.genlayer.com/contracts/0x44ccfCdeb1e9667C8548E051eDcf6D734c3fBA59";
$("contractLink").textContent = "Contract " + short(CONTRACT);
$("contractLink").target = "_blank";
$("contractLink").rel = "noopener";

function toast(msg, kind = "") {
  const el = document.createElement("div");
  el.className = "toast " + kind;
  el.textContent = msg;
  $("log").appendChild(el);
  setTimeout(() => el.remove(), kind === "err" ? 14000 : 5200);
}

async function ensureWallet() {
  if (account) return account;
  await connectWallet();
  account = activeAccount();
  $("walletSlot").innerHTML = `<span class="pill">${short(account)}</span>`;
  return account;
}

function parseList(raw) {
  try {
    const x = JSON.parse(String(raw));
    return Array.isArray(x) ? x : [];
  } catch {
    return [];
  }
}

async function load() {
  const statsRaw = await read("get_contract_stats");
  const stats = JSON.parse(String(statsRaw || "{}"));
  $("stats").innerHTML = [
    ["Debates", stats.debates || 0],
    ["Judgements", stats.judgements || 0],
    ["Appeals", stats.appeals || 0],
    ["Archived", stats.archived || 0],
    ["Evidence", stats.evidence || 0],
    ["Audit", stats.audits || 0],
  ].map(([k, v]) => `<div class="stat"><b>${v}</b><span>${k}</span></div>`).join("");

  debates = parseList(await read("get_recent_debates", [40]));
  if (selected === null && debates.length) selected = debates[0].id;
  renderList();
  await renderDetail();
}

function renderList() {
  const list = $("debateList");
  if (!debates.length) {
    list.innerHTML = `<div class="notes">No debates yet. Open the first motion.</div>`;
    return;
  }
  list.innerHTML = debates.map((d) => `
    <button class="debate-card ${String(d.id) === String(selected) ? "on" : ""}" data-id="${esc(d.id)}">
      <h3>${esc(d.motion)}</h3>
      <div class="meta">
        <span class="pill">${esc(d.status)}</span>
        <span class="pill">winner ${d.outcome === "met" ? "FOR" : d.outcome === "not_met" ? "AGAINST" : "pending"}</span>
        <span class="pill">${d.confidenceBps || 0} bps</span>
      </div>
    </button>
  `).join("");
  list.querySelectorAll(".debate-card").forEach((btn) => btn.onclick = async () => {
    selected = btn.dataset.id;
    renderList();
    await renderDetail();
  });
}

async function renderDetail() {
  if (selected === null) {
    $("detail").innerHTML = `<div class="empty">Select a debate.</div>`;
    return;
  }
  const fallback = debates.find((d) => String(d.id) === String(selected));
  const raw = await withTimeout(read("get_debate_record", [String(selected)]), 2600, "");
  if (!raw && !fallback) {
    $("detail").innerHTML = `<div class="empty">Debate not found.</div>`;
    return;
  }
  const d = raw ? JSON.parse(String(raw)) : fallback;
  positions = parseList(await withTimeout(read("get_positions", [String(selected)]), 2600, "[]"));
  const forArgs = positions.filter((p) => Number(p.side || 1) === 1);
  const againstArgs = positions.filter((p) => Number(p.side || 1) === 2);
  const lane = (title, rows) => `<section class="lane"><h3>${title}</h3>${rows.length ? rows.map((p) => `
    <div class="arg">${esc(p.detail)}<small>${esc(p.proofUrl || "no evidence URL")} - ${short(p.author || "")}</small></div>
  `).join("") : `<div class="arg">No arguments yet.</div>`}</section>`;
  $("detail").innerHTML = `
    <div class="detail-head">
      <span class="eyebrow">${esc(d.status)} / ${d.outcome === "met" ? "FOR" : d.outcome === "not_met" ? "AGAINST" : "pending"}</span>
      <h2>${esc(d.motion)}</h2>
      <div class="rationale">${esc(d.rationale || d.summary || d.resolutionRule || "Awaiting judgement.")}</div>
      <div class="meta"><span class="pill">${d.confidenceBps || 0} confidence bps</span><span class="pill">${esc(d.primary_url || "no primary URL")}</span></div>
    </div>
    <div class="columns">${lane("FOR", forArgs)}${lane("AGAINST", againstArgs)}</div>
  `;
  $("notes").innerHTML = `Selected debate <b>${esc(String(selected))}</b><br>Use Judge after both sides have an argument. Challenge and Appeal require the normal lifecycle.`;
}

$("connectBtn").onclick = ensureWallet;
$("refreshBtn").onclick = () => load().catch((e) => toast(fmtErr(e), "err"));

$("motionForm").onsubmit = async (e) => {
  e.preventDefault();
  const motion = $("motionInput").value.trim();
  if (!motion) return;
  try {
    await ensureWallet();
    await write(CONTRACT, "open_debate", [motion]);
    $("motionInput").value = "";
    toast("Debate opened.", "ok");
    await load();
  } catch (err) { toast(fmtErr(err), "err"); }
};

$("argueForm").onsubmit = async (e) => {
  e.preventDefault();
  if (selected === null) return toast("Select a debate first.", "err");
  try {
    await ensureWallet();
    await write(CONTRACT, "argue", [Number(selected), Number($("sideInput").value), $("argumentInput").value.trim(), $("evidenceInput").value.trim()]);
    $("argumentInput").value = "";
    $("evidenceInput").value = "";
    toast("Argument submitted.", "ok");
    await load();
  } catch (err) { toast(fmtErr(err), "err"); }
};

$("judgeBtn").onclick = async () => {
  if (selected === null) return;
  try { await ensureWallet(); await write(CONTRACT, "conclude", [Number(selected)]); toast("Judgement requested.", "ok"); await load(); }
  catch (err) { toast(fmtErr(err), "err"); }
};

$("challengeBtn").onclick = async () => {
  if (selected === null) return;
  try {
    await ensureWallet();
    await write(CONTRACT, "open_challenge_window", [String(selected)]);
    await write(CONTRACT, "submit_challenge", [String(selected), "This debate needs a stricter source-quality review.", "https://en.wikipedia.org/wiki/Prompt_injection"]);
    toast("Challenge submitted.", "ok");
    await load();
  } catch (err) { toast(fmtErr(err), "err"); }
};

$("appealBtn").onclick = async () => {
  if (selected === null) return;
  try {
    await ensureWallet();
    await write(CONTRACT, "submit_appeal", [String(selected), "Appeal asks validators to preserve the best-supported reasoning path.", "https://docs.genlayer.com/"]);
    toast("Appeal submitted.", "ok");
    await load();
  } catch (err) { toast(fmtErr(err), "err"); }
};

load().catch((e) => toast(fmtErr(e), "err"));
