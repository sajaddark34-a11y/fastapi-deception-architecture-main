# FastAPI-Driven Deception Architecture for Threat Detection and Forensics Extraction
# معمارية الخداع السيبراني المبنية على FastAPI لكشف التهديدات واستخراج الأدلة الجنائية

---

## 1. Executive Overview | نظرة عامة تنفيذية

### English
**FastAPI-Driven Deception Architecture for Threat Detection and Forensics Extraction** is an enterprise-grade active cyber-defense and threat-deception platform built with **FastAPI**, **Pydantic v2**, **Redis**, **PostgreSQL**, and **Docker**. Instead of merely blocking suspicious requests at the perimeter, the platform embeds cryptographic decoy lures (**Honey Tokens**) into responses from the legitimate application. When an adversary or automated scanner interacts with a decoy header, hidden URL, fake API key, or session cookie, the **Deception Gateway** transparently diverts the attacker's session into a **Prewarmed Dynamic Sandbox** (isolated honey containers on an air-gapped internal network). While the adversary believes they are exploiting the production environment, the **Forensic Extraction Engine** captures every shell command, system call (`eBPF`), and network packet (`PCAP`), verifying artifacts with `SHA-256` checksums and streaming live alerts to the **Defender SOC Dashboard**.

### العربية
مشروع **معمارية الخداع السيبراني المبنية على FastAPI لكشف التهديدات واستخراج الأدلة الجنائية** هو نظام دفاع سيبراني نشط (Active Cyber Defense) يعتمد على تقنيات الخداع والعزل اللحظي. بدلاً من الاكتفاء بحظر الطلبات المشبوهة تقليدياً، يقوم النظام بحقن شراك خداعية (**Honey Tokens**) داخل استجابات التطبيق الحقيقي. عند قيام المهاجم أو أداة الفحص الآلي باستخدام أي شرك (مثل ترويسة HTTP مزيفة، رابط مخفي، أو مفتاح API وهمي)، تقوم **بوابة الخداع (`deception_gateway`)** بتحويل مسار جلسة المهاجم بشفافية تامة ودون انقطاع إلى **بيئة عزل ديناميكية مُحمّاة مسبقاً (`isolation_sandbox`)** معزولة كلياً عن الإنترنت وعن قواعد بيانات الإنتاج. وأثناء تفاعل المهاجم مع الحاوية الخادعة، يقوم **محرك استخراج الأدلة الجنائية (`forensic_extraction_engine`)** بالتقاط كافة الأوامر المنفذة وحزم الشبكة (`PCAP`) ونداءات النواة (`eBPF`) وتوثيقها جنائياً ببصمة `SHA-256` مع بث التنبيهات الفورية إلى **لوحة تحكم مركز العمليات الأمنية (`soc_dashboard`)**.

---

## 2. Four-Layer System Architecture | المعمارية الهندسية ذات الطبقات الأربع

```
                    [ Incoming HTTP/HTTPS Client Traffic ]
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: INGRESS GATEWAY & TRAFFIC CLASSIFICATION (deception_gateway)     │
│  • traffic_classifier.py  • redis_cache_verifier.py  • attack_detector.py │
│  • gateway_router.py      • malicious_session_router.py                   │
└──────────────────────┬─────────────────────────────────┬──────────────────┘
                       │ Legitimate Traffic              │ Trapped / Malicious Session
                       ▼ (ingress_gateway_net)           ▼ (sandbox_containment_net - internal: true)
┌─────────────────────────────────────────┐   ┌──────────────────────────────────────────┐
│ LAYER 2: CORE APP & HONEY INJECTOR      │   │ LAYER 3: SANDBOX & FORENSICS EXTRACTION  │
│  • core_web_app (Auth & Prod Routes)    │   │  • isolation_sandbox (Prewarmed Pool &   │
│  • honey_token_injector (Fake Headers,  │   │    Isolated Honey Containers)            │
│    Hidden URLs, Decoy Middleware)       │   │  • forensic_extraction_engine (Command   │
│                                         │   │    Logger, PCAP Sniffer, eBPF Handler)   │
└──────────────────────┬──────────────────┘   └────────────────────┬─────────────────────┘
                       │                                           │
                       └─────────────────────┬─────────────────────┘
                                             ▼ (soc_data_backbone_net)
┌───────────────────────────────────────────────────────────────────────────┐
│ LAYER 4: DATA STORAGE & DEFENDER SOC DASHBOARD                            │
│  • data_storage/redis_store (Session State & Fast Alerts Stream)          │
│  • data_storage/postgresql_store (Logs & Forensic Artifacts Repository)   │
│  • soc_dashboard (Live Attack Visualizations & Incident Report Generator) │
└───────────────────────────────────────────────────────────────────────────┘
```

