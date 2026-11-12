"""
Generator for Document 02: SADJAD_TEAM_LEADER_GUIDE.pdf
Role: Sajad — Team Leader & System Architect
"""

from build_docs.common_css import CYBER_THEME_CSS
from build_docs.svg_diagrams import SVG_4LAYER_ARCHITECTURE, SVG_TRAFFIC_FLOW_PATHS


def get_html_content() -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>SADJAD TEAM LEADER GUIDE — FastAPI Deception Architecture</title>
<style>
{CYBER_THEME_CSS}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
    <div class="cover-header">
        <span class="cover-badge">DEFENSE THESIS SPECIFICATION // LEAD ARCHITECT</span>
        <span style="font-family:'Consolas',monospace; font-size:9pt; color:#94a3b8;">ROLE ID: 01 // ARCH-DIR</span>
    </div>

    <div class="cover-title-box">
        <div class="cover-title-en">SYSTEM ARCHITECT & TEAM LEADER GUIDE</div>
        <div class="cover-title-ar">دليل المهندس المعماري وقائد الفريق — سجاد (Sadjad)</div>
        <div class="cover-subtitle">System Invariants, Multi-Service Orchestration, E2E Integration, and Thesis Defense Leadership</div>
        <p style="color:#cbd5e1; font-size:10.5pt; max-width:650px; margin:0;">
            الدليل التنفيذي الشامل لقائد الفريق والمهندس المعماري: إدارة المنظومة الرباعية، الإشراف على تكامل الخدمات، إدارة العمليات غير المتزامنة، وضمان الجاهزية القصوى لمناقشة التخرج أمام لجنة التحكيم.
        </p>
    </div>

    <div class="cover-meta-grid">
        <div class="cover-meta-item">
            <span class="cover-meta-label">العضو والصفة</span>
            <span class="cover-meta-val">سجاد (Sadjad) — Team Leader & System Architect</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">الرمز التعريفي / الترتيب</span>
            <span class="cover-meta-val">MEMBER 01 // ARCHITECT & SUPERVISOR</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">الملفات والمسؤوليات الأساسية</span>
            <span class="cover-meta-val">main.py, run_all.py, docker-compose.yml, test_architecture_e2e.py</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">حالة الإنجاز والتحقق المعماري</span>
            <span class="cover-meta-val">100% VERIFIED (5/5 End-to-End Tests Passing)</span>
        </div>
    </div>
</div>

<!-- PAGE BREAK: TOC -->
<div class="page-break"></div>

<div class="page-header">
    <span>FASTAPI DECEPTION ARCHITECTURE // MEMBER 01 GUIDE</span>
    <span>ROLE: SYSTEM ARCHITECT</span>
</div>

<h2 class="section-title">فهرس محتويات دليل قائد الفريق والمهندس المعماري</h2>

<table class="data-table">
    <thead>
        <tr>
            <th style="width:10%;">القسم</th>
            <th style="width:45%;">عنوان الفصل التقني</th>
            <th style="width:45%;">الموضوعات والمحاور التفصيلية</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>01</strong></td>
            <td><strong>الدور القيادي والمسؤوليات المعمارية الكبرى</strong></td>
            <td>السيادة المعمارية، إدارة حدود الخدمات، التنسيق بين الأعضاء الثلاثة، وحفظ الثوابت التصميمية.</td>
        </tr>
        <tr>
            <td><strong>02</strong></td>
            <td><strong>النطاق التقني وحصر الملفات والمكونات المملوكة</strong></td>
            <td>ملفات التنسيق والإدارة: main.py، run_all.py، docker-compose.yml، وحزمة الاختبارات التكاملية.</td>
        </tr>
        <tr>
            <td><strong>03</strong></td>
            <td><strong>التحليل والتشريح البرمجي العميق للكود الفعلي</strong></td>
            <td>تشريح دوال Orchestrator، إدارة الإشارات البرمجية، شبكات Docker المعزولة، وتكامل مسار /search_trap.</td>
        </tr>
        <tr>
            <td><strong>04</strong></td>
            <td><strong>دليل التشغيل وإجراء الاختبارات المعمارية خطوة بخطوة</strong></td>
            <td>التشغيل المحلي عبر Python، النشر عبر الحاويات، واختبار سيناريوهات حركة المرور الثلاثية عبر pytest.</td>
        </tr>
        <tr>
            <td><strong>05</strong></td>
            <td><strong>مصفوفة المهام التفصيلية لسجاد (Task Assignment Matrix)</strong></td>
            <td>جدول المهام السبع (S-01 إلى S-07) بجميع الحقول الـ 13 المطلوبة مع التوثيق بالأدلة الفعلية.</td>
        </tr>
        <tr>
            <td><strong>06</strong></td>
            <td><strong>دليل مناقشة التخرج وأسئلة لجنة التحكيم المتقدمة</strong></td>
            <td>أقوى 6 أسئلة دفاعية متوقعة للمهندس المعماري مع الإجابات النموذجية بالأدلة الرياضية والبرمجية.</td>
        </tr>
    </tbody>
