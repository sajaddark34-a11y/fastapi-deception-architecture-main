"""
Vector SVG Diagrams for the FastAPI Deception Architecture Documentation.
Rendered cleanly and sharply across all PDF pages.
"""

SVG_4LAYER_ARCHITECTURE = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 500" width="100%" height="auto" style="max-height: 380px;">
  <defs>
    <linearGradient id="layer1Grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="layer2Grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0369a1"/>
      <stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>
    <linearGradient id="layer3Grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#b91c1c"/>
      <stop offset="100%" stop-color="#dc2626"/>
    </linearGradient>
    <linearGradient id="layer4Grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#047857"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#000000" flood-opacity="0.15"/>
    </filter>
  </defs>

  <!-- Incoming Traffic Node -->
  <g transform="translate(300, 15)">
    <rect width="300" height="40" rx="8" fill="#334155" filter="url(#shadow)"/>
    <text x="150" y="25" fill="#f8fafc" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="bold" text-anchor="middle">
      🌐 Incoming HTTP / TCP Traffic (Clients & Scanners)
    </text>
  </g>

  <!-- Arrow down to Layer 1 -->
  <line x1="450" y1="55" x2="450" y2="85" stroke="#0284c7" stroke-width="3" marker-end="url(#arrow)"/>
  <polygon points="445,80 450,90 455,80" fill="#0284c7"/>

  <!-- Layer 1: Ingress Gateway -->
  <g transform="translate(50, 90)">
    <rect width="800" height="90" rx="10" fill="url(#layer1Grad)" stroke="#38bdf8" stroke-width="2" filter="url(#shadow)"/>
    <text x="25" y="30" fill="#38bdf8" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold">
      LAYER 1: INGRESS GATEWAY & TRAFFIC CLASSIFIER (Port 8000) — علي (Ali)
    </text>
    <text x="25" y="52" fill="#cbd5e1" font-family="'Segoe UI', sans-serif" font-size="11">
      • traffic_classifier.py  • redis_cache_verifier.py  • attack_detector.py  • TCPL4DeceptionProtocol
    </text>
    <text x="25" y="72" fill="#94a3b8" font-family="'Segoe UI', sans-serif" font-size="10.5">
      Sub-millisecond session state evaluation via Redis • Threat signature & Honey-Token deep inspection
    </text>
  </g>

  <!-- Splitting Arrows -->
  <!-- Left Legitimate Arrow -->
  <path d="M 250 180 L 250 220" stroke="#0284c7" stroke-width="3" fill="none"/>
  <polygon points="245,215 250,225 255,215" fill="#0284c7"/>
  <rect x="140" y="190" width="160" height="22" rx="4" fill="#e0f2fe"/>
  <text x="220" y="205" fill="#0369a1" font-family="'Segoe UI', sans-serif" font-size="9.5" font-weight="bold" text-anchor="middle">
    Legitimate Traffic (Clean)
  </text>

  <!-- Right Malicious Arrow -->
  <path d="M 650 180 L 650 220" stroke="#dc2626" stroke-width="3" fill="none"/>
  <polygon points="645,215 650,225 655,215" fill="#dc2626"/>
  <rect x="560" y="190" width="180" height="22" rx="4" fill="#fee2e2"/>
  <text x="650" y="205" fill="#b91c1c" font-family="'Segoe UI', sans-serif" font-size="9.5" font-weight="bold" text-anchor="middle">
    Trapped Session (Adversary)
  </text>

  <!-- Layer 2: Core Web App & Honey Token Injector (Left Box) -->
  <g transform="translate(50, 225)">
    <rect width="380" height="135" rx="10" fill="url(#layer2Grad)" stroke="#7dd3fc" stroke-width="1.5" filter="url(#shadow)"/>
    <text x="20" y="28" fill="#ffffff" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="bold">
      LAYER 2: CORE WEB APP & INJECTOR
    </text>
    <text x="20" y="48" fill="#e0f2fe" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold">
      يوسف (App & Auth) & عمار (Honey Injector)
    </text>
    <text x="20" y="70" fill="#f0f9ff" font-family="'Segoe UI', sans-serif" font-size="10">
      • core_web_app (Auth PBKDF2/JWT, Records)
    </text>
    <text x="20" y="88" fill="#f0f9ff" font-family="'Segoe UI', sans-serif" font-size="10">
      • honey_token_injector (Fake Headers, URLs)
    </text>
    <text x="20" y="108" fill="#e0f2fe" font-family="'Segoe UI', sans-serif" font-size="9.5">
      Injects HMAC-SHA256 decoy lures into legitimate JSON
    </text>
    <rect x="20" y="115" width="340" height="14" rx="3" fill="rgba(0,0,0,0.2)"/>
    <text x="25" y="125" fill="#bae6fd" font-family="'Segoe UI', sans-serif" font-size="8.5">
      Network: ingress_gateway_net (172.28.0.0/24)
    </text>
  </g>

  <!-- Layer 3: Containment Sandbox & DFIR Engine (Right Box) -->
  <g transform="translate(470, 225)">
    <rect width="380" height="135" rx="10" fill="url(#layer3Grad)" stroke="#fca5a5" stroke-width="1.5" filter="url(#shadow)"/>
    <text x="20" y="28" fill="#ffffff" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="bold">
      LAYER 3: SANDBOX & DFIR ENGINE
    </text>
    <text x="20" y="48" fill="#fee2e2" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold">
      عمار (Containment, Forensics, Chain of Custody)
    </text>
    <text x="20" y="70" fill="#fff1f2" font-family="'Segoe UI', sans-serif" font-size="10">
      • isolation_sandbox (Prewarmed Zero-Latency Pool)
    </text>
    <text x="20" y="88" fill="#fff1f2" font-family="'Segoe UI', sans-serif" font-size="10">
      • forensic_extraction_engine (Commands, PCAP, eBPF)
    </text>
    <text x="20" y="108" fill="#fee2e2" font-family="'Segoe UI', sans-serif" font-size="9.5">
      Tamper-Evident HMAC-SHA256 Hash Chain verification
    </text>
    <rect x="20" y="115" width="340" height="14" rx="3" fill="rgba(0,0,0,0.2)"/>
    <text x="25" y="125" fill="#fecaca" font-family="'Segoe UI', sans-serif" font-size="8.5">
      Network: sandbox_containment_net (internal: true, 172.29.0.0/24)
    </text>
  </g>

  <!-- Arrows merging into Layer 4 -->
  <path d="M 240 360 L 240 385 L 450 385 L 450 400" stroke="#047857" stroke-width="2.5" fill="none"/>
  <path d="M 660 360 L 660 385 L 450 385" stroke="#047857" stroke-width="2.5" fill="none"/>
  <polygon points="445,395 450,405 455,395" fill="#047857"/>

  <!-- Layer 4: Storage Backbone & SOC Dashboard -->
  <g transform="translate(50, 405)">
    <rect width="800" height="85" rx="10" fill="url(#layer4Grad)" stroke="#6ee7b7" stroke-width="1.5" filter="url(#shadow)"/>
    <text x="25" y="28" fill="#ffffff" font-family="'Segoe UI', sans-serif" font-size="13.5" font-weight="bold">
      LAYER 4: DATA STORAGE BACKBONE & DEFENDER SOC (Port 8500)
    </text>
    <text x="25" y="48" fill="#d1fae5" font-family="'Segoe UI', sans-serif" font-size="10.5">
      يوسف: Redis Store (Sessions & Alert Streams) + PostgreSQL Store (Immutable Logs & SHA-256 Artifacts)
    </text>
    <text x="25" y="68" fill="#d1fae5" font-family="'Segoe UI', sans-serif" font-size="10.5">
      عمار: soc_dashboard (Live WS/SSE Telemetry, MITRE Heatmap, Terminal Replay, SOAR Containment Controls)
    </text>
  </g>
