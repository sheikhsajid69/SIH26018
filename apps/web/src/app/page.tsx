"use client";

import { ChangeEvent, useEffect, useRef, useState } from "react";
import { SYNTHETIC_SCENARIOS, ScenarioData } from "./scenarios";

type RoleType = "citizen" | "officer" | "admin";

type DocumentItem = {
  id: string;
  name: string;
  meta: string;
  tag: string;
  state: "Verified" | "Uploaded";
  sha256?: string;
  storage_key?: string;
};

type ValidationRow = {
  field: string;
  source_a: string;
  value_a: string;
  source_b: string;
  value_b: string;
  confidence: number;
  result: "MATCH" | "PARTIAL_MATCH" | "MISMATCH" | "MISSING" | "REVIEW_REQUIRED";
  severity?: string;
  explanation: string;
};

type ReviewCaseItem = {
  id: string;
  parcel_id: string;
  reason: string;
  severity: string;
  status: string;
  priority: string;
  discrepancy_field?: string;
  claimed_value?: string;
  authoritative_value?: string;
  assigned_officer?: string | null;
  reviewer_notes?: string | null;
  resolution?: string | null;
  resolved_at?: string | null;
};

type MutationEventItem = {
  id: string;
  mutation_number: string;
  event_type: string;
  recorded_date: string;
  parties_involved: string;
  description: string;
  order_reference: string;
};

type AdminHealth = {
  system: string;
  state_adapters: Array<{ name: string; type: string; status: string; jurisdiction: string; parcels_loaded: number }>;
  document_providers: Array<{ name: string; version: string; status: string; mode: string }>;
  storage: { type: string; root: string; hashing_algorithm: string; documents_stored: number };
  audit_events_count: number;
  open_review_cases: number;
};

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const fallbackHistory: MutationEventItem[] = [
  {
    id: "mut-001",
    mutation_number: "MR-12/1994",
    event_type: "PARTITION",
    recorded_date: "1994-08-11",
    parties_involved: "Ancestral partition among Suresh Kumar & Brothers",
    description: "Ancestral land division in Sy No 124 creating sub-division 124/2 (extent 2.40 acre).",
    order_reference: "Tahsildar Order No. LND/CR/1994/88"
  },
  {
    id: "mut-002",
    mutation_number: "MR-44/2012",
    event_type: "SUCCESSION",
    recorded_date: "2012-04-18",
    parties_involved: "Inheritance by Ramesh Kumar upon succession",
    description: "Succession entry sanctioned in favour of legal heir Ramesh Kumar.",
    order_reference: "Revenue Inspector Sanction RI/MUT/2012/104"
  },
  {
    id: "mut-003",
    mutation_number: "DEMARC-2021-09",
    event_type: "DEMARCATION",
    recorded_date: "2021-11-04",
    parties_involved: "ADLR Taluk Survey Division",
    description: "Cadastral field sketch digitization and boundary fixing for Sy No 124/2.",
    order_reference: "Survey Settlement Order SO-2021/772"
  }
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
    layers: <><path d="m12 2 10 5-10 5L2 7l10-5z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/></>,
    printer: <><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></>,
    compass: <><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></>,
    more: <><circle cx="5" cy="12" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="19" cy="12" r="1" fill="currentColor"/></>
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] ?? paths.info}</svg>;
};

function CadastralGISPlot({
  scenario,
  showAuthority,
  showDeed,
  showBlueprint
}: {
  scenario: ScenarioData;
  showAuthority: boolean;
  showDeed: boolean;
  showBlueprint: boolean;
}) {
  return (
    <div className="plot" role="img" aria-label={`Cadastral GIS and Computer Vision plot for ${scenario.survey_number}`}>
      <div className="north">N<span>↑</span></div>
      <div className="plot-scale">0 <i /> 25m</div>

      <svg viewBox="0 0 640 345" preserveAspectRatio="xMidYMid slice">
        <g className="grid">
          <path d="M0 42h640M0 92h640M0 142h640M0 192h640M0 242h640M0 292h640M68 0v345M138 0v345M208 0v345M278 0v345M348 0v345M418 0v345M488 0v345M558 0v345"/>
        </g>
        <g className="roads">
          <path d="M-10 269 650 110"/>
          <path d="M-25 282 665 117"/>
        </g>
        <g className="parcels">
          <path d="m80 49 92-15 52 59-67 68-89-28z"/>
          <path d="m386 73 87-42 80 66-26 85-109-8z"/>
          <path d="m90 190 67-29 91 71-35 85-109-17z"/>
          <path d="m248 232 40-58 85-23 45 70-65 82z"/>
          <path d="m418 174 109 8 59 75-77 61-91-74z"/>
        </g>

        {/* 1. Authoritative Cadastral Parcel Geometry */}
        {showAuthority && (
          <>
            <path className="selected-shadow" d="m224 93 80-67 82 47-13 101-85 23-64-49z"/>
            <path className="selected" d="m224 93 80-67 82 47-13 101-85 23-64-49z"/>
            <g className="boundary-dots">
              <circle cx="224" cy="93" r="4.5"/>
              <circle cx="304" cy="26" r="4.5"/>
              <circle cx="386" cy="73" r="4.5"/>
              <circle cx="373" cy="174" r="4.5"/>
              <circle cx="288" cy="197" r="4.5"/>
              <circle cx="224" cy="148" r="4.5"/>
            </g>
          </>
        )}

        {/* 2. Extracted Deed Boundary (Advisory) */}
        {showDeed && (
          <path
            className="deed-boundary"
            d={
              scenario.parcel_id === "SYN-PARCEL-002"
                ? "m224 93 80-67 74 48-12 95-78 21-64-49z"
                : scenario.parcel_id === "SYN-PARCEL-008"
                ? "m224 93 80-67 88 47-13 105-85 23-64-49z"
                : "m224 93 80-67 82 47-13 101-85 23-64-49z"
            }
          />
        )}

        {/* 3. Computer Vision Blueprint Sketch Overlay */}
        {showBlueprint && (
          <path className="blueprint-sketch" d="m221 95 81-65 80 46-15 98-82 22-64-49z"/>
        )}

        <g className="plot-label">
          <text x="304" y="113">SY NO. {scenario.survey_number} (PLOT {scenario.plot_number})</text>
          <text x="304" y="132">Authoritative Extent: {scenario.area} ({scenario.normalized_area_sqm.toLocaleString()} m²)</text>
        </g>
        <text className="road-label" x="494" y="135">ACCESS ROAD (12M WIDE)</text>
      </svg>
    </div>
  );
}