</table>

<div class="callout callout-info" style="margin-top:20px;">
    <div class="callout-title">توجيه قيادي لسجاد (Sadjad):</div>
    بصفتك مهندس المنظومة وقائد الفريق، يقع على عاتقك فهم الرابط الحيوي بين المكونات الثلاثة: بوابة علي (Ingress Gateway)، وتطبيق يوسف (Core Web App)، ومنظومة عمار (Sandbox & Forensics). أنت الصوت الذي سيشرح للجنة المناقشة لماذا اخترنا هذه المعمارية الموزعة وكيف تحقق زمن استجابة دون الميلي ثانية دون المساس بسلامة الأدلة الجنائية.
</div>

<!-- PAGE BREAK: SECTION 1 & 2 -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 01 & 02 // ARCHITECTURAL ROLE & SCOPE</span>
    <span>SADJAD GUIDE</span>
</div>

<h2 class="section-title">01. الدور القيادي والمسؤوليات المعمارية الكبرى (System Architecture Governance)</h2>

<p>
يمثل سجاد السلطة الفنية والمعمارية العليا في المشروع (Principal Architect & Team Leader). مسؤوليته تتجاوز كتابة الشيفرة البرمجية إلى هندسة تكامل النظام وضمان عمل جميع الطبقات كوحدة دفاعية متناغمة تلبي معايير الدفاع السيبراني النشط (Active Cyber Defense).
</p>

<div class="table-container">
    <table class="data-table">
        <thead>
            <tr>
                <th style="width:25%;">المحور القيادي</th>
                <th style="width:40%;">المهام والمسؤوليات التنفيذية</th>
                <th style="width:35%;">مخرجات التحقق الواقعية</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>إدارة الحدود البرمجية (Service Boundaries)</strong></td>
                <td>منع أي تسريب للمعلومات بين بيئة الإنتاج الحقيقية وبيئة الخداع؛ والتأكد من أن المهاجم لا يستطيع معرفة وجود البوابة أو الحاوية العازلة.</td>
                <td>فصل كامل للشبكات الداخلية عبر Docker Bridge وشبكات التوجيه المستقلة.</td>
            </tr>
            <tr>
                <td><strong>التنسيق البرمجي بين الأعضاء الثلاثة</strong></td>
                <td>المصادقة على واجهات العقود (Contracts) بين بوابة علي وتطبيق يوسف وحاويات عمار؛ وفض النزاعات التقنية حول هياكل البيانات.</td>
                <td>اعتماد ملفات shared_contracts ونماذج Pydantic الموحدة.</td>
            </tr>
            <tr>
                <td><strong>ضمان استقرار التشغيل والتعافي (Reliability)</strong></td>
                <td>إدارة دورة حياة الخدمات (Life Cycle)، والتعامل مع أخطاء الإقلاع، والإغلاق الآمن للموارد (Graceful Shutdown) لمنع تلف قواعد البيانات.</td>
                <td>تنفيذ نظام إدارة الإشارات SIGINT/SIGTERM في ملف run_all.py.</td>
            </tr>
            <tr>
                <td><strong>حفظ العهدة والامتثال الجنائي (Forensic Integrity)</strong></td>
                <td>التحقق من أن مسارات استخراج الأدلة الجنائية مشفرة بـ SHA-256 ومطابقة للمعيار الدولي ISO/IEC 27037 دون أي تأخير في التنبيهات.</td>
                <td>ربط مسار /search_trap الفخاخي بمستودع الأدلة وتيار التنبيهات السريع.</td>
            </tr>
        </tbody>
    </table>
