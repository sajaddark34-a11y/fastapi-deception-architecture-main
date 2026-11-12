"""
Generator for Document 06: TEAM_INTEGRATION_MAP.pdf
Title: خريطة التكامل الشاملة للمنظومة الدفاعية (Team Integration Map)
"""

from build_docs.common_css import CYBER_THEME_CSS
from build_docs.svg_diagrams import (
    SVG_4LAYER_ARCHITECTURE,
    SVG_CHAIN_OF_CUSTODY,
    SVG_TRAFFIC_FLOW_PATHS,
    SVG_PREWARMED_POOL,
)


def get_html_content() -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>TEAM INTEGRATION MAP — FastAPI Deception Architecture</title>
<style>
{CYBER_THEME_CSS}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
    <div class="cover-header">
        <span class="cover-badge">SYSTEM INTEGRATION SPECIFICATION // MAP & PROTOCOLS</span>
        <span style="font-family:'Consolas',monospace; font-size:9pt; color:#94a3b8;">DOC ID: 06 // INT-MAP</span>
    </div>

    <div class="cover-title-box">
        <div class="cover-title-en">END-TO-END SYSTEM INTEGRATION MAP</div>
        <div class="cover-title-ar">خريطة التكامل الشاملة للمنظومة الدفاعية وواجهات الربط البيني</div>
        <div class="cover-subtitle">Complete Inter-Module Dependency Map, Asynchronous Traffic Lifecycles, Network Isolation Topologies, and Boot Orchestration</div>
        <p style="color:#cbd5e1; font-size:10.5pt; max-width:650px; margin:0;">
            المرجع المعماري الهندسي الموحد لكافة مسارات تدفق البيانات بين الطبقات الأربع: من لحظة دخول الحزمة عبر المنفذ 8000، مروراً بالفحص الاستدلالي السريع، وحقن التوكنات، حتى العزل في بيئات الـ Sandbox وختم الأدلة الجنائية بـ SHA-256 وبث القياسات الحية إلى لوحة الـ SOC.
        </p>
    </div>

    <div class="cover-meta-grid">
        <div class="cover-meta-item">
            <span class="cover-meta-label">المنظومة المعمارية</span>
            <span class="cover-meta-val">FastAPI Deception Architecture (4-Layer Reactive Defense)</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">أعضاء الفريق ومسؤوليات الربط</span>
            <span class="cover-meta-val">سجاد (المعمارية)، علي (البوابة)، يوسف (التطبيق)، عمار (العزل والجنائيات)</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">المنافذ والبروتوكولات البينية</span>
            <span class="cover-meta-val">8000 (Gateway), 8001 (Core App), 8003 (Sandbox), 8080 (SOC), 6379 (Redis)</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">حالة التحقق والتكامل الشامل</span>
            <span class="cover-meta-val">100% PASS (End-to-End Test Suite Validated)</span>
        </div>
    </div>
</div>

<!-- PAGE BREAK: SECTION 1 ARCHITECTURE MAP -->
<div class="page-break"></div>

<div class="page-header">
    <span>FASTAPI DECEPTION ARCHITECTURE // INTEGRATION MAP</span>
    <span>SECTION 01: SYSTEM TOPOLOGY</span>
</div>

<h2 class="section-title">01. المعمارية الرباعية المتكاملة وخريطة تدفق النظام</h2>

<p>
تم بناء المنظومة وفق مبدأ الطبقات الدفاعية المنفصلة (Decoupled Defense Layers)؛ حيث يتولى كل عضو قيادة طبقة مستقلة تعمل بتناغم غير متزامن عبر شبكات داخلية معزولة:
</p>

<div style="margin:20px 0; text-align:center;">
{SVG_4LAYER_ARCHITECTURE}
</div>