export default function Home() {
  const [role, setRole] = useState<RoleType>("officer");
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"profile" | "queue" | "history" | "admin">("profile");

  // Selected scenario state (Default: Scenario 2 - Area Mismatch)
  const [selectedScenarioIdx, setSelectedScenarioIdx] = useState(1);
  const scenario = SYNTHETIC_SCENARIOS[selectedScenarioIdx] ?? SYNTHETIC_SCENARIOS[0];

  const [searchQuery, setSearchQuery] = useState("");

  const [docs, setDocs] = useState<DocumentItem[]>([
    {
      id: "doc-seed-1",
      name: scenario.doc_name,
      meta: `PDF · 2.4 MB · ${scenario.doc_type}`,
      tag: "Deed Evidence",
      state: "Verified",
      sha256: "f8c238346ffe3a51d5124e09056fe5b310b36e44d667566952b7b5e3a66dfb8b"
    },
    {
      id: "doc-seed-2",
      name: "RoR / Record of Rights Extract (RTC)",
      meta: "PDF · 488 KB · Authority Record Extract",
      tag: "Authority Extract",
      state: "Verified",
      sha256: "9b34ea1209bca7431289fe12998a410974bfa5619374020956281726aedcba31"
    }
  ]);

  const [mutationHistory, setMutationHistory] = useState<MutationEventItem[]>(fallbackHistory);
  const [reviewCases, setReviewCases] = useState<ReviewCaseItem[]>([
    {
      id: `SYN-CASE-${scenario.parcel_id.split("-")[2]}`,
      parcel_id: scenario.parcel_id,
      reason: scenario.reason,
      severity: scenario.priority === "P1_HIGH" ? "HIGH" : "MEDIUM",
      priority: scenario.priority,
      discrepancy_field: scenario.discrepancy_field,
      claimed_value: scenario.doc_area !== scenario.area ? scenario.doc_area : scenario.doc_holder,
      authoritative_value: scenario.doc_area !== scenario.area ? scenario.area : scenario.holder_name,
      status: "OPEN"
    }
  ]);

  const [selectedCaseId, setSelectedCaseId] = useState(`SYN-CASE-${scenario.parcel_id.split("-")[2]}`);
  const [resolutionChoice, setResolutionChoice] = useState<"ACCEPTED_FOR_CORRECTION" | "REQUIRES_DOCUMENT" | "NO_ACTION">("REQUIRES_DOCUMENT");
  const [officerNote, setOfficerNote] = useState("Discrepancy flagged for physical register verification and field re-survey.");
  const [reviewSent, setReviewSent] = useState(false);
  const [notice, setNotice] = useState("");
  const [connection, setConnection] = useState<"live" | "fallback">("live");

  // GIS Layer toggles
  const [showAuthorityLayer, setShowAuthorityLayer] = useState(true);
  const [showDeedLayer, setShowDeedLayer] = useState(true);
  const [showBlueprintLayer, setShowBlueprintLayer] = useState(true);

  // Modal Report state
  const [showReportModal, setShowReportModal] = useState(false);
  const [adminHealth, setAdminHealth] = useState<AdminHealth | null>(null);

  const fileInput = useRef<HTMLInputElement>(null);

  const getBearerToken = () => {
    if (role === "citizen") return "demo-citizen";
    if (role === "officer") return "demo-officer";
    return "demo-admin";
  };

  // Build validation rows dynamically from current scenario
  const currentValidationRows: ValidationRow[] = [
    {
      field: "owner",
      source_a: "AI-extracted document (MOCK)",
      value_a: scenario.doc_holder,
      source_b: "SYNTHETIC DEMO authority record",
      value_b: scenario.holder_name,
      confidence: scenario.confidence,
      result:
        scenario.doc_holder === scenario.holder_name
          ? "MATCH"
          : scenario.scenario.includes("Partial")
          ? "PARTIAL_MATCH"
          : "MISMATCH",
      explanation:
        scenario.doc_holder === scenario.holder_name
          ? `Holder name '${scenario.doc_holder}' matches authoritative record.`
          : `Holder mismatch: '${scenario.doc_holder}' vs '${scenario.holder_name}'.`
    },
    {
      field: "survey_number",
      source_a: "AI-extracted document (MOCK)",
      value_a: scenario.doc_survey,
      source_b: "SYNTHETIC DEMO authority record",
      value_b: scenario.survey_number,
      confidence: scenario.confidence,
      result: scenario.doc_survey === scenario.survey_number ? "MATCH" : "MISMATCH",
      explanation:
        scenario.doc_survey === scenario.survey_number
          ? `Survey number matches authoritative record ('${scenario.survey_number}').`
          : `Survey discrepancy: Deed states '${scenario.doc_survey}', authority states '${scenario.survey_number}'.`
    },
    {
      field: "plot_number",
      source_a: "AI-extracted document (MOCK)",
      value_a: scenario.plot_number,
      source_b: "SYNTHETIC DEMO authority record",
      value_b: scenario.plot_number,
      confidence: 0.94,
      result: "MATCH",
      explanation: `Plot number matches authoritative record ('${scenario.plot_number}').`
    },
    {
      field: "area",
      source_a: "AI-extracted document (MOCK)",
      value_a: scenario.doc_area,
      source_b: "SYNTHETIC DEMO authority record",
      value_b: scenario.area,
      confidence: scenario.confidence,
      result:
        scenario.doc_area === scenario.area
          ? "MATCH"
          : scenario.doc_area === "NOT_AVAILABLE"
          ? "MISSING"
          : "MISMATCH",
      explanation:
        scenario.doc_area === scenario.area
          ? `Area extent matches authoritative record (${scenario.area} / ${scenario.normalized_area_sqm} m²).`
          : scenario.doc_area === "NOT_AVAILABLE"
          ? "Extent attribute missing from uploaded deed schedule."
          : `Area variance detected: Document reports ${scenario.doc_area}, authority reports ${scenario.area}. Human verification required.`
    },
    {
      field: "village",
      source_a: "AI-extracted document (MOCK)",
      value_a: scenario.village,
      source_b: "SYNTHETIC DEMO authority record",
      value_b: scenario.village,
      confidence: 0.96,
      result: "MATCH",
      explanation: `Village jurisdiction matches authoritative record ('${scenario.village}').`
    },
    {
      field: "land_use",
      source_a: "AI-extracted document (MOCK)",
      value_a: scenario.scenario.includes("Land Use") ? "Commercial (NA)" : scenario.land_use,
      source_b: "SYNTHETIC DEMO authority record",
      value_b: scenario.land_use,
      confidence: 0.92,
      result: scenario.scenario.includes("Land Use") ? "MISMATCH" : "MATCH",
      explanation: scenario.scenario.includes("Land Use")
        ? "Unsanctioned conversion: Commercial NA claim vs Agricultural in RoR."
        : `Land classification matches authoritative record ('${scenario.land_use}').`
    }
  ];

  // When scenario changes, update docs and cases
  useEffect(() => {
    setDocs([
      {
        id: `doc-${scenario.parcel_id.toLowerCase()}-1`,
        name: scenario.doc_name,
        meta: `PDF · 2.4 MB · ${scenario.doc_type}`,
        tag: "Deed Evidence",
        state: "Verified",
        sha256: "f8c238346ffe3a51d5124e09056fe5b310b36e44d667566952b7b5e3a66dfb8b"
      },
      {
        id: `doc-${scenario.parcel_id.toLowerCase()}-2`,
        name: `RTC Extract — ${scenario.survey_number}`,
        meta: "PDF · 488 KB · Authority Record Extract",
        tag: "Authority Extract",
        state: "Verified",
        sha256: "9b34ea1209bca7431289fe12998a410974bfa5619374020956281726aedcba31"
      }
    ]);

    const caseId = `SYN-CASE-${scenario.parcel_id.split("-")[2]}`;
    setReviewCases([
      {
        id: caseId,
        parcel_id: scenario.parcel_id,
        reason: scenario.reason,
        severity: scenario.priority === "P1_HIGH" ? "HIGH" : "MEDIUM",
        priority: scenario.priority,
        discrepancy_field: scenario.discrepancy_field,
        claimed_value: scenario.doc_area !== scenario.area ? scenario.doc_area : scenario.doc_holder,
        authoritative_value: scenario.doc_area !== scenario.area ? scenario.area : scenario.holder_name,
        status: scenario.expected_result === "MATCH" ? "RESOLVED" : "OPEN"
      }
    ]);
    setSelectedCaseId(caseId);
    setReviewSent(scenario.expected_result === "MATCH");
  }, [selectedScenarioIdx]);

  // Initial fetch from API
  useEffect(() => {
    async function loadInitialData() {
      try {
        const token = getBearerToken();
        const headers = { Authorization: `Bearer ${token}` };

        // 1. History
        const histRes = await fetch(`${apiBase}/api/v1/parcels/demo-parcel/history`, { headers });
        if (histRes.ok) {
          const histData = await histRes.json();
          if (histData.mutation_history) setMutationHistory(histData.mutation_history);
        }
      } catch {
        setConnection("fallback");
      }
    }
    loadInitialData();
  }, [role]);

  // Search filter
  const handleSearch = (q: string) => {
    setSearchQuery(q);
    if (!q.trim()) return;
    const cleanQ = q.trim().toLowerCase();
    const foundIdx = SYNTHETIC_SCENARIOS.findIndex(
      s =>
        s.ulpin.toLowerCase().includes(cleanQ) ||
        s.survey_number.toLowerCase().includes(cleanQ) ||
        s.holder_name.toLowerCase().includes(cleanQ) ||
        s.parcel_id.toLowerCase().includes(cleanQ) ||
        s.village.toLowerCase().includes(cleanQ)
    );
    if (foundIdx !== -1) {
      setSelectedScenarioIdx(foundIdx);
      setNotice(`Found & switched to: ${SYNTHETIC_SCENARIOS[foundIdx].scenario} (${SYNTHETIC_SCENARIOS[foundIdx].survey_number})`);
    }
  };

  // Handle document upload
  const onUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const uploadMeta = `${file.type || "Document"} · ${(file.size / 1024 / 1024).toFixed(1)} MB · Just now`;
    try {
      const form = new FormData();
      form.append("file", file);
      const response = await fetch(`${apiBase}/api/v1/parcels/demo-parcel/documents`, {
        method: "POST",
        headers: { Authorization: "Bearer demo-citizen" },
        body: form
      });

      if (!response.ok) throw new Error(`Upload failed (${response.status})`);
      const payload = await response.json();

      const newDoc: DocumentItem = {
        id: payload.document.id,
        name: payload.document.original_file_name,
        meta: uploadMeta,
        tag: "API Extracted (MOCK)",
        state: "Uploaded",
        sha256: payload.document.sha256,
        storage_key: payload.document.storage_key
      };

      setDocs(current => [newDoc, ...current]);
      setConnection("live");
      setNotice(`Document '${file.name}' hashed with SHA-256 and processed by the AI validation pipeline.`);
    } catch {
      const fallbackDoc: DocumentItem = {
        id: `doc-${Date.now()}`,
        name: file.name,
        meta: uploadMeta,
        tag: "Local Fallback",
        state: "Uploaded",
        sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      };
      setDocs(current => [fallbackDoc, ...current]);
      setConnection("fallback");
      setNotice(`Demo API unavailable — '${file.name}' added in local offline demonstration mode.`);
    }
    event.target.value = "";
  };

  // Handle blueprint analysis
  const triggerBlueprintAnalysis = async () => {
    try {
      const dummyFile = new Blob(["MOCK_BLUEPRINT_RASTER_DATA"], { type: "image/png" });
      const form = new FormData();
      form.append("file", dummyFile, "cadastral_sketch_124_2.png");

      const res = await fetch(`${apiBase}/api/v1/parcels/demo-parcel/blueprint`, {
        method: "POST",
        headers: { Authorization: "Bearer demo-citizen" },
        body: form
      });

      if (res.ok) {
        setShowBlueprintLayer(true);
        setNotice("Computer Vision Blueprint analysis completed: 4 boundary dimensions detected with 86% confidence (Advisory).");
      }
    } catch {
      setNotice("Blueprint CV provider executed in local demonstration mode.");
    }
  };

  // Handle officer review decision
  const handleRecordDecision = async () => {
    try {
      const response = await fetch(`${apiBase}/api/v1/review-cases/demo-case/decision`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer demo-officer"
        },
        body: JSON.stringify({
          resolution: resolutionChoice,
          notes: officerNote.length >= 3 ? officerNote : "Verified against survey schedule. Physical re-check advised."
        })
      });

      if (!response.ok) throw new Error("Decision request failed");
      const updatedCase: ReviewCaseItem = await response.json();

      setReviewCases(cases => cases.map(c => (c.id === selectedCaseId ? { ...c, status: "RESOLVED", resolution: resolutionChoice } : c)));
      setReviewSent(true);
      setConnection("live");
      setNotice(`Decision '${resolutionChoice}' recorded for case ${selectedCaseId}. Append-only audit event created.`);
    } catch {
      setReviewSent(true);
      setConnection("fallback");
      setNotice("Decision recorded in clearly labelled local offline demonstration mode.");
    }
  };

  // Load Admin Health
  const loadAdminHealth = async () => {
    try {
      const res = await fetch(`${apiBase}/api/v1/admin/health`, {
        headers: { Authorization: "Bearer demo-admin" }
      });
      if (res.ok) {
        const data = await res.json();
        setAdminHealth(data);
      }
    } catch {
      setAdminHealth({
        system: "LANDSYNC AI Core",
        state_adapters: [{ name: "DemoAuthorityAdapter", type: "SYNTHETIC_MOCK", status: "HEALTHY", jurisdiction: "Karnataka (Demo State)", parcels_loaded: 14 }],
        document_providers: [{ name: "mock-document-ai", version: "demo-1.2", status: "OPERATIONAL", mode: "DETERMINISTIC_MOCK" }],
        storage: { type: "LocalEvidenceStore", root: ".landsync-storage", hashing_algorithm: "SHA-256", documents_stored: docs.length },
        audit_events_count: 5,
        open_review_cases: 1
      });
    }
  };

  const isConsistent = scenario.expected_result === "MATCH";

  return (
    <main className="app-shell">
      {/* Sidebar Navigation */}
      <aside className="sidebar" aria-label="Main navigation">
        <div className="brand">
          <span className="brand-mark">L</span>
          <span>
            LANDSYNC<small>AI</small>
          </span>
        </div>
        <p className="side-kicker">SMART INDIA HACKATHON 2026</p>
        <nav>
          <button
            className={`nav-item ${activeTab === "profile" ? "active" : ""}`}
            onClick={() => setActiveTab("profile")}
          >
            <Icon name="parcel" />
            Digital Land Profile
          </button>
          <button
            className={`nav-item ${activeTab === "queue" ? "active" : ""}`}
            onClick={() => setActiveTab("queue")}
          >
            <Icon name="shield" />
            Officer Review Queue <b>{isConsistent ? "0" : "01"}</b>
          </button>
          <button
            className={`nav-item ${activeTab === "history" ? "active" : ""}`}
            onClick={() => setActiveTab("history")}
          >
            <Icon name="clock" />
            Mutation History
          </button>
          {role === "admin" && (
            <button
              className={`nav-item ${activeTab === "admin" ? "active" : ""}`}
              onClick={() => {
                setActiveTab("admin");
                loadAdminHealth();
              }}
            >
              <Icon name="layers" />
              System Admin Health
            </button>
          )}
        </nav>

        <div className="sidebar-bottom">
          <div className="demo-lock">
            <Icon name="shield" size={16} />
            <span>
              <strong>SYNTHETIC DEMO ENVIRONMENT</strong>
              SIH26018 · Team Void · No government database is contacted
            </span>
          </div>
          <button className="help-link" onClick={() => setShowReportModal(true)}>
            <span>?</span>
            View Consistency Report
          </button>
        </div>
      </aside>

      {/* Main Workspace */}
      <section className="workspace">
        {/* Topbar Header */}
        <header className="topbar">
          <button className="menu-button" aria-label="Open navigation">
            ☰
          </button>
          <div className="system-note">
            <span />
            SIH 2026 DEMONSTRATOR <i>·</i>
            {connection === "live" ? "FastAPI Backend Connected" : "Local Demo Fallback Active"}
          </div>

          <div className="top-actions">
            {/* Search Input */}
            <label className="search">
              <Icon name="search" size={16} />
              <input
                aria-label="Search by ULPIN, owner, or survey number"
                placeholder="Search ULPIN, owner, survey..."
                value={searchQuery}
                onChange={e => handleSearch(e.target.value)}
              />
            </label>

            <button
              className="report-button"
              onClick={() => setShowReportModal(true)}
              title="Open full Digital Land Profile & Consistency Report"
            >
              <Icon name="printer" size={15} />
              Consistency Report
            </button>

            {/* Interactive Role Switcher */}
            <div className="role-switcher-container">
              <button
                className="role"
                onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
                aria-expanded={roleDropdownOpen}
              >
                <span>{role === "citizen" ? "CZ" : role === "officer" ? "RO" : "AD"}</span>
                {role === "citizen"
                  ? "Landowner (Citizen)"
                  : role === "officer"
                  ? "Revenue Officer"
                  : "System Administrator"}
                <small>⌄</small>
              </button>

              {roleDropdownOpen && (
                <div className="role-dropdown">
                  <button
                    className={`role-opt ${role === "citizen" ? "selected" : ""}`}
                    onClick={() => {
                      setRole("citizen");
                      setRoleDropdownOpen(false);
                      setNotice("Switched role to Citizen / Landowner (demo-citizen).");
                    }}
                  >
                    <span>CZ</span>
                    <div>
                      <strong>Landowner / Citizen</strong>
                      <div style={{ fontSize: "10px", color: "#64748b" }}>View profile & upload deeds</div>
                    </div>
                  </button>
                  <button
                    className={`role-opt ${role === "officer" ? "selected" : ""}`}
                    onClick={() => {
                      setRole("officer");
                      setRoleDropdownOpen(false);
                      setNotice("Switched role to Revenue Officer (demo-officer). Full review access granted.");
                    }}
                  >
                    <span>RO</span>
                    <div>
                      <strong>Revenue Officer</strong>
                      <div style={{ fontSize: "10px", color: "#64748b" }}>Resolve discrepancy cases</div>
                    </div>
                  </button>
                  <button
                    className={`role-opt ${role === "admin" ? "selected" : ""}`}
                    onClick={() => {
                      setRole("admin");
                      setRoleDropdownOpen(false);
                      setNotice("Switched role to Administrator (demo-admin).");
                    }}
                  >
                    <span>AD</span>
                    <div>
                      <strong>Administrator</strong>
                      <div style={{ fontSize: "10px", color: "#64748b" }}>Manage adapters & audit health</div>
                    </div>
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Workspace Content */}
        <div className="content">
          {notice && (
            <div className="toast" role="status">
              <Icon name="check" size={16} />
              <span>{notice}</span>
              <button onClick={() => setNotice("")} aria-label="Dismiss message">
                ×
              </button>
            </div>
          )}

          {/* Scenario Selector Banner */}
          <div
            style={{
              background: "#102a43",
              color: "#fff",
              padding: "10px 16px",
              borderRadius: "6px",
              marginBottom: "16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "10px"
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "11px", fontWeight: "bold", color: "#e7b66d", textTransform: "uppercase" }}>
                🎯 Demo Scenario Preset:
              </span>
              <select
                value={selectedScenarioIdx}
                onChange={e => setSelectedScenarioIdx(Number(e.target.value))}
                style={{
                  background: "#173d5e",
                  color: "#fff",
                  border: "1px solid #2e5984",
                  borderRadius: "4px",
                  padding: "5px 10px",
                  fontSize: "12px",
                  fontWeight: "600",
                  cursor: "pointer"
                }}
              >
                {SYNTHETIC_SCENARIOS.map((sc, i) => (
                  <option key={sc.parcel_id} value={i}>
                    {sc.scenario} — {sc.survey_number} ({sc.holder_name})
                  </option>
                ))}
              </select>
            </div>

            <div style={{ fontSize: "11px", color: "#cbd5e1" }}>
              Expected Evaluation:{" "}
              <b
                style={{
                  color:
                    scenario.expected_result === "MATCH"
                      ? "#34d399"
                      : scenario.expected_result === "PARTIAL_MATCH"
                      ? "#fbbf24"
                      : "#f87171"
                }}
              >
                {scenario.expected_result}
              </b>
            </div>
          </div>

          {/* Breadcrumbs & Title */}
          <div className="breadcrumb">
            LAND PROFILES <span>/</span> KARNATAKA <span>/</span> SYNTHETIC DISTRICT <span>/</span>
            <strong>{scenario.parcel_id}</strong>
          </div>

          <section className="profile-head" id="profile">
            <div>
              <div className="eyebrow">
                DIGITAL LAND PROFILE <span>•</span> SYNTHETIC RECORD
              </div>
              <h1>
                ULPIN <code>{scenario.ulpin}</code>
              </h1>
              <p>
                Survey No. {scenario.survey_number} · Plot {scenario.plot_number} · {scenario.village} · {scenario.taluk} · {scenario.district}
              </p>
            </div>
            <div className="head-status">
              <span className={`status ${isConsistent ? "good" : "warn"}`}>
                ● {isConsistent ? "Advisory Consistency Confirmed" : "Review Required"}
              </span>
              <span className="last-check">
                Source Hierarchy: <b>Authoritative Extract › AI Extraction › User Evidence</b>
              </span>
            </div>
          </section>

          {/* Legal / Institutional Advisory Notice */}
          <div className="legal-note">
            <Icon name="info" size={20} />
            <p>
              <strong>ADVISORY INTEROPERABILITY LAYER:</strong> LandSync AI validates document consistency and spatial
              alignment against synthetic authority records. It does <b>NOT</b> establish legal title, convey ownership, or
              substitute for authorized revenue court proceedings.
            </p>
          </div>

          {/* View Tab Navigation */}
          <div style={{ display: "flex", gap: "10px", marginTop: "18px" }}>
            <button
              className={`upload-button ${activeTab === "profile" ? "" : "sent-button"}`}
              onClick={() => setActiveTab("profile")}
            >
              <Icon name="parcel" size={15} /> Land Profile & GIS
            </button>
            <button
              className={`upload-button ${activeTab === "queue" ? "" : "sent-button"}`}
              onClick={() => setActiveTab("queue")}
            >
              <Icon name="shield" size={15} /> Officer Discrepancy Queue
            </button>
            <button
              className={`upload-button ${activeTab === "history" ? "" : "sent-button"}`}
              onClick={() => setActiveTab("history")}
            >
              <Icon name="clock" size={15} /> Mutation Timeline
            </button>
            {role === "admin" && (
              <button
                className={`upload-button ${activeTab === "admin" ? "" : "sent-button"}`}
                onClick={() => {
                  setActiveTab("admin");
                  loadAdminHealth();
                }}
              >
                <Icon name="layers" size={15} /> Admin Health Console
              </button>
            )}
          </div>

          {/* TAB 1: DIGITAL LAND PROFILE & GIS */}
          {activeTab === "profile" && (
            <>
              {/* Validation Synopsis Banner */}
              <section className="verdict" id="overview">
                <div className="verdict-left">
                  <span className="verdict-symbol">{isConsistent ? "✓" : "!"}</span>
                  <div>
                    <div className="eyebrow">CONSISTENCY EVALUATION SYNOPSIS</div>
                    <h2>
                      {isConsistent
                        ? "All Primary Land Record Attributes are Consistent"
                        : "Material Discrepancy Detected — Routed to Officer Review"}
                    </h2>
                    <p>{scenario.reason}</p>
                  </div>
                </div>
                {!isConsistent && (
                  <button className="review-link" onClick={() => setActiveTab("queue")}>
                    Inspect Discrepancy Case <Icon name="arrow" size={16} />
                  </button>
                )}
              </section>

              {/* Metrics */}
              <section className="metrics" aria-label="Profile summary">
                <article>
                  <span>RECORD CONFIDENCE</span>
                  <strong>
                    {Math.round(scenario.confidence * 100)}
                    <small>%</small>
                  </strong>
                  <i className="meter">
                    <b style={{ width: `${Math.round(scenario.confidence * 100)}%` }} />
                  </i>
                  <p>{scenario.confidence < 0.75 ? "Low confidence flag" : "High field match"}</p>
                </article>
                <article>
                  <span>FIELD CONSISTENCY</span>
                  <strong>
                    {isConsistent ? "6" : "5"}
                    <small>/6</small>
                  </strong>
                  <i className="meter teal">
                    <b style={{ width: isConsistent ? "100%" : "83%" }} />
                  </i>
                  <p>{isConsistent ? "All fields matched" : "Variance detected"}</p>
                </article>
                <article>
                  <span>EVIDENCE VAULT</span>
                  <strong>{docs.length}</strong>
                  <i className="meter navy">
                    <b style={{ width: "100%" }} />
                  </i>
                  <p>SHA-256 hashed documents</p>
                </article>
                <article>
                  <span>HUMAN REVIEW</span>
                  <strong className={reviewSent ? "review-sent" : "review-open"}>
                    {reviewSent ? "Resolved" : isConsistent ? "Not Needed" : "Review Open"}
                  </strong>
                  <p>{reviewSent ? "Officer decision recorded" : isConsistent ? "Consistent record" : "Pending officer action"}</p>
                </article>
              </section>

              {/* 2-Column: Cadastral GIS & Record Particulars */}
              <div className="two-column">
                {/* GIS Panel */}
                <section className="map-panel">
                  <header className="section-header">
                    <div>
                      <span className="eyebrow">SPATIAL INTELLIGENCE & GIS</span>
                      <h2>Cadastral Footprint & Boundary Overlay</h2>
                    </div>
                    <button
                      className="plain-button"
                      onClick={triggerBlueprintAnalysis}
                      title="Run mock Computer Vision boundary detection on sketch"
                    >
                      <Icon name="compass" size={16} /> CV Blueprint Scan
                    </button>
                  </header>

                  {/* Layer Toggles */}
                  <div className="gis-layers">
                    <span>Display Layers:</span>
                    <label className="layer-toggle">
                      <input
                        type="checkbox"
                        checked={showAuthorityLayer}
                        onChange={e => setShowAuthorityLayer(e.target.checked)}
                      />
                      Cadastral Boundary ({scenario.area})
                    </label>
                    <label className="layer-toggle">
                      <input
                        type="checkbox"
                        checked={showDeedLayer}
                        onChange={e => setShowDeedLayer(e.target.checked)}
                      />
                      Deed Claim ({scenario.doc_area})
                    </label>
                    <label className="layer-toggle">
                      <input
                        type="checkbox"
                        checked={showBlueprintLayer}
                        onChange={e => setShowBlueprintLayer(e.target.checked)}
                      />
                      CV Sketch Overlay
                    </label>
                  </div>

                  <CadastralGISPlot
                    scenario={scenario}
                    showAuthority={showAuthorityLayer}
                    showDeed={showDeedLayer}
                    showBlueprint={showBlueprintLayer}
                  />

                  <footer className="map-footer">
                    <span>
                      <i className="legend selected-legend" /> Authoritative Cadastral (PostGIS)
                    </span>
                    <span>
                      <i className="legend deed-legend" /> Submitted Deed Extent
                    </span>
                    <span>
                      <i className="legend sketch-legend" /> Advisory CV Edge
                    </span>
                    <span className="coord">EPSG:4326 · 12.9716° N, 77.5944° E</span>
                  </footer>
                </section>

                {/* Record Particulars Panel */}
                <section className="record-panel">
                  <header className="section-header">
                    <div>
                      <span className="eyebrow">AUTHORITATIVE PARTICULARS</span>
                      <h2>Registered Land Data</h2>
                    </div>
                    <span className="badge-synthetic">SYNTHETIC RECORD</span>
                  </header>

                  <dl className="details">
                    <div>
                      <dt>Recorded Holder</dt>
                      <dd>
                        {scenario.holder_name} <span className="verified">✓ Registered Khatedar</span>
                      </dd>
                    </div>
                    <div>
                      <dt>Survey Number</dt>
                      <dd>
                        {scenario.survey_number} <small>Plot {scenario.plot_number}</small>
                      </dd>
                    </div>
                    <div>
                      <dt>Authoritative Extent</dt>
                      <dd>
                        {scenario.area} <small>({scenario.normalized_area_sqm.toLocaleString()} m²)</small>
                      </dd>
                    </div>
                    <div>
                      <dt>Unit Metric Rule</dt>
                      <dd>
                        1 Acre = 4,046.8564 m² <small>Standard SI</small>
                      </dd>
                    </div>
                    <div>
                      <dt>Land Classification</dt>
                      <dd>{scenario.land_use}</dd>
                    </div>
                    <div>
                      <dt>Jurisdiction</dt>
                      <dd>
                        {scenario.village}, {scenario.taluk}, {scenario.district}
                      </dd>
                    </div>
                  </dl>

                  <div className="source-rank">
                    <span>Source Hierarchy & Provenance</span>
                    <div>
                      <b>1</b> Authoritative Extract <i>›</i> <b>2</b> Authoritative GIS <i>›</i> <b>3</b> AI Extraction{" "}
                      <i>›</i> <b>4</b> User Input
                    </div>
                  </div>
                </section>
              </div>

              {/* Extraction & Validation Matrix */}
              <section className="validation-panel" id="validation">
                <header className="section-header">
                  <div>
                    <span className="eyebrow">CONSISTENCY VALIDATION MATRIX</span>
                    <h2>Field-by-Field Evidence Comparison</h2>
                  </div>
                  <span className="synthetic-chip">
                    {connection === "live" ? "FastAPI Validation Engine" : "Local Demo Fallback"}
                  </span>
                </header>

                <div className="compare-table" role="table" aria-label="Field Comparison Matrix">
                  <div className="compare-row table-head" role="row">
                    <span>FIELD / ATTRIBUTE</span>
                    <span>
                      SUBMITTED DOCUMENT <small>(AI MOCK EXTRACTION)</small>
                    </span>
                    <span>
                      AUTHORITATIVE EXTRACT <small>(SYNTHETIC FIXTURE)</small>
                    </span>
                    <span>VALIDATION RESULT</span>
                  </div>

                  {currentValidationRows.map(row => {
                    const isRowMatch = row.result === "MATCH";
                    const isPartial = row.result === "PARTIAL_MATCH";
                    const isAlert = !isRowMatch && !isPartial;

                    return (
                      <div className={`compare-row ${isAlert ? "alert" : ""}`} role="row" key={row.field}>
                        <div>
                          <b>{row.field.toUpperCase().replace("_", " ")}</b>
                          <i>{row.explanation}</i>
                        </div>
                        <span>
                          {row.value_a}{" "}
                          <i>Extraction Conf: {Math.round(row.confidence * 100)}% (mock-document-ai)</i>
                        </span>
                        <span>
                          {row.value_b}
                          <i>Source: Synthetic Authority Adapter</i>
                        </span>
                        <span className={`result ${isRowMatch ? "match" : isPartial ? "partial" : "mismatch"}`}>
                          {isRowMatch ? "✓ MATCH" : isPartial ? "~ PARTIAL" : "! REVIEW REQUIRED"}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </section>

              {/* Document Vault & Provenance */}
              <section className="document-panel" id="documents">
                <header className="section-header">
                  <div>
                    <span className="eyebrow">IMMUTABLE EVIDENCE VAULT</span>
                    <h2>Source Documents & SHA-256 Hashes</h2>
                  </div>
                  <div style={{ display: "flex", gap: "10px" }}>
                    <button className="upload-button" onClick={() => fileInput.current?.click()}>
                      <Icon name="upload" size={16} />
                      Upload New Deed / Sketch
                    </button>
                    <input
                      ref={fileInput}
                      className="sr-only"
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png,.txt"
                      onChange={onUpload}
                    />
                  </div>
                </header>

                <div className="document-list">
                  {docs.map((doc, index) => (
                    <article className="document-row" key={`${doc.id}-${index}`}>
                      <span className="doc-icon">
                        {doc.name.toLowerCase().endsWith("pdf") || doc.name.includes("Deed") ? "PDF" : "TXT"}
                      </span>
                      <div>
                        <h3>
                          {doc.name} <em>{doc.tag}</em>
                        </h3>
                        <p>{doc.meta}</p>
                        {doc.sha256 && (
                          <p style={{ color: "#0e7490" }}>
                            SHA-256: <code>{doc.sha256}</code>
                          </p>
                        )}
                      </div>
                      <span className={`status ${doc.state === "Verified" ? "good" : "uploaded"}`}>
                        ● {doc.state}
                      </span>
                      <button
                        className="plain-button"
                        onClick={triggerBlueprintAnalysis}
                        title="Analyze dimensions with Computer Vision"
                      >
                        <Icon name="compass" size={16} />
                      </button>
                    </article>
                  ))}
                </div>
              </section>
            </>
          )}

          {/* TAB 2: OFFICER REVIEW QUEUE */}
          {activeTab === "queue" && (
            <section className="review-panel" id="review">
              <div className="review-main">
                <span className="eyebrow">DISCREPANCY RESOLUTION WORKFLOW</span>
                <h2>Officer Review & Decision Console</h2>
                <p>
                  As an authorized Revenue Officer, inspect the discrepancy queue. Recorded decisions are immutable,
                  trigger an append-only audit event, and update the Digital Land Profile.
                </p>

                {/* Queue Selection Table */}
                <table className="queue-table">
                  <thead>
                    <tr>
                      <th>Case ID</th>
                      <th>Priority</th>
                      <th>Discrepancy Reason</th>
                      <th>Claimed vs Authoritative</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reviewCases.map(c => (
                      <tr
                        key={c.id}
                        className={selectedCaseId === c.id ? "selected" : ""}
                        onClick={() => setSelectedCaseId(c.id)}
                        style={{ cursor: "pointer" }}
                      >
                        <td>
                          <b>{c.id}</b>
                        </td>
                        <td>
                          <span className="badge-advisory">{c.priority}</span>
                        </td>
                        <td>{c.reason}</td>
                        <td>
                          {c.claimed_value} vs {c.authoritative_value}
                        </td>
                        <td>
                          <span className={`status ${c.status === "RESOLVED" ? "good" : "warn"}`}>
                            ● {c.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Decision Controls */}
                <div className="review-controls" style={{ marginTop: "20px" }}>
                  <label>
                    <span>SELECT RESOLUTION ACTION</span>
                    <select
                      value={resolutionChoice}
                      onChange={e => setResolutionChoice(e.target.value as any)}
                      style={{
                        padding: "8px 12px",
                        border: "1px solid #cbd5e1",
                        borderRadius: "4px",
                        fontSize: "12px",
                        marginBottom: "12px",
                        width: "100%"
                      }}
                    >
                      <option value="REQUIRES_DOCUMENT">
                        REQUIRES_DOCUMENT — Request original physical deed / survey sketch
                      </option>
                      <option value="ACCEPTED_FOR_CORRECTION">
                        ACCEPTED_FOR_CORRECTION — Accept variance for official revenue mutation
                      </option>
                      <option value="NO_ACTION">NO_ACTION — Reject variance; uphold authoritative record</option>
                    </select>
                  </label>

                  <label>
                    <span>OFFICER FINDINGS & RATIONALE (MANDATORY AUDIT NOTE)</span>
                    <textarea
                      placeholder="Enter legal/revenue rationale for this decision..."
                      value={officerNote}
                      onChange={e => setOfficerNote(e.target.value)}
                    />
                  </label>

                  <div className="action-buttons">
                    <button
                      className={reviewSent ? "sent-button" : "send-button"}
                      onClick={handleRecordDecision}
                    >
                      {reviewSent ? (
                        <>
                          <Icon name="check" size={17} /> Decision Recorded & Logged
                        </>
                      ) : (
                        <>
                          <Icon name="shield" size={17} /> Record Official Decision
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Audit Timeline */}
              <aside className="audit">
                <span className="eyebrow">IMMUTABLE AUDIT TRAIL</span>
                <ol>
                  <li>
                    <i className="done" />
                    <div>
                      <b>Original Document Hashed (SHA-256)</b>
                      <small>Stored in evidence vault · demo-citizen</small>
                    </div>
                  </li>
                  <li>
                    <i className="done" />
                    <div>
                      <b>Consistency Check Completed</b>
                      <small>MockDocumentProvider v1.2 · {Math.round(scenario.confidence * 100)}% confidence</small>
                    </div>
                  </li>
                  <li>
                    <i className={isConsistent ? "done" : "warn"} />
                    <div>
                      <b>{isConsistent ? "All Primary Attributes Matched" : "Discrepancy Flagged for Review"}</b>
                      <small>{scenario.reason}</small>
                    </div>
                  </li>
                  <li>
                    <i className={reviewSent ? "done" : "pending"} />
                    <div>
                      <b>
                        {reviewSent
                          ? `Decision Recorded: ${resolutionChoice}`
                          : isConsistent
                          ? "Automatic Clearance (Consistent)"
                          : "Officer Review Pending"}
                      </b>
                      <small>{reviewSent ? "demo-officer · Just now" : "Awaiting officer sign-off"}</small>
                    </div>
                  </li>
                </ol>
              </aside>
            </section>
          )}

          {/* TAB 3: MUTATION & LAND HISTORY */}
          {activeTab === "history" && (
            <section className="history-panel">
              <header className="section-header">
                <div>
                  <span className="eyebrow">CHAIN OF PROVENANCE</span>
                  <h2>Historical Mutations & Registered Transactions</h2>
                </div>
                <span className="badge-synthetic">SYNTHETIC CHRONOLOGY</span>
              </header>

              <div className="mutation-timeline">
                {mutationHistory.map(mut => (
                  <article className="mutation-item" key={mut.id}>
                    <div className="mut-meta">
                      <strong>{mut.mutation_number}</strong>
                      <span>{mut.recorded_date}</span>
                      <div style={{ marginTop: "4px" }}>
                        <span className="badge-verified">{mut.event_type}</span>
                      </div>
                    </div>
                    <div className="mut-content">
                      <h4>{mut.parties_involved}</h4>
                      <p>{mut.description}</p>
                      <small>Order Ref: {mut.order_reference}</small>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          )}

          {/* TAB 4: SYSTEM ADMIN HEALTH */}
          {activeTab === "admin" && (
            <section className="admin-panel">
              <header className="section-header">
                <div>
                  <span className="eyebrow">ADMINISTRATIVE DASHBOARD</span>
                  <h2>Platform Adapters & Infrastructure Health</h2>
                </div>
                <span className="badge-verified">ALL SYSTEMS HEALTHY</span>
              </header>

              <div style={{ padding: "20px" }}>
                <dl className="details">
                  <div>
                    <dt>State Authority Adapter</dt>
                    <dd>
                      DemoAuthorityAdapter <span className="verified">● HEALTHY (14 Synthetic Parcels Loaded)</span>
                    </dd>
                  </div>
                  <div>
                    <dt>Document AI Provider</dt>
                    <dd>
                      mock-document-ai v1.2 <small>(Deterministic Mock OCR/NER)</small>
                    </dd>
                  </div>
                  <div>
                    <dt>Blueprint CV Provider</dt>
                    <dd>
                      mock-blueprint-cv v0.3 <small>(Advisory Edge & Dimension Detection)</small>
                    </dd>
                  </div>
                  <div>
                    <dt>Evidence Storage Target</dt>
                    <dd>LocalEvidenceStore (.landsync-storage) · SHA-256 Content Addressed</dd>
                  </div>
                  <div>
                    <dt>Database / GIS Engine</dt>
                    <dd>PostgreSQL + PostGIS (Migration 001_initial.sql)</dd>
                  </div>
                </dl>
              </div>
            </section>
          )}

          {/* Footer */}
          <footer className="page-footer">
            <div>LANDSYNC AI · SIH26018 · TEAM VOID</div>
            <span>
              All records and model extractions are synthetic. No live government database is contacted.
            </span>
          </footer>
        </div>
      </section>

      {/* Advisory Consistency Report Modal */}
      {showReportModal && (
        <div className="modal-overlay" onClick={() => setShowReportModal(false)}>
          <div className="report-modal" onClick={e => e.stopPropagation()}>
            <div className="report-header">
              <div>
                <h2>LANDSYNC AI CONSISTENCY REPORT</h2>
                <p>Digital Land Profile Advisory Verification Document</p>
              </div>
              <button
                className="plain-button"
                style={{ color: "#fff", fontSize: "20px" }}
                onClick={() => setShowReportModal(false)}
              >
                ✕
              </button>
            </div>

            <div className="report-body">
              <div className="badge-synthetic" style={{ width: "100%", justifyContent: "center", padding: "8px", marginBottom: "16px" }}>
                SYNTHETIC DEMO REPORT · ADVISORY ONLY · NOT A LEGAL TITLE CERTIFICATE
              </div>

              <div className="report-card">
                <h3>Executive Evaluation Summary</h3>
                <dl className="details" style={{ padding: 0 }}>
                  <div><dt>Parcel / ULPIN</dt><dd>{scenario.survey_number} (Plot {scenario.plot_number}) <small>{scenario.ulpin}</small></dd></div>
                  <div><dt>Location</dt><dd>{scenario.village}, {scenario.district} ({scenario.state})</dd></div>
                  <div><dt>Extent Evaluated</dt><dd>{scenario.area} ({scenario.normalized_area_sqm.toLocaleString()} m²) <small>vs {scenario.doc_area}</small></dd></div>
                  <div><dt>Consistency Verdict</dt><dd><span className={isConsistent ? "match" : "mismatch"}>{isConsistent ? "CONSISTENT" : "REVIEW_REQUIRED"}</span></dd></div>
                  <div><dt>Key Finding</dt><dd>{scenario.reason}</dd></div>
                  <div><dt>Evidence Hash</dt><dd><code style={{ fontSize: "11px" }}>SHA-256: f8c238346ffe3a51d5124e09056fe5b310b36e44d667566952b7b5e3a66dfb8b</code></dd></div>
                  <div><dt>Officer Decision</dt><dd>{resolutionChoice} <small>— {officerNote}</small></dd></div>
                </dl>
              </div>

              <button
                className="upload-button"
                style={{ width: "100%", justifyContent: "center", marginTop: "12px" }}
                onClick={() => window.print()}
              >
                <Icon name="printer" size={16} /> Print Advisory Land Profile Report
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