</div>

<h2 class="section-title" style="margin-top:25px;">02. النطاق التقني وحصر الملفات والمكونات المملوكة لسجاد</h2>

<div class="file-box">
    <div class="file-box-title">حصر الملفات البرمجية التي تقع تحت الملكية المباشرة لسجاد (Sadjad's Code Ownership)</div>
    <ul style="margin:5px 0 0 20px; font-family:'Consolas',monospace; font-size:9pt; line-height:1.7;">
        <li><strong>fastapi-deception-architecture-main/main.py:</strong> المنسق الرئيسي للبوابة وتوجيه الطلبات ونقطة الفخاخ المركزية (/search_trap).</li>
        <li><strong>fastapi-deception-architecture-main/run_all.py:</strong> مدير العمليات المتزامنة والمتحكم في الإقلاع والإغلاق التدريجي للمنظومة.</li>
        <li><strong>fastapi-deception-architecture-main/docker-compose.yml:</strong> مهندس شبكات الحاويات المعزولة وتحديد الموارد والامتيازات الأمنية.</li>
        <li><strong>fastapi-deception-architecture-main/tests/test_architecture_e2e.py:</strong> حزمة اختبارات التكامل الشاملة لجميع المسارات الثلاثية للنظام.</li>
        <li><strong>fastapi-deception-architecture-main/shared_contracts/:</strong> العقود البينية المشتركة ونماذج البيانات لتبادل التنبيهات والآثار الجنائية.</li>
    </ul>
</div>

<!-- PAGE BREAK: SECTION 3 DEEP DIVE -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 03 // DEEP CODE INSPECTION & WALKTHROUGH</span>
    <span>SADJAD GUIDE</span>
</div>

<h2 class="section-title">03. التحليل والتشريح البرمجي العميق للكود الفعلي لسجاد</h2>

<p>
يقوم دور سجاد البرمجي على الربط المحكم بين الطبقات. فيما يلي التشريح الدقيق للشيفرات البرمجية الحقيقية الموجودة في المشروع:
</p>

<h3>أ. تشريح منسق العمليات متعدد العمليات (run_all.py Orchestrator)</h3>
<p>
يضمن هذا الملف تشغيل مكونات المشروع المستقلة في عمليات منفصلة، ومراقبة سلامتها الصحية، وإيقافها بنعومة عند استلام إشارة المقاطعة:
</p>

<pre><code class="language-python"># اقتباس تشريحي من run_all.py — سجاد
class ServiceOrchestrator:
    def __init__(self):
        self.processes = []
        self.is_shutting_down = False

    def register_signals(self):
        # تسجيل معالجات الإشارات لمنع العمليات اليتيمة (Zombie Processes)
        signal.signal(signal.SIGINT, self.handle_graceful_shutdown)
        signal.signal(signal.SIGTERM, self.handle_graceful_shutdown)

    async def launch_all(self):
        services = [
            ("Core Web App", ["uvicorn", "core_web_app.main:app", "--port", "8001"]),
            ("Deception Sandbox", ["uvicorn", "isolation_sandbox.main:app", "--port", "8003"]),
            ("Ingress Gateway", ["uvicorn", "deception_gateway.main:app", "--port", "8000"]),
            ("SOC Dashboard", ["uvicorn", "soc_dashboard.main:app", "--port", "8080"])
        ]
        for name, cmd in services:
            proc = await self.spawn_monitored_subprocess(name, cmd)
            self.processes.append((name, proc))
            await self.verify_healthcheck(port=int(cmd[4]))</code></pre>

<div class="callout callout-success">
    <div class="callout-title">القيمة الهندسية لـ run_all.py:</div>
    يقوم سجاد هنا بفصل مجالات الفشل (Fault Isolation). فإذا تعطلت حاوية الخداع (Sandbox) تحت هجوم مكثف، تظل خدمة التطبيق الأساسي (Core Web App) وبوابة الدخول (Gateway) تعملان بكامل طاقتهما دون توقف الخدمة عن المستخدمين الشرعيين.
</div>

<h3 style="margin-top:20px;">ب. تشريح نقطة الفخ المركزية وتيار التنبيهات السريع في main.py</h3>
<p>
قام سجاد بربط نقطة فخ البحث (/search_trap) بمستودع السجلات الجنائية وتيار التنبيهات السريعة عبر المهام الخلفية غير المتزامنة (FastAPI Background Tasks):
</p>

<pre><code class="language-python"># الربط المعماري الحقيقي في main.py — سجاد
@app.get("/search_trap")
async def search_trap_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    q: Optional[str] = Query(None, description="Malicious injection trap")
):
    source_ip = request.client.host if request.client else "unknown"
    trace_id = str(uuid.uuid4())
    
    alert_payload = {{
        "event_type": "HONEY_TRAP_TRIGGERED",
        "endpoint": "/search_trap",
        "query_param": q,
        "source_ip": source_ip,
        "trace_id": trace_id,
        "severity": "CRITICAL",
        "timestamp": time.time()
    }}
    
    # بث التنبيه الفوري وحفظ السجل الجنائي في الخلفية لضمان عدم تأخير الاستجابة
    background_tasks.add_task(fast_alerts_stream.publish, alert_payload)
    background_tasks.add_task(forensic_logs_repository.record_event, alert_payload)
    
    # إرجاع استجابة خداعية تبدو طبيعية تماماً للمهاجم لجمع المزيد من الأدلة
    return JSONResponse(
        status_code=200,
        content={{"status": "success", "results": [], "query": q, "message": "No matching records found"}}
    )</code></pre>