</svg>
"""

SVG_CHAIN_OF_CUSTODY = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 180" width="100%" height="auto" style="max-height: 180px;">
  <defs>
    <filter id="chainShadow">
      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000" flood-opacity="0.1"/>
    </filter>
  </defs>

  <!-- Genesis Block -->
  <g transform="translate(10, 25)">
    <rect width="160" height="130" rx="8" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5" filter="url(#chainShadow)"/>
    <text x="80" y="30" fill="#38bdf8" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">GENESIS BLOCK</text>
    <text x="80" y="52" fill="#94a3b8" font-family="'Consolas', monospace" font-size="8.5" text-anchor="middle">Seq: #0</text>
    <text x="80" y="75" fill="#f8fafc" font-family="'Consolas', monospace" font-size="8" text-anchor="middle">PrevHash: 0*64</text>
    <rect x="15" y="90" width="130" height="24" rx="4" fill="#1e293b"/>
    <text x="80" y="106" fill="#4ade80" font-family="'Consolas', monospace" font-size="8" text-anchor="middle">Chain Root Seed</text>
  </g>

  <!-- Link 1 -->
  <line x1="170" y1="90" x2="220" y2="90" stroke="#0ea5e9" stroke-width="3" stroke-dasharray="4"/>
  <polygon points="215,85 225,90 215,95" fill="#0ea5e9"/>

  <!-- Block 1: PCAP Chunk -->
  <g transform="translate(225, 25)">
    <rect width="180" height="130" rx="8" fill="#1e293b" stroke="#0ea5e9" stroke-width="1.5" filter="url(#chainShadow)"/>
    <text x="90" y="28" fill="#38bdf8" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">ARTIFACT #1 (PCAP)</text>
    <text x="90" y="48" fill="#94a3b8" font-family="'Consolas', monospace" font-size="8.5" text-anchor="middle">session_01_capture.pcap</text>
    <text x="90" y="70" fill="#cbd5e1" font-family="'Consolas', monospace" font-size="7.5" text-anchor="middle">SHA256: 7a8b9c...e1f2</text>
    <rect x="15" y="85" width="150" height="30" rx="4" fill="#0f172a"/>
    <text x="90" y="98" fill="#facc15" font-family="'Consolas', monospace" font-size="7.5" text-anchor="middle">HMAC-SHA256 Signed</text>
    <text x="90" y="110" fill="#38bdf8" font-family="'Consolas', monospace" font-size="7.5" text-anchor="middle">Legal Admissibility OK</text>
  </g>

  <!-- Link 2 -->
  <line x1="405" y1="90" x2="455" y2="90" stroke="#0ea5e9" stroke-width="3" stroke-dasharray="4"/>
  <polygon points="450,85 460,90 450,95" fill="#0ea5e9"/>

  <!-- Block 2: Shell Command -->
  <g transform="translate(460, 25)">
    <rect width="180" height="130" rx="8" fill="#1e293b" stroke="#0ea5e9" stroke-width="1.5" filter="url(#chainShadow)"/>
    <text x="90" y="28" fill="#38bdf8" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">ARTIFACT #2 (CMD)</text>
    <text x="90" y="48" fill="#94a3b8" font-family="'Consolas', monospace" font-size="8.5" text-anchor="middle">commands.jsonl (whoami)</text>
    <text x="90" y="70" fill="#cbd5e1" font-family="'Consolas', monospace" font-size="7.5" text-anchor="middle">SHA256: 3d4e5f...90ab</text>
    <rect x="15" y="85" width="150" height="30" rx="4" fill="#0f172a"/>
    <text x="90" y="98" fill="#facc15" font-family="'Consolas', monospace" font-size="7.5" text-anchor="middle">MITRE: T1033 Matched</text>
    <text x="90" y="110" fill="#38bdf8" font-family="'Consolas', monospace" font-size="7.5" text-anchor="middle">Chain Hash Verified</text>
  </g>

  <!-- Link 3 -->
  <line x1="640" y1="90" x2="690" y2="90" stroke="#0ea5e9" stroke-width="3" stroke-dasharray="4"/>
  <polygon points="685,85 695,90 685,95" fill="#0ea5e9"/>

  <!-- Block 3: eBPF Trace -->
  <g transform="translate(695, 25)">
    <rect width="145" height="130" rx="8" fill="#1e293b" stroke="#0ea5e9" stroke-width="1.5" filter="url(#chainShadow)"/>
    <text x="72" y="28" fill="#38bdf8" font-family="'Segoe UI', sans-serif" font-size="10.5" font-weight="bold" text-anchor="middle">ARTIFACT #3 (eBPF)</text>
    <text x="72" y="48" fill="#94a3b8" font-family="'Consolas', monospace" font-size="8" text-anchor="middle">ebpf_trace.log</text>
    <text x="72" y="70" fill="#cbd5e1" font-family="'Consolas', monospace" font-size="7" text-anchor="middle">sys_enter_execve</text>
    <rect x="10" y="85" width="125" height="30" rx="4" fill="#0f172a"/>
    <text x="72" y="104" fill="#4ade80" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" text-anchor="middle">SEALED BUNDLE</text>
  </g>
</svg>
"""