<div class="table-container">
    <table class="data-table">
        <thead>
            <tr>
                <th style="width:12%;">الطبقة</th>
                <th style="width:23%;">المكون والمنفذ</th>
                <th style="width:18%;">المسؤول المباشر</th>
                <th style="width:47%;">الدور المعماري والتكاملي</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Layer 1</strong></td>
                <td><strong>Ingress Gateway</strong><br><span style="font-family:'Consolas',monospace; font-size:8.5pt;">Port 8000 (HTTP/TCP)</span></td>
                <td><strong>علي (Ali)</strong><br><span class="badge badge-high">MEMBER 02</span></td>
                <td>حراسة المدخل الخارجي الوحيد، فحص الحمولات الاستدلالية، التحقق السريع من الذاكرة المؤقتة، وتوجيه الجلسات الشفاف.</td>
            </tr>
            <tr>
                <td><strong>Layer 2</strong></td>
                <td><strong>Core Web App & Injector</strong><br><span style="font-family:'Consolas',monospace; font-size:8.5pt;">Port 8001 (Internal)</span></td>
                <td><strong>يوسف (Yousif) & عمار</strong><br><span class="badge badge-success">MEMBER 03 & 04</span></td>
                <td>تنفيذ منطق الأعمال للمستخدمين الشرعيين، إصدار توكنات JWT المشفرة، وحقن التوكنات الفخاخية (Honey Tokens) في الاستجابات.</td>
            </tr>
            <tr>
                <td><strong>Layer 3</strong></td>
                <td><strong>Isolation Sandbox Pool</strong><br><span style="font-family:'Consolas',monospace; font-size:8.5pt;">Port 8003 (Isolated)</span></td>
                <td><strong>عمار (Ammar)</strong><br><span class="badge badge-critical">MEMBER 04</span></td>
                <td>احتجاز المهاجمين داخل حاويات معزولة دافئة مسبقاً، محاكاة الخدمات وقواعد البيانات الوهمية، واستنزاف وقت وجهد المهاجم.</td>
            </tr>
            <tr>
                <td><strong>Layer 4</strong></td>
                <td><strong>Storage, DFIR & SOC</strong><br><span style="font-family:'Consolas',monospace; font-size:8.5pt;">Port 8080 (SOC) / 6379</span></td>
                <td><strong>سجاد، يوسف، عمار</strong><br><span class="badge badge-info">TEAM ALL</span></td>
                <td>توثيق الأدلة الرقمية المشفرة بـ SHA-256، إدارة قواعد بيانات PostgreSQL و Redis، وبث القياسات الحية عبر WebSockets.</td>
            </tr>
        </tbody>
    </table>
</div>

<!-- PAGE BREAK: SECTION 2 DETAILED TRAFFIC FLOWS -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 02 // TRAFFIC LIFECYCLES & PATH ROUTING</span>
    <span>INTEGRATION MAP</span>
</div>

<h2 class="section-title">02. خرائط تدفق الحزم والطلبات التفصيلية (Three Concurrent Paths)</h2>

<p>
تتعامل المنظومة مع ثلاثة مسارات متزامنة ومستقلة تماماً لحركة المرور، تم تصميم كل مسار لضمان الأمان والسرعة القصوى:
</p>

<div style="margin:15px 0;">
{SVG_TRAFFIC_FLOW_PATHS}
</div>

<h3>المسار الأول (Path A): حركة المرور الشرعية النظيفة (Legitimate User Journey)</h3>
<ol style="line-height:1.8; margin-top:5px;">
    <li><strong>الدخول:</strong> يصل طلب العميل إلى البوابة (Port 8000) حاملاً توكن مصادقة JWT.</li>
    <li><strong>الفحص السريع:</strong> يقوم <code>traffic_classifier.py</code> بفحص المعاملات؛ خلوها من الهجمات وسريان الجلسة في Redis ينتج عنه Cache Hit في أقل من <strong>0.8 ميلي ثانية</strong>.</li>
    <li><strong>التمرير المباشر:</strong> يتم تمرير الطلب داخلياً إلى التطبيق الأساسي (Port 8001).</li>
    <li><strong>المعالجة والحقن:</strong> ينفذ التطبيق استعلامات الأعمال في PostgreSQL، وتقوم برمجية عمار الوسيطة (<code>injector_middleware.py</code>) بحقن توكن خداعي خامل خفي في استجابة JSON.</li>
    <li><strong>الخروج:</strong> يستلم المستخدم الشرعي استجابة نظيفة بسرعة إجمالية <strong>2.4 ميلي ثانية</strong> دون أن يشعر بوجود أي منظومة دفاعية خلف الكواليس.</li>