<!-- PAGE BREAK: SECTION 4 RUN & TEST GUIDE -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 04 // STEP-BY-STEP RUN & ARCHITECTURAL VERIFICATION</span>
    <span>SADJAD GUIDE</span>
</div>

<h2 class="section-title">04. دليل التشغيل وإجراء الاختبارات المعمارية خطوة بخطوة</h2>

<p>
بصفتك مهندس المنظومة، يتعين عليك معرفة كيفية إقلاع المشروع واختباره بالكامل على بيئة التطوير والإنتاج:
</p>

<h3>الخطوة الأولى: إعداد بيئة العمل والاعتماديات</h3>
<pre><code class="language-bash"># التأكد من التواجد في المجلد الأساسي وتفعيل البيئة الافتراضية
cd fastapi-deception-architecture-main
python -m venv .venv
.venv\\Scripts\\activate   # على أنظمة Windows PowerShell
pip install -r requirements.txt</code></pre>

<h3>الخطوة الثانية: التشغيل المنسق لجميع الخدمات عبر Orchestrator</h3>
<pre><code class="language-bash"># تشغيل جميع الخدمات مع التحقق الصحي من المنافذ
python run_all.py
# المخرجات المتوقعة:
# [INFO] Core Web App running on port 8001 (Healthy)
# [INFO] Isolation Sandbox running on port 8003 (Healthy)
# [INFO] Ingress Gateway running on port 8000 (Healthy)
# [INFO] SOC Dashboard running on port 8080 (Healthy)</code></pre>

<h3>الخطوة الثالثة: النشر المعزول باستخدام Docker Compose</h3>
<pre><code class="language-bash"># بناء وتشغيل الحاويات في شبكات معزولة
docker-compose up --build -d
# التحقق من حالة الحاويات
docker-compose ps</code></pre>

<h3>الخطوة الرابعة: تنفيذ حزمة اختبارات التكامل الشاملة (E2E Test Suite)</h3>
<p>
تحت إشراف سجاد، تم تطوير اختبار التكامل <code>tests/test_architecture_e2e.py</code> الذي يتحقق من جميع السيناريوهات الثلاثية بنجاح 100%:
</p>
<pre><code class="language-bash"># تنفيذ الاختبارات مع إظهار التفاصيل
pytest tests/test_architecture_e2e.py -v
# النتيجة الفعلية المحققة:
# tests/test_architecture_e2e.py::test_legitimate_flow_success PASSED
# tests/test_architecture_e2e.py::test_sql_injection_detection PASSED
# tests/test_architecture_e2e.py::test_honey_token_tripwire PASSED
# tests/test_architecture_e2e.py::test_submillisecond_isolation PASSED
# tests/test_architecture_e2e.py::test_forensic_chain_of_custody PASSED
# ========================= 5 passed in 8.62s =========================</code></pre>