### Detailed Layer Breakdown | تفصيل الطبقات المعمارية الأربع

1. **Layer 1 — Ingress Point & Traffic Classification (`deception_gateway`) | الطبقة الأولى — نقطة الدخول وتصنيف المرور:**
   - **EN:** Acts as the high-performance asynchronous reverse proxy. Verifies client sessions against `redis_store`, inspects incoming headers/URLs/payloads for triggered honey tokens or scanner signatures, emits real-time alerts, and routes benign sessions to `core_web_app` while transparently pinning malicious sessions to `isolation_sandbox`.
   - **AR:** تعمل كبوابة عبور عكسية غير متزامنة تفحص حالة الجلسة في Redis وتتحقق من الشراك المحقونة، وترسل التنبيهات الفورية، وتوجه المستخدمين الشرعيين للتطبيق الحقيقي بينما تعزل المهاجمين داخل حاويات الخداع.

2. **Layer 2 — Core Web App & Honey Token Injector (`core_web_app`, `honey_token_injector`) | الطبقة الثانية — التطبيق الحقيقي ومحقن الشراك:**
   - **EN:** Serves legitimate application routes and authentication (`core_web_app`) while the `honey_token_injector` middleware dynamically embeds decoy HTTP headers (`FAKE_HTTP_HEADER`), hidden HTML/API links (`HIDDEN_DECOY_URL`), fake API keys (`FAKE_API_KEY`), and decoy cookies (`DECOY_SESSION_COOKIE`) into outgoing responses.
   - **AR:** تشغل خدمات الويب الحقيقية والمصادقة، مع طبقة وسيطة (`injector_middleware`) تقوم بتوليد وحقن الشراك الخداعية برمجياً داخل الترويسات وحقول JSON وتعليقات HTML لكشف أي محاولة استغلال.

3. **Layer 3 — Containment Sandbox & Forensic Extraction (`isolation_sandbox`, `forensic_extraction_engine`) | الطبقة الثالثة — العزل والتحقيق الجنائي:**
   - **EN:** Maintains a pool of prewarmed decoy containers (`prewarmed_dynamic_sandbox`) bound to trapped sessions over the air-gapped `sandbox_containment_net` (`internal: true`). Simultaneously, `forensic_extraction_engine` records attacker shell commands (`attacker_command_logger`), network packets (`pcap_sniffer`), and kernel syscalls (`ebpf_probe_handler`).
   - **AR:** تدير مجمع حاويات خداعية معزولة شبكياً بشكل صارم لمنع المهاجم من الاتصال بالإنترنت أو ببيئة الإنتاج، بالتوازي مع محرك التحقيق الجنائي الذي يسجل أوامر المهاجم وحزم الشبكة ونداءات النظام لحظة بلحظة.

4. **Layer 4 — Data Backbone & SOC Operations (`data_storage`, `soc_dashboard`) | الطبقة الرابعة — البيانات وغرفة عمليات الأمان (SOC):**
   - **EN:** Persists sub-millisecond session states and real-time alert streams in `redis_store`, stores immutable forensic metadata and `SHA-256` verified artifacts in `postgresql_store`, and powers `soc_dashboard` for live telemetry charts and automated SOC incident reports.
   - **AR:** توفر البنية التحتية للتخزين السريع في Redis والتخزين الجنائي الدائم في PostgreSQL، وتغذي لوحة تحكم المدافعين بالرسوم البيانية اللحظية وتقارير الحوادث الجنائية الموثقة.

---

## 3. Team Role Distribution (4 Engineers) | جدول توزيع المهام على أعضاء الفريق الأربعة