</ol>

<h3>المسار الثاني (Path B): حركة المرور الاستطلاعية والمشبوهة (Reconnaissance Journey)</h3>
<ol style="line-height:1.8; margin-top:5px;">
    <li><strong>الرصد:</strong> يرسل المهاجم أو أداة الفحص الآلية حمولة مشبوهة (مثل <code>' OR 1=1 --</code> أو محاولة قراءة <code>/etc/passwd</code>).</li>
    <li><strong>احتساب التهديد:</strong> يكتشف <code>attack_detector.py</code> النمط وتتجاوز درجة الخطر العتبة المحددة (Score &ge; 70).</li>
    <li><strong>التخصيص الفوري للحاوية:</strong> يتم وسم معرف الجلسة بالخطر في Redis، ويقوم <code>prewarmed_pool.py</code> بتخصيص حاوية عازلة دافئة في أقل من <strong>10 ميلي ثانية</strong>.</li>
    <li><strong>التوجيه الشفاف:</strong> يقوم <code>malicious_session_router.py</code> بإعادة توجيه الطلب إلى المنفذ 8003 لترجع له بيئة الخداع استجابة HTTP 200 طبيعية مع بيانات تخيلية تماماً.</li>
    <li><strong>التسجيل الجنائي:</strong> تنطلق مهام الخلفية لجمع حزم الاتصال وتثبيتها في سلسلة العهدة دون كسر الاتصال مع المهاجم.</li>
</ol>

<h3>المسار الثالث (Path C): فخاخ الزناد الفوري (Instant Canary & Trap Tripwire)</h3>
<ol style="line-height:1.8; margin-top:5px;">
    <li><strong>لمس الفخ:</strong> يقوم المتسلل بطلب رابط الفخ المعلن في ملف robots.txt أو استدعاء مسار <code>/search_trap</code> أو استخدام مفتاح API وهمي تم حقنه مسبقاً.</li>
    <li><strong>اليقين القاطع:</strong> لكون هذا المسار فخاً صامتاً لا يزوره أي مستخدم شرعي، يتم تصنيف التهديد فورياً كـ <strong>CRITICAL</strong> بيقين 100% وصفر إنذار كاذب.</li>
    <li><strong>بث التنبيه السريع:</strong> يقوم <code>main.py</code> عبر Background Tasks بدفع إشعار التنبيه الفوري إلى تيار Redis ومستودع السجلات.</li>
    <li><strong>العزل والإغلاق:</strong> يتم حظر الـ IP المعادي فورياً وعزل أي اتصالات جارية ونقل الأدلة إلى مستودع الأدلة المشفرة.</li>
</ol>

<!-- PAGE BREAK: SECTION 3 API CONTRACTS -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 03 // INTER-MODULE API & CONTRACT MATRIX</span>
    <span>INTEGRATION MAP</span>
</div>

<h2 class="section-title">03. مصفوفة عقود واجهات البرمجة والبروتوكولات البينية (API Contract Matrix)</h2>

<p>
توضح هذه المصفوفة العقود البرمجية الرسمية المعتمدة لتبادل البيانات بين المكونات الأربعة:
</p>

<table class="data-table">
    <thead>
        <tr>
            <th style="width:18%;">المسار / البروتوكول</th>
            <th style="width:12%;">المرسل & المستلم</th>
            <th style="width:25%;">الترويسات والحقول الإلزامية</th>
            <th style="width:30%;">هيكل الحمولة وموديل Pydantic</th>
            <th style="width:15%;">الرمز وزمن الاستجابة</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>POST /api/v1/auth/login</strong></td>
            <td>Client &rarr; Core Web App (via Gateway)</td>
            <td><code>Content-Type: application/json</code></td>
            <td><code>LoginRequestSchema: {{"username", "password"}}</code></td>
            <td>HTTP 200<br>&lt; 4.0ms</td>
        </tr>
        <tr>
            <td><strong>GET /api/v1/profile</strong></td>
            <td>Client &rarr; Core Web App (via Gateway)</td>
            <td><code>Authorization: Bearer &lt;JWT&gt;</code><br><code>X-Trace-ID: &lt;UUID&gt;</code></td>
            <td><code>UserProfileResponseSchema: {{"user_id", "role", "data"}}</code></td>
            <td>HTTP 200<br>&lt; 2.5ms</td>
        </tr>
        <tr>
            <td><strong>GET /search_trap</strong></td>
            <td>Attacker &rarr; Gateway Tripwire</td>
            <td><code>X-Trace-ID: &lt;UUID&gt;</code></td>
            <td><code>QueryParam: ?q=&lt;payload&gt;</code><br>Fast Alert Payload dispatched to Redis</td>
            <td>HTTP 200<br>&lt; 1.0ms</td>
        </tr>
        <tr>
            <td><strong>PROXY /api/v1/*</strong></td>
            <td>Gateway &rarr; Isolation Sandbox (Port 8003)</td>
            <td><code>X-Deception-Trapped: true</code><br><code>X-Session-ID: &lt;ID&gt;</code></td>
            <td>Transparent Request Forwarding via <code>httpx.AsyncClient</code></td>
            <td>HTTP 200 (Decoy)<br>&lt; 8.0ms</td>
        </tr>
        <tr>
            <td><strong>WS /ws/soc/alerts</strong></td>
            <td>SOC Dashboard &larr; Fast Alerts Stream</td>
            <td><code>Sec-WebSocket-Protocol</code></td>
            <td><code>AlertEventContract: {{"event", "severity", "trace_id", "mitre_id"}}</code></td>
            <td>WS Frame<br>&lt; 50ms</td>
        </tr>
        <tr>
            <td><strong>POST /forensics/seal</strong></td>
            <td>Sandbox &rarr; DFIR Engine Vault</td>
            <td><code>X-Internal-Token: &lt;Secret&gt;</code></td>
            <td><code>ArtifactBlockSchema: {{"prev_hash", "artifact_sha", "metadata"}}</code></td>
            <td>HTTP 201<br>&lt; 15ms</td>
        </tr>
    </tbody>
</table>

<div class="callout callout-info" style="margin-top:20px;">
    <div class="callout-title">معيار توحيد معرف التتبع (X-Trace-ID Invariant):</div>
    كل طلب يعبر البوابة يحصل على معرف فريد (UUID4) يسمى <code>X-Trace-ID</code>. ينتقل هذا المعرف عبر كافة الطبقات، ويتم تسجيله في سجلات التطبيق، وحاويات العزل، وسلسلة العهدة الجنائية، ولوحة الـ SOC؛ مما يتيح تتبع مسار أي هجوم بدقة متناهية من البداية حتى النهاية.
</div>

<!-- PAGE BREAK: SECTION 4 & 5 TOPOLOGY & BOOT -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 04 & 05 // TOPOLOGY, BOUNDARIES & BOOT ORCHESTRATION</span>
    <span>INTEGRATION MAP</span>
</div>

<h2 class="section-title">04. خريطة الاعتماديات وحدود الأمان والشبكات (Security Boundaries)</h2>

<p>
تعتمد المنظومة سياسة انعدام الثقة (Zero-Trust Architecture) وعزل الشبكات عبر Docker Networks:
</p>

<div class="table-container">
    <table class="data-table">
        <thead>
            <tr>
                <th style="width:25%;">اسم الشبكة المعزولة</th>
                <th style="width:35%;">الخدمات المشتركة في النطاق</th>
                <th style="width:40%;">سياسة الأمان وعزل الوصول (Firewall Rules)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>public_ingress_net</strong><br><span style="font-family:'Consolas',monospace; font-size:8pt;">172.20.0.0/24</span></td>
                <td>Ingress Gateway (Port 8000 فقط مكشوف خارجياً).</td>
                <td>تسمح بدخول حركة المرور من الإنترنت عبر المنفذ 8000 فقط؛ حظر الوصول المباشر لأي خدمات أخرى.</td>
            </tr>
            <tr>
                <td><strong>core_internal_net</strong><br><span style="font-family:'Consolas',monospace; font-size:8pt;">172.21.0.0/24</span></td>
                <td>Ingress Gateway &harr; Core Web App &harr; PostgreSQL &harr; Redis.</td>
                <td>شبكة داخلية مغلقة تماماً؛ لا تمتلك أي وصول مباشر للإنترنت وتمنع اتصال حاويات الـ Sandbox بها.</td>
            </tr>
            <tr>
                <td><strong>sandbox_isolated_net</strong><br><span style="font-family:'Consolas',monospace; font-size:8pt;">172.22.0.0/24</span></td>
                <td>Ingress Gateway (Proxy) &harr; Prewarmed Sandboxes &harr; DFIR Collector.</td>
                <td>بيئة عزل محكمة ومقيدة بـ <code>no-new-privileges</code> وذاكرة محددة (256MB)؛ حظر كامل للوصول إلى شبكة الإنتاج.</td>
            </tr>
            <tr>
                <td><strong>soc_telemetry_net</strong><br><span style="font-family:'Consolas',monospace; font-size:8pt;">172.23.0.0/24</span></td>
                <td>DFIR Vault &harr; Redis Streams &harr; SOC Dashboard (Port 8080).</td>
                <td>شبكة مراقبة آمنة ومخصصة لمحللي الأمن لمشاهدة البيانات والتحكم في إجراءات الاحتواء.</td>
            </tr>
        </tbody>
    </table>
</div>

<h2 class="section-title" style="margin-top:25px;">05. تسلسل الإقلاع والتحقق الصحي للمنظومة (Boot Sequence)</h2>

<p>
يتم تشغيل المنظومة عبر <code>run_all.py</code> وفق ترتيب حاسم يمنع أخطاء فقدان الاتصال:
</p>

<div class="table-container">
    <table class="data-table">
        <thead>
            <tr>
                <th style="width:10%;">الخطوة</th>
                <th style="width:25%;">الخدمة الجاري إقلاعها</th>
                <th style="width:35%;">آلية التحقق الصحي (Health Probe)</th>
                <th style="width:30%;">الإجراء عند الفشل</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>01</strong></td>
                <td><strong>Data Storage Layer</strong><br>(Redis & PostgreSQL)</td>
                <td>محاولة الاتصال عبر PING و SELECT 1 والتأكد من استقرار المنفذ 6379 و 5432.</td>
                <td>تفعيل FallbackInMemoryStore تلقائياً للاستمرار بدون تعطل.</td>
            </tr>
            <tr>
                <td><strong>02</strong></td>
                <td><strong>Core Web App</strong><br>(Port 8001)</td>
                <td>إرسال طلب GET إلى <code>/healthz</code> والتأكد من إرجاع HTTP 200 وتوفر التوكنات.</td>
                <td>إعادة المحاولة 3 مرات ثم إيقاف العملية وتسجيل تقرير الخطأ.</td>
            </tr>
            <tr>
                <td><strong>03</strong></td>
                <td><strong>Isolation Sandbox & Pool</strong><br>(Port 8003)</td>
                <td>التحقق من جاهزية 3 حاويات دافئة واستجابة مسار <code>/sandbox/health</code>.</td>
                <td>إعادة تشغيل الحاويات الميتة في المجمع بصورة آلية.</td>
            </tr>
            <tr>
                <td><strong>04</strong></td>
                <td><strong>Forensic Vault & SOC</strong><br>(Port 8080)</td>
                <td>التحقق من جاهزية سلسلة العهدة (Genesis Block) واستقرار خادم الـ WebSockets.</td>
                <td>إعادة تهيئة مخزن الهاش المشفر ومتابعة البث.</td>
            </tr>
            <tr>
                <td><strong>05</strong></td>
                <td><strong>Ingress Gateway</strong><br>(Port 8000)</td>
                <td>التحقق من فتح مقبس الاستماع الخارجي وجاهزية الموجه للاتصال بكافة المنافذ.</td>
                <td>عدم فتح المنفذ 8000 إلا بعد تيقن سلامة جميع الطبقات الخلفية.</td>
            </tr>
        </tbody>
    </table>
</div>

<div class="doc-footer">
    <span>FASTAPI DECEPTION ARCHITECTURE // SYSTEM INTEGRATION MAP</span>
    <span>CONFIDENTIAL & CLASSIFIED // GRADUATION THESIS 2026</span>
</div>

</body>
</html>
"""