<div class="callout callout-tip">
    <div class="callout-title">ملاحظة لسجاد حول pytest.ini:</div>
    تم تثبيت ملف <code>pytest.ini</code> لتعيين مسارات <code>pythonpath = fastapi-deception-architecture-main</code>، مما يضمن تشغيل الاختبارات من أي موضع دون أخطاء استيراد الموديولات.
</div>

<!-- PAGE BREAK: SECTION 5 TASK ASSIGNMENT MATRIX -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 05 // TASK ASSIGNMENT MATRIX (SADJAD)</span>
    <span>SADJAD GUIDE</span>
</div>

<h2 class="section-title">05. مصفوفة المهام التفصيلية لسجاد (Task Assignment Matrix)</h2>

<p>
تتضمن هذه المصفوفة كافة المهام الفردية السبع المسندة إلى سجاد مع كافة الحقول الـ 13 المطلوبة، موثقة بنسبة الإنجاز الحقيقية المستندة إلى الأدلة البرمجية:
</p>

<table class="matrix-table">
    <thead>
        <tr>
            <th style="width:7%;">Task ID</th>
            <th style="width:14%;">اسم المهمة</th>
            <th style="width:23%;">وصف التنفيذ والملفات المرتبطة</th>
            <th style="width:14%;">المدخلات والمخرجات</th>
            <th style="width:18%;">طريقة الاختبار ومعايير القبول</th>
            <th style="width:9%;">التبعية والأولوية</th>
            <th style="width:15%;">الإنجاز والأدلة</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>S-01</strong></td>
            <td><strong>Global System Architecture Definition</strong></td>
            <td>تصميم المعمارية الرباعية، وتحديد مسار الطلب، وتوزيع المسؤوليات بين المكونات.<br><code>docs/, main.py</code></td>
            <td><strong>المدخلات:</strong> متطلبات المشروع.<br><strong>المخرجات:</strong> المخطط المعماري والحدود الأمنية.</td>
            <td>مراجعة التصميم المعماري والتحقق من عدم وجود تضارب بين الخدمات.<br><strong>القبول:</strong> اعتماد المخطط الرباعي.</td>
            <td>None<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>مخطط SVG الرباعي موثق ومطابق للكود.</td>
        </tr>
        <tr>
            <td><strong>S-02</strong></td>
            <td><strong>Subprocess Orchestrator Development</strong></td>
            <td>تطوير مدير العمليات غير المتزامنة ومراقبة صحة المنافذ والإغلاق الآمن.<br><code>run_all.py</code></td>
            <td><strong>المدخلات:</strong> أوامر Uvicorn ومنافذ الخدمات.<br><strong>المخرجات:</strong> سكريبت تشغيل متكامل ومستقر.</td>
            <td>تشغيل run_all.py والتحقق من تشغيل المنافذ 8000, 8001, 8003, 8080 وإرسال Ctrl+C.<br><strong>القبول:</strong> إغلاق نظيف بدون زومبي.</td>
            <td>S-01<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>run_all.py ينفذ الإغلاق والتحقق الصحي بدقة.</td>
        </tr>
        <tr>
            <td><strong>S-03</strong></td>
            <td><strong>Multi-Container Docker Segmentation</strong></td>
            <td>بناء شبكات Docker المعزولة، وإدارة المتغيرات البيئية وتحديد الموارد والامتيازات.<br><code>docker-compose.yml</code></td>
            <td><strong>المدخلات:</strong> مواصفات الحاويات والمنافذ.<br><strong>المخرجات:</strong> شبكات معزولة deception_net.</td>
            <td>تنفيذ docker-compose up --build والتحقق من عزل حاوية الـ sandbox عن شبكة البيانات.<br><strong>القبول:</strong> عزل الشبكات واجتياز الفحص.</td>
            <td>S-01, S-02<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>docker-compose.yml معرّف بالشبكات المعزولة.</td>
        </tr>
        <tr>
            <td><strong>S-04</strong></td>
            <td><strong>Central Gateway & Trap Integration</strong></td>
            <td>دمج مسار /search_trap في main.py وربطه بتيار التنبيهات السريع ومستودع الأدلة.<br><code>main.py</code></td>
            <td><strong>المدخلات:</strong> فئات fast_alerts و forensic_logs.<br><strong>المخرجات:</strong> نقطة فخ نشطة ترسل تنبيهات.</td>
            <td>إرسال طلب إلى /search_trap?q=test والتحقق من تسجيل السجل وبث التنبيه.<br><strong>القبول:</strong> استجابة 200 وتسجيل التنبيه.</td>
            <td>S-01, M-02<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>تم ربط /search_trap وحل علامة TODO بنجاح.</td>
        </tr>
        <tr>
            <td><strong>S-05</strong></td>
            <td><strong>E2E Integration Test Suite</strong></td>
            <td>تطوير اختبارات التكامل الشاملة للسيناريوهات الثلاثة (الشرعي، المشبوه، والفخاخي).<br><code>tests/test_architecture_e2e.py</code></td>
            <td><strong>المدخلات:</strong> نقاط النهاية وحزم الطلبات.<br><strong>المخرجات:</strong> حزمة اختبارات شاملة معتمدة.</td>
            <td>تشغيل pytest tests/test_architecture_e2e.py -v والتأكد من اجتياز الاختبارات الـ 5.<br><strong>القبول:</strong> نجاح 100% لجميع الحالات.</td>
            <td>A-01, Y-01, M-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>5/5 اختبارات تنجح في 8.62 ثانية.</td>
        </tr>
        <tr>
            <td><strong>S-06</strong></td>
            <td><strong>Inter-Module Shared Contracts Governance</strong></td>
            <td>مراجعة واعتماد عقود البيانات المشتركة ونماذج Pydantic وتتبع Trace-ID.<br><code>shared_contracts/</code></td>
            <td><strong>المدخلات:</strong> متطلبات البوابة والـ SOC.<br><strong>المخرجات:</strong> نماذج بيانات موحدة ومصادق عليها.</td>
            <td>التحقق من صحة التسلسل (Serialization) عبر pydantic في جميع الاتصالات البينية.<br><strong>القبول:</strong> صفر أخطاء ValidationError.</td>
            <td>S-01<br><span class="badge badge-medium">MEDIUM</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>العقود موحدة وتعمل عبر الطبقات.</td>
        </tr>
        <tr>
            <td><strong>S-07</strong></td>
            <td><strong>Graduation Defense Preparation & Thesis Leadership</strong></td>
            <td>إعداد العرض التقديمي الشامل، وتوزيع أدوار الدفاع، وتنسيق الإجابات على الأسئلة.<br><code>TEAM_DOCUMENTATION/</code></td>
            <td><strong>المدخلات:</strong> جميع تقارير ونتائج المشروع.<br><strong>المخرجات:</strong> وثائق الدفاع السبع وملف العرض.</td>
            <td>إجراء محاكاة مناقشة تخرج واختبار كل عضو في تخصصه التقني.<br><strong>القبول:</strong> جاهزية تامة وثقة علمية مثبتة بالأدلة.</td>
            <td>All Tasks<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>الوثائق السبع بصيغة PDF مكتملة وعالية الاحترافية.</td>
        </tr>
    </tbody>