| Engineer | Assigned Modules | Core Responsibilities (English) | المسؤوليات الأساسية (بالعربية) |
| :--- | :--- | :--- | :--- |
| **Member 1**<br>*(Gateway & Traffic Lead)* | `deception_gateway/`<br>`shared_contracts/session_schema.py`<br>`shared_contracts/alert_schema.py` | Implement the FastAPI reverse-proxy gateway, Redis session verifier, attack detector, and transparent session routing between `core_web_app` and `isolation_sandbox`. | تطوير بوابة الخداع، مصنف حركة المرور، كاشف الهجمات، والتحويل اللحظي لجلسات المهاجمين بالتكامل مع Redis. |
| **Member 2**<br>*(App & Deception Lures Lead)* | `core_web_app/`<br>`honey_token_injector/`<br>`shared_contracts/honey_token_schema.py` | Build the core web application, authentication handlers, honey token generators (fake headers/URLs), injection middleware, and token validation logic. | بناء التطبيق الحقيقي ونظام المصادقة، وتطوير مولدات الشراك الخداعية والطبقة الوسيطة لحقنها والتحقق منها. |
| **Member 3**<br>*(Sandbox & Forensics Lead)* | `isolation_sandbox/`<br>`forensic_extraction_engine/`<br>`shared_contracts/telemetry_schema.py` | Architect the Docker sandbox lifecycle manager, prewarmed container pool, session binder, decoy service, and real-time command/PCAP/eBPF telemetry collectors. | هندسة مدير حاويات العزل، المجمع المسبق التحمية، ربط الجلسات، ومحرك التقاط أوامر المهاجم وحزم PCAP ومجسات eBPF. |
| **Member 4**<br>*(Storage & SOC Dashboard Lead)* | `data_storage/`<br>`soc_dashboard/`<br>`shared_contracts/forensic_artifact_schema.py` | Implement Redis session/alert streams, PostgreSQL repositories for logs and SHA-256 artifacts, SOC visualization endpoints, and automated incident report exports. | بناء مستودعات البيانات في Redis وPostgreSQL، حفظ الأدلة الجنائية الموثقة، وتطوير لوحة تحكم SOC ومولد تقارير الحوادث. |

---

## 4. Shared Contracts (`shared_contracts`) Usage Guide | دليل استخدام العقود المشتركة

All modules across the four layers communicate strictly through the **Pydantic v2** schemas exported by `shared_contracts`. This guarantees zero schema drift between microservices.

تتواصل جميع الوحدات البرمجية في الطبقات الأربع حصرياً عبر نماذج **Pydantic v2** المعرفة داخل حزمة `shared_contracts` لضمان التوافق الصارم والتحقق التلقائي من صحة البيانات.

### Direct Package Import | الاستيراد المباشر الموحد

```python
from shared_contracts import (
    # 1. Session & Sandbox Binding
    SessionStatusEnum,
    RoutingTargetEnum,
    SessionStateContract,
    SandboxBindingContract,
    # 2. Honey Tokens
    HoneyTokenTypeEnum,
    InjectionVectorEnum,
    HoneyTokenCreateContract,
    HoneyTokenValidationContract,
    # 3. Real-Time Security Alerts
    AlertSeverityEnum,
    AttackCategoryEnum,
    SecurityAlertContract,
    # 4. Forensic Telemetry (Commands & Network/eBPF)
    TelemetrySourceEnum,
    AttackerCommandEvent,
    NetworkTelemetryEvent,
    TelemetryStreamEnvelope,
    # 5. Forensic Artifacts & SOC Incident Reports
    ArtifactTypeEnum,
    ForensicArtifactContract,
    IncidentReportContract,
)
```

### Example: Validating Session State & Serialization | مثال تطبيقي للتحقق من حالة الجلسة

```python
from shared_contracts import RoutingTargetEnum, SessionStateContract, SessionStatusEnum

# Create and strictly validate a trapped attacker session
session = SessionStateContract(
    session_id="550e8400-e29b-41d4-a716-446655440000",
    client_ip="203.0.113.42",
    user_agent="Mozilla/5.0 (X11; Linux x86_64)",
    status=SessionStatusEnum.MALICIOUS_TRAPPED,
    routing_target=RoutingTargetEnum.PREWARMED_SANDBOX,
    risk_score=95.0,
    triggered_token_id="htk_9f8e7d6c5b4a",
    assigned_container_id="honey_sbx_01a2b3c4d5e6",
    request_count=5,
    ttl_seconds=3600,
)

# Serialize to JSON for Redis storage
redis_payload: str = session.model_dump_json()

# Re-validate from JSON payload
restored_session = SessionStateContract.model_validate_json(redis_payload)
```

---

## 5. Network Isolation & Infrastructure (`docker-compose.yml`) | العزل الشبكي والبنية التحتية

The `docker-compose.yml` topology enforces strict three-tier network segmentation:
1. **`ingress_gateway_net` (`172.28.0.0/24`):** Connects `deception_gateway` with `core_web_app` (and embedded `honey_token_injector`).
2. **`sandbox_containment_net` (`172.29.0.0/24`, `internal: true`):** Air-gapped containment network for `isolation_sandbox` and `forensic_extraction_engine`. Prevents trapped attackers from initiating outbound internet connections or reaching production databases.
3. **`soc_data_backbone_net` (`172.30.0.0/24`):** Secure backend data plane linking `deception_gateway`, `forensic_extraction_engine`, `redis_store`, `postgresql_store`, and `soc_dashboard`.
