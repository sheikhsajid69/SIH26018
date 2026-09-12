"use client";

import { ChangeEvent, useRef, useState } from "react";

type Document = { name: string; meta: string; tag: string; state: "Verified" | "Uploaded"; };
type ValidationRow = { field: string; value_a: string; value_b: string; confidence: number; result: string; };

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const fallbackValidation: ValidationRow[] = [
  { field: "owner", value_a: "Ramesh Kumar", value_b: "Ramesh Kumar (synthetic demo person)", confidence: .97, result: "MATCH" },
  { field: "survey_number", value_a: "124/2", value_b: "124/2", confidence: .99, result: "MATCH" },
  { field: "area", value_a: "2.31 acre", value_b: "2.40 acre", confidence: .88, result: "REVIEW_REQUIRED" },
  { field: "village", value_a: "Sampurna", value_b: "Sampurna", confidence: .95, result: "MATCH" }
];

const Icon = ({ name, size = 18 }: { name: string; size?: number }) => {
  const paths: Record<string, React.ReactNode> = {
    home: <><path d="M3 10.6 12 3l9 7.6v9.9a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 20.5z"/><path d="M9 22v-6h6v6"/></>,
    parcel: <><path d="m4 5 8-3 8 3v14l-8 3-8-3z"/><path d="m4 5 8 3 8-3M12 8v14"/></>,
    folder: <><path d="M3 6.5A1.5 1.5 0 0 1 4.5 5H10l2 2h7.5A1.5 1.5 0 0 1 21 8.5v10a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.5z"/></>,
    check: <><circle cx="12" cy="12" r="9"/><path d="m8 12 2.6 2.6L16.5 9"/></>,
    shield: <><path d="M12 3 20 6v5c0 5.1-3.4 8.8-8 10-4.6-1.2-8-4.9-8-10V6z"/><path d="m8.5 12 2.2 2.2 4.8-5"/></>,
    search: <><circle cx="10.8" cy="10.8" r="6.3"/><path d="m16 16 4.2 4.2"/></>,
    upload: <><path d="M12 16V3M7 8l5-5 5 5"/><path d="M4 14v5a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"/></>,
    arrow: <><path d="M5 12h14M13 6l6 6-6 6"/></>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></>,
    info: <><circle cx="12" cy="12" r="9"/><path d="M12 10v6M12 7h.01"/></>,
    bell: <><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></>,
    more: <><circle cx="5" cy="12" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="19" cy="12" r="1" fill="currentColor"/></>
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
};

function CadastralPlot() {
  return <div className="plot" role="img" aria-label="Illustrated synthetic cadastral parcel plot for ULPIN 29-08-042-011-003">
    <div className="north">N<span>↑</span></div><div className="plot-scale">0 <i/> 25m</div>
    <svg viewBox="0 0 640 345" preserveAspectRatio="xMidYMid slice">
      <g className="grid"><path d="M0 42h640M0 92h640M0 142h640M0 192h640M0 242h640M0 292h640M68 0v345M138 0v345M208 0v345M278 0v345M348 0v345M418 0v345M488 0v345M558 0v345"/></g>
      <g className="roads"><path d="M-10 269 650 110"/><path d="M-25 282 665 117"/></g>
      <g className="parcels"><path d="m80 49 92-15 52 59-67 68-89-28z"/><path d="m224 93 80-67 82 47-13 101-85 23-64-49z"/><path d="m386 73 87-42 80 66-26 85-109-8z"/><path d="m90 190 67-29 91 71-35 85-109-17z"/><path d="m248 232 40-58 85-23 45 70-65 82z"/><path d="m418 174 109 8 59 75-77 61-91-74z"/></g>
      <path className="selected-shadow" d="m224 93 80-67 82 47-13 101-85 23-64-49z"/><path className="selected" d="m224 93 80-67 82 47-13 101-85 23-64-49z"/>
      <g className="boundary-dots"><circle cx="224" cy="93" r="4"/><circle cx="304" cy="26" r="4"/><circle cx="386" cy="73" r="4"/><circle cx="373" cy="174" r="4"/><circle cx="288" cy="197" r="4"/><circle cx="224" cy="148" r="4"/></g>
      <g className="plot-label"><text x="304" y="113">PLOT 11/3</text><text x="304" y="132">1,840 m²</text></g><text className="road-label" x="494" y="135">ACCESS ROAD</text>
    </svg>
  </div>;
}

export default function Home() {
  const [docs, setDocs] = useState<Document[]>([
    { name: "Registered Sale Deed", meta: "PDF · 2.4 MB · 14 Feb 2024", tag: "Primary document", state: "Verified" },
    { name: "Khata Extract — 2024", meta: "PDF · 488 KB · 14 Feb 2024", tag: "Authority copy", state: "Verified" }
  ]);
  const [review, setReview] = useState<"idle" | "sent">("idle");
  const [notice, setNotice] = useState("");
  const [validationRows, setValidationRows] = useState<ValidationRow[]>(fallbackValidation);
  const [connection, setConnection] = useState<"fallback" | "live">("fallback");
  const [officerNote, setOfficerNote] = useState("Area variance in deed scan; please verify against the original register.");
  const fileInput = useRef<HTMLInputElement>(null);
  const onUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const uploadMeta = `${file.type || "Document"} · ${(file.size / 1024 / 1024).toFixed(1)} MB · Just now`;
    try {
      const form = new FormData(); form.append("file", file);
      const response = await fetch(`${apiBase}/api/v1/parcels/demo-parcel/documents`, { method: "POST", headers: { Authorization: "Bearer demo-citizen" }, body: form });
      if (!response.ok) throw new Error(`Upload failed (${response.status})`);
      const payload = await response.json();
      setDocs(current => [...current, { name: payload.document.original_file_name, meta: uploadMeta, tag: "API processed", state: "Uploaded" }]);
      setValidationRows(payload.validation);
      setConnection("live");
      setNotice(`${file.name} was processed by the demo API. Mock extraction results are shown below.`);
    } catch {
      setDocs(current => [...current, { name: file.name, meta: uploadMeta, tag: "Local demo fallback", state: "Uploaded" }]);
      setValidationRows(fallbackValidation);
      setConnection("fallback");
      setNotice(`API unavailable — ${file.name} is displayed using the clearly labelled local demo fallback.`);
    }
    event.target.value = "";
  };
  const sendForReview = async () => {
    try {
      const response = await fetch(`${apiBase}/api/v1/review-cases/demo-case/decision`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: "Bearer demo-officer" }, body: JSON.stringify({ resolution: "REQUIRES_DOCUMENT", notes: officerNote.length >= 3 ? officerNote : "Area variance requires document review." }) });
      if (!response.ok) throw new Error("Decision request failed");
      setConnection("live"); setNotice("Discrepancy has been recorded in the demo officer review queue.");
    } catch {
      setConnection("fallback"); setNotice("API unavailable — review is recorded in the clearly labelled local demo fallback.");
    }
    setReview("sent");
  };
  return <main className="app-shell">
    <aside className="sidebar" aria-label="Main navigation">
      <div className="brand"><span className="brand-mark">L</span><span>LANDSYNC<small>AI</small></span></div>
      <p className="side-kicker">RECORD CONSOLE</p>
      <nav><a className="nav-item" href="#overview"><Icon name="home"/>Overview</a><a className="nav-item active" href="#profile"><Icon name="parcel"/>Land profiles</a><a className="nav-item" href="#documents"><Icon name="folder"/>Document vault</a><a className="nav-item" href="#review"><Icon name="shield"/>Review queue <b>03</b></a></nav>
      <div className="sidebar-bottom"><div className="demo-lock"><Icon name="shield" size={16}/><span><strong>DEMO ENVIRONMENT</strong>All records are synthetic</span></div><button className="help-link"><span>?</span>Help & guidance</button></div>
    </aside>
    <section className="workspace">
      <header className="topbar"><button className="menu-button" aria-label="Open navigation">☰</button><div className="system-note"><span/> SIH 2026 DEMONSTRATOR <i>·</i> Not connected to live government systems</div><div className="top-actions"><label className="search"><Icon name="search" size={16}/><input aria-label="Search a ULPIN, owner, or village" placeholder="Search ULPIN, owner, village"/></label><button className="icon-button" aria-label="Notifications"><Icon name="bell" size={18}/><em/></button><button className="role"><span>RO</span>Revenue Officer <small>⌄</small></button></div></header>
      <div className="content">
        {notice && <div className="toast" role="status"><Icon name="check" size={16}/>{notice}<button onClick={() => setNotice("")} aria-label="Dismiss message">×</button></div>}
        <div className="breadcrumb">LAND PROFILES <span>/</span> KARNATAKA <span>/</span> BENGALURU RURAL <strong>DEMO RECORD</strong></div>
        <section className="profile-head" id="profile"><div><div className="eyebrow">DIGITAL LAND PROFILE <span>•</span> SYNTHETIC RECORD</div><h1>ULPIN <code>DEMO-ULPIN-27-000-124-2</code></h1><p>Survey No. 124/2, Sampurna Village · Model Tehsil · Sample District</p></div><div className="head-status"><span className="status good">● Consistency checked</span><span className="last-check">{connection === "live" ? "Demo API connected" : "Local demo fallback"}</span></div></section>
        <div className="legal-note"><Icon name="info" size={18}/><p><strong>Advisory only.</strong> LandSync AI checks document consistency against a <b>synthetic authority record</b>; it does not establish, transfer, or guarantee title.</p></div>
        <section className="verdict" id="overview"><div className="verdict-left"><span className="verdict-symbol">!</span><div><div className="eyebrow">VALIDATION SYNOPSIS</div><h2>1 material discrepancy requires review</h2><p>Area in the submitted deed differs from the synthetic authority extract by <strong>0.09 acre</strong>.</p></div></div><a href="#review" className="review-link">View review path <Icon name="arrow" size={16}/></a></section>
        <section className="metrics" aria-label="Profile summary"><article><span>RECORD CONFIDENCE</span><strong>92<small>%</small></strong><i className="meter"><b style={{width:"92%"}}/></i><p>High field-level match</p></article><article><span>FIELD MATCHES</span><strong>8<small>/9</small></strong><i className="meter teal"><b style={{width:"89%"}}/></i><p>Matched across sources</p></article><article><span>DOCUMENTS</span><strong>{docs.length}</strong><i className="meter navy"><b style={{width:"76%"}}/></i><p>In the document vault</p></article><article><span>REVIEW STATUS</span><strong className={review === "sent" ? "review-sent" : "review-open"}>{review === "sent" ? "Sent" : "Open"}</strong><p>{review === "sent" ? "Officer queue updated" : "Awaiting officer action"}</p></article></section>
        <div className="two-column"><section className="map-panel"><header className="section-header"><div><span className="eyebrow">PARCEL GIS</span><h2>Mapped parcel footprint</h2></div><button className="plain-button">Grid reference <Icon name="more" size={17}/></button></header><CadastralPlot/><footer className="map-footer"><span><i className="legend selected-legend"/>Selected parcel</span><span><i className="legend"/>Adjacent parcel</span><span className="coord">EPSG:4326 · 13.2368° N, 77.7071° E</span></footer></section>
          <section className="record-panel"><header className="section-header"><div><span className="eyebrow">RECORD DETAILS</span><h2>Registered particulars</h2></div><button className="plain-button" aria-label="More record options"><Icon name="more"/></button></header><dl className="details"><div><dt>Recorded holder</dt><dd>Ramesh Kumar <span className="verified">✓ synthetic</span></dd></div><div><dt>Land classification</dt><dd>Agricultural</dd></div><div><dt>Recorded extent</dt><dd>2.40 acre <small>9,712.46 m²</small></dd></div><div><dt>Survey number</dt><dd>124/2 <small>Plot 18B</small></dd></div><div><dt>Record ID</dt><dd>demo-parcel</dd></div><div><dt>Jurisdiction</dt><dd>Model Tehsil, Sample District</dd></div></dl><div className="source-rank"><span>Source hierarchy</span><div><b>1</b> Synthetic authority extract <i>›</i> <b>2</b> Mock extraction <i>›</i> <b>3</b> Citizen upload</div></div></section></div>
        <section className="document-panel" id="documents"><header className="section-header"><div><span className="eyebrow">DOCUMENT VAULT</span><h2>Source documents & provenance</h2></div><button className="upload-button" onClick={() => fileInput.current?.click()}><Icon name="upload" size={16}/>Upload document</button><input ref={fileInput} className="sr-only" type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={onUpload}/></header><div className="document-list">{docs.map((doc, index) => <article className="document-row" key={`${doc.name}-${index}`}><span className="doc-icon">{doc.name.toLowerCase().endsWith("pdf") || doc.name.includes("Deed") || doc.name.includes("Extract") ? "PDF" : "FILE"}</span><div><h3>{doc.name} <em>{doc.tag}</em></h3><p>{doc.meta}</p></div><span className={`status ${doc.state === "Verified" ? "good" : "uploaded"}`}>● {doc.state}</span><button className="plain-button" aria-label={`More options for ${doc.name}`}><Icon name="more"/></button></article>)}</div></section>
        <section className="validation-panel"><header className="section-header"><div><span className="eyebrow">EXTRACTION & VALIDATION</span><h2>What was compared</h2></div><span className="synthetic-chip">{connection === "live" ? "Demo API result" : "Local demo fallback"}</span></header><div className="compare-table" role="table" aria-label="Document extraction and authority comparison"><div className="compare-row table-head" role="row"><span>FIELD</span><span>SUBMITTED DOCUMENT <small>Mock AI extraction</small></span><span>SYNTHETIC AUTHORITY EXTRACT</span><span>RESULT</span></div>{validationRows.map(row => { const match = row.result === "MATCH"; return <div className={`compare-row ${match ? "" : "alert"}`} role="row" key={row.field}><b>{row.field.replace("_", " ")}</b><span>{row.value_a} <i>{Math.round(row.confidence * 100)}% confidence</i></span><span>{row.value_b}</span><span className={`result ${match ? "match" : "mismatch"}`}>{match ? "✓ MATCH" : "! REVIEW"}</span></div>; })}</div></section>
        <section className="review-panel" id="review"><div className="review-main"><span className="eyebrow">OFFICER REVIEW</span><h2>{review === "sent" ? "Discrepancy sent to the review queue" : "Route this discrepancy for review"}</h2><p>{review === "sent" ? "The synthetic demo queue has been updated. An officer may compare the two stated areas and record an advisory response." : "This workflow flags an inconsistency for human examination. It does not determine legal ownership or title."}</p><div className="review-controls"><label><span>Officer note</span><textarea placeholder="Add context for the officer (optional)" value={officerNote} onChange={event => setOfficerNote(event.target.value)}/></label><button className={review === "sent" ? "sent-button" : "send-button"} onClick={sendForReview} disabled={review === "sent"}>{review === "sent" ? <><Icon name="check" size={17}/>Sent for review</> : <><Icon name="shield" size={17}/>Assign & send for review</>}</button></div></div><aside className="audit"><span className="eyebrow">AUDIT TIMELINE</span><ol><li><i className="done"/><div><b>Consistency check completed</b><small>Today · 10:42 IST</small></div></li><li><i className="warn"/><div><b>Area variance flagged</b><small>Today · 10:42 IST</small></div></li><li><i className={review === "sent" ? "done" : "pending"}/><div><b>{review === "sent" ? "Assigned to officer queue" : "Officer review pending"}</b><small>{review === "sent" ? "Just now" : "No action recorded"}</small></div></li></ol></aside></section>
        <footer className="page-footer">LANDSYNC AI · SIH 2026 DEMO <span>All data on this screen is synthetic. No live government registry is queried.</span></footer>
      </div>
    </section>
  </main>;
}