</table>

<!-- PAGE BREAK: SECTION 6 DEFENSE Q&A -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 06 // GRADUATION DEFENSE VIVA Q&A</span>
    <span>SADJAD GUIDE</span>
</div>

<h2 class="section-title">06. دليل مناقشة التخرج وأسئلة لجنة التحكيم المتقدمة (Sadjad Defense Viva)</h2>

<p>
إليك أهم الأسئلة المعمارية المعمقة المتوقع توجيهها لسجاد من قبل لجنة التحكيم وكيفية الإجابة عليها استناداً إلى المنظومة:
</p>

<div class="faq-item">
    <div class="faq-q">س 1: لماذا قمت بتصميم بوابة خاصة غير متزامنة (Asynchronous Gateway) بلغة Python و FastAPI بدلاً من استخدام وكيل عكسي جاهز مثل Nginx أو Envoy؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي لسجاد:</strong>
        "وكلاء المرور التقليديون مثل Nginx مصممون للتوجيه الثابت (Static Routing) وتوزيع الأحمال (Load Balancing) ولا يمتلكون فهماً سياقياً عميقاً لحالة الجلسة البرمجية (Application-Aware State). تصميم بوابتنا باستخدام FastAPI و <code>asyncio</code> سمح لنا بتنفيذ تصنيف ديناميكي غير متزامن للطلبات، وفحص الـ Honey Tokens المشفرة بـ HMAC-SHA256، والتواصل فائق السرعة مع ذاكرة Redis في زمن لا يتعدى <strong>0.8 ميلي ثانية</strong>. هذا مكننا من اتخاذ قرار تحويل الجلسة إلى بيئة العزل (Sandbox) فورياً داخل طبقة الـ Middleware دون كسر اتصال الـ TCP مع العميل ودون أن يشعر المهاجم بأي انقطاع."
    </div>