SVG_TRAFFIC_FLOW_PATHS = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 320" width="100%" height="auto" style="max-height: 260px;">
  <defs>
    <filter id="flowShadow">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.12"/>
    </filter>
  </defs>

  <!-- Title Banner -->
  <rect x="10" y="10" width="880" height="30" rx="5" fill="#0f172a"/>
  <text x="450" y="30" fill="#38bdf8" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="bold" text-anchor="middle">
    THREE CONCURRENT EXECUTION PATHS (مسارات المعالجة والتصنيف الثلاثية المتزامنة)
  </text>

  <!-- Path A: Green Legitimate -->
  <g transform="translate(10, 55)">
    <rect width="280" height="250" rx="8" fill="#f0fdf4" stroke="#22c55e" stroke-width="2" filter="url(#flowShadow)"/>
    <rect x="10" y="10" width="260" height="28" rx="4" fill="#15803d"/>
    <text x="140" y="29" fill="#ffffff" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">
      PATH A: الشرعي (LEGITIMATE)
    </text>
    <text x="15" y="60" fill="#166534" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">1. Ingress Classification:</text>
    <text x="25" y="78" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Clean JWT / PBKDF2 Session</text>
    <text x="25" y="94" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Cache Hit &lt; 0.8ms</text>
    <text x="15" y="120" fill="#166534" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">2. Direct Forwarding:</text>
    <text x="25" y="138" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Core Web App (Port 8001)</text>
    <text x="25" y="154" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• True Business Logic Executed</text>
    <text x="15" y="180" fill="#166534" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">3. Transparent Egress:</text>
    <text x="25" y="198" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Decoy Canary injected in JSON</text>
    <text x="25" y="214" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Client receives valid response</text>
    <rect x="20" y="226" width="240" height="16" rx="3" fill="#bbf7d0"/>
    <text x="140" y="238" fill="#14532d" font-family="'Consolas', monospace" font-size="8.5" font-weight="bold" text-anchor="middle">Latency: 2.4ms | ZERO IMPACT</text>
  </g>

  <!-- Path B: Orange Heuristic Suspicious -->
  <g transform="translate(310, 55)">
    <rect width="280" height="250" rx="8" fill="#fffbeb" stroke="#f59e0b" stroke-width="2" filter="url(#flowShadow)"/>
    <rect x="10" y="10" width="260" height="28" rx="4" fill="#b45309"/>
    <text x="140" y="29" fill="#ffffff" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">
      PATH B: المشبوه (SUSPICIOUS)
    </text>
    <text x="15" y="60" fill="#92400e" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">1. Ingress Heuristics:</text>
    <text x="25" y="78" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Attack Signature detected</text>
    <text x="25" y="94" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Score exceeds threshold (&gt;70)</text>
    <text x="15" y="120" fill="#92400e" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">2. Sub-Millisecond Isolation:</text>
    <text x="25" y="138" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Prewarmed Container assigned</text>
    <text x="25" y="154" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Handshake switched in &lt;10ms</text>
    <text x="15" y="180" fill="#92400e" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">3. Active Containment:</text>
    <text x="25" y="198" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Fake Database records returned</text>
    <text x="25" y="214" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• HTTP 200 (Attacker unaware)</text>
    <rect x="20" y="226" width="240" height="16" rx="3" fill="#fde68a"/>
    <text x="140" y="238" fill="#78350f" font-family="'Consolas', monospace" font-size="8.5" font-weight="bold" text-anchor="middle">Switch Time: 7.2ms | ISOLATED</text>
  </g>

  <!-- Path C: Red Honeypot Tripwire -->
  <g transform="translate(610, 55)">
    <rect width="280" height="250" rx="8" fill="#fef2f2" stroke="#ef4444" stroke-width="2" filter="url(#flowShadow)"/>
    <rect x="10" y="10" width="260" height="28" rx="4" fill="#b91c1c"/>
    <text x="140" y="29" fill="#ffffff" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">
      PATH C: الفخ الفوري (HONEY TRAP)
    </text>
    <text x="15" y="60" fill="#991b1b" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">1. Tripwire Triggered:</text>
    <text x="25" y="78" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Canary token invoked (/search_trap)</text>
    <text x="25" y="94" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Zero False Alarm (100% confidence)</text>
    <text x="15" y="120" fill="#991b1b" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">2. Instant Fast Alert:</text>
    <text x="25" y="138" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Async queue broadcast to SOC</text>
    <text x="25" y="154" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• IP blacklisted / quarantined</text>
    <text x="15" y="180" fill="#991b1b" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">3. Tamper-Proof Evidence:</text>
    <text x="25" y="198" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• SHA-256 Chain of Custody sealed</text>
    <text x="25" y="214" fill="#334155" font-family="'Segoe UI', sans-serif" font-size="9.5">• Admissible legal forensic package</text>
    <rect x="20" y="226" width="240" height="16" rx="3" fill="#fecaca"/>
    <text x="140" y="238" fill="#7f1d1d" font-family="'Consolas', monospace" font-size="8.5" font-weight="bold" text-anchor="middle">Trip Latency: &lt;1.0ms | FORENSIC READY</text>
  </g>