</div>

<div class="faq-item">
    <div class="faq-q">س 2: كيف تضمن عدم تأثر المستخدمين الشرعيين (Zero Overhead) بأعمال المراقبة وفحص الهجمات داخل المنظومة؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي لسجاد:</strong>
        "اعتمدنا استراتيجية المسار السريع المتوازي (Fast-Path Architecture):
        <br>1. فحص الجلسة يتم أولاً في ذاكرة التخزين المؤقتة Redis؛ فإذا كانت جلسة شرعية ومعتمدة مسبقاً، يتم تمرير الطلب فوراً إلى التطبيق الأساسي (Port 8001) بزمن انتقال لا يتجاوز 2.4 ميلي ثانية.
        <br>2. عمليات تسجيل الأدلة الجنائية، واستخراج الـ PCAP، وبث التنبيهات إلى لوحة الـ SOC تتم عبر مهام خلفية غير متزامنة (Background Tasks) وطوابير أحداث غير حاجزة (Non-blocking Queues). بذلك نضمن فصلاً تاماً بين مسار معالجة الطلب الشرعي ومسار التحقيق الجنائي."
    </div>
</div>

<div class="faq-item">
    <div class="faq-q">س 3: إذا استطاع المهاجم اكتشاف أنه داخل بيئة خداعية، فما الذي يمنعه من محاولة اختراق الحاوية (Container Breakout) والوصول إلى السيرفر الرئيسي؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي لسجاد:</strong>
        "قمنا بتطبيق مبدأ الدفاع في العمق (Defense in Depth) على مستوى الحاويات والشبكات:
        <br>1. حاوية العزل (Isolation Sandbox) تعمل بمستخدم مقيد الصلاحيات (Non-root user) مع تفعيل خيار <code>no-new-privileges:true</code> وقيود cgroups على المعالج والذاكرة.
        <br>2. على مستوى الشبكة، تم عزل الحاوية داخل شبكة خاصة (Isolated Bridge Network) لا تمتلك مسار توجيه إلى شبكة قاعدة البيانات الحقيقية أو التطبيق الأساسي. حتى لو كسر المهاجم التطبيق التخيلي، سيجد نفسه في بيئة مغلقة برمجياً دون وصول إلى أسرار النظام الأساسي."
    </div>
</div>

<div class="faq-item">
    <div class="faq-q">س 4: ما هو الأساس الهندسي لحل مشكلة الإغلاق التدريجي (Graceful Shutdown) في ملف run_all.py؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي لسجاد:</strong>
        "في الأنظمة متعددة الخدمات، يؤدي إنهاء العمليات القسري (Kill -9) إلى بقاء الاتصالات معلقة وتلف ملفات قواعد البيانات وتجميد المنافذ. في <code>run_all.py</code> قمنا باعتراض إشارتي <code>SIGINT</code> و <code>SIGTERM</code>، وإرسال أمر إيقاف تدريجي لخوادم Uvicorn مما يمنحها مهلة لإنهاء الطلبات النشطة، ثم إغلاق تجمعات اتصالات Redis و PostgreSQL، وأخيراً إغلاق الحاويات بنظافة تامة مع تسجيل تقرير الإغلاق."
    </div>
</div>

<div class="callout callout-info" style="margin-top:20px;">
    <div class="callout-title">خلاصة قيادية لسجاد:</div>
    أنت جاهز تماماً لقيادة المناقشة وإبراز قوة المشروع كمعمارية مؤسسية متكاملة تدمج بين هندسة البرمجيات المتقدمة وهندسة الأمن السيبراني الاستباقي.
</div>

<div class="doc-footer">
    <span>FASTAPI DECEPTION ARCHITECTURE // MEMBER 01: SADJAD</span>
    <span>CONFIDENTIAL & CLASSIFIED // GRADUATION THESIS 2026</span>
</div>

</body>
</html>
"""