</svg>
"""

SVG_PREWARMED_POOL = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 200" width="100%" height="auto" style="max-height: 190px;">
  <defs>
    <filter id="poolShadow">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.12"/>
    </filter>
  </defs>

  <!-- Step 1: Pre-Spawned Ready Pool -->
  <g transform="translate(15, 20)">
    <rect width="180" height="155" rx="8" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5" filter="url(#poolShadow)"/>
    <text x="90" y="28" fill="#38bdf8" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">1. WARM POOL</text>
    <text x="90" y="48" fill="#94a3b8" font-family="'Consolas', monospace" font-size="8.5" text-anchor="middle">Prewarmed Instances</text>
    <rect x="15" y="60" width="150" height="22" rx="4" fill="#1e293b"/>
    <text x="90" y="75" fill="#4ade80" font-family="'Consolas', monospace" font-size="8" text-anchor="middle">● Box-01: READY</text>
    <rect x="15" y="88" width="150" height="22" rx="4" fill="#1e293b"/>
    <text x="90" y="103" fill="#4ade80" font-family="'Consolas', monospace" font-size="8" text-anchor="middle">● Box-02: READY</text>
    <rect x="15" y="116" width="150" height="22" rx="4" fill="#1e293b"/>
    <text x="90" y="131" fill="#4ade80" font-family="'Consolas', monospace" font-size="8" text-anchor="middle">● Box-03: READY</text>
  </g>

  <!-- Arrow 1 -->
  <line x1="205" y1="95" x2="245" y2="95" stroke="#38bdf8" stroke-width="3"/>
  <polygon points="240,90 250,95 240,100" fill="#38bdf8"/>
  <text x="225" y="85" fill="#0284c7" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" text-anchor="middle">&lt;10ms</text>

  <!-- Step 2: Instant Allocation -->
  <g transform="translate(255, 20)">
    <rect width="180" height="155" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5" filter="url(#poolShadow)"/>
    <text x="90" y="28" fill="#f59e0b" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">2. ALLOCATION</text>
    <text x="90" y="48" fill="#94a3b8" font-family="'Consolas', monospace" font-size="8.5" text-anchor="middle">Sub-ms Session Lock</text>
    <rect x="15" y="62" width="150" height="35" rx="4" fill="#0f172a"/>
    <text x="90" y="78" fill="#facc15" font-family="'Consolas', monospace" font-size="8" text-anchor="middle">Box-01 Assigned</text>
    <text x="90" y="90" fill="#cbd5e1" font-family="'Consolas', monospace" font-size="7.5" text-anchor="middle">Session: #atk-9812</text>
    <rect x="15" y="108" width="150" height="35" rx="4" fill="#0f172a"/>
    <text x="90" y="124" fill="#38bdf8" font-family="'Consolas', monospace" font-size="8" text-anchor="middle">Async Replenish Trigger</text>
    <text x="90" y="136" fill="#94a3b8" font-family="'Consolas', monospace" font-size="7.5" text-anchor="middle">Spawns new Box-04</text>
  </g>

  <!-- Arrow 2 -->
  <line x1="445" y1="95" x2="485" y2="95" stroke="#f59e0b" stroke-width="3"/>
  <polygon points="480,90 490,95 480,100" fill="#f59e0b"/>

  <!-- Step 3: Adversary Containment -->
  <g transform="translate(495, 20)">
    <rect width="180" height="155" rx="8" fill="#1e293b" stroke="#ef4444" stroke-width="1.5" filter="url(#poolShadow)"/>
    <text x="90" y="28" fill="#ef4444" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">3. DECEPTION RUN</text>
    <text x="90" y="48" fill="#94a3b8" font-family="'Consolas', monospace" font-size="8.5" text-anchor="middle">Synthetic Env Active</text>
    <text x="25" y="75" fill="#fca5a5" font-family="'Segoe UI', sans-serif" font-size="9">• Fake DB Schema</text>
    <text x="25" y="93" fill="#fca5a5" font-family="'Segoe UI', sans-serif" font-size="9">• Injected Breadcrumbs</text>
    <text x="25" y="111" fill="#fca5a5" font-family="'Segoe UI', sans-serif" font-size="9">• eBPF Syscall Monitor</text>
    <text x="25" y="129" fill="#fca5a5" font-family="'Segoe UI', sans-serif" font-size="9">• Real Core UNTOUCHED</text>
    <rect x="15" y="137" width="150" height="18" rx="3" fill="#450a0a"/>
    <text x="90" y="150" fill="#f87171" font-family="'Consolas', monospace" font-size="7.5" font-weight="bold" text-anchor="middle">ZERO Real Data Access</text>
  </g>

  <!-- Arrow 3 -->
  <line x1="685" y1="95" x2="725" y2="95" stroke="#ef4444" stroke-width="3"/>
  <polygon points="720,90 730,95 720,100" fill="#ef4444"/>

  <!-- Step 4: Snapshot & Evidence Vault -->
  <g transform="translate(735, 20)">
    <rect width="135" height="155" rx="8" fill="#0f172a" stroke="#22c55e" stroke-width="1.5" filter="url(#poolShadow)"/>
    <text x="67" y="28" fill="#22c55e" font-family="'Segoe UI', sans-serif" font-size="10.5" font-weight="bold" text-anchor="middle">4. SEAL & RECYCLE</text>
    <text x="67" y="48" fill="#94a3b8" font-family="'Consolas', monospace" font-size="8" text-anchor="middle">DFIR Extraction</text>
    <rect x="10" y="62" width="115" height="26" rx="4" fill="#1e293b"/>
    <text x="67" y="78" fill="#cbd5e1" font-family="'Consolas', monospace" font-size="7.5" text-anchor="middle">Memory Dump</text>
    <rect x="10" y="94" width="115" height="26" rx="4" fill="#1e293b"/>
    <text x="67" y="110" fill="#cbd5e1" font-family="'Consolas', monospace" font-size="7.5" text-anchor="middle">PCAP Extraction</text>
    <rect x="10" y="126" width="115" height="24" rx="4" fill="#14532d"/>
    <text x="67" y="142" fill="#86efac" font-family="'Consolas', monospace" font-size="7.5" font-weight="bold" text-anchor="middle">Chain Sealed</text>
  </g>
</svg>
"""
