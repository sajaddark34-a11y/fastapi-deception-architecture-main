"""
Generator for Document 07: TEAM_DEVELOPMENT_ROADMAP.pdf
Title: خريطة الطريق التنفيذية ومصفوفة إدارة المهام (Team Development Roadmap & WBS)
"""

from build_docs.common_css import CYBER_THEME_CSS
from build_docs.svg_diagrams import SVG_4LAYER_ARCHITECTURE, SVG_TRAFFIC_FLOW_PATHS


def get_html_content() -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>TEAM DEVELOPMENT ROADMAP — FastAPI Deception Architecture</title>
<style>
{CYBER_THEME_CSS}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
    <div class="cover-header">
        <span class="cover-badge">PROJECT MANAGEMENT & GOVERNANCE // ROADMAP & WBS</span>
        <span style="font-family:'Consolas',monospace; font-size:9pt; color:#94a3b8;">DOC ID: 07 // ROADMAP-WBS</span>
    </div>

    <div class="cover-title-box">
        <div class="cover-title-en">MASTER DEVELOPMENT ROADMAP & WBS MATRIX</div>
        <div class="cover-title-ar">خريطة الطريق التنفيذية ومصفوفة تفصيل هيكل العمل وإدارة المهام</div>
        <div class="cover-subtitle">Complete 28-Task Work Breakdown Structure, Enterprise RACI Governance, Git Review Workflows, and Graduation Defense Milestones</div>
        <p style="color:#cbd5e1; font-size:10.5pt; max-width:650px; margin:0;">
            الدليل التنظيمي والإداري المتكامل لمشروع التخرج: مصفوفة المهام الفردية الشاملة الموزعة على الأعضاء الأربعة، حوكمة المسؤوليات عبر نموذج RACI، معايير القبول البرمجية الصارمة (Definition of Done)، والجدول الزمني للجاهزية الدفاعية النهائية.
        </p>
    </div>

    <div class="cover-meta-grid">
        <div class="cover-meta-item">
            <span class="cover-meta-label">إجمالي المهام المعتمدة</span>
            <span class="cover-meta-val">28 TASK (7 Tasks per Team Member)</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">إدارة الحوكمة والمشروع</span>
            <span class="cover-meta-val">سجاد (Team Leader & Project Governance)</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">نسبة الإنجاز الفعلية المثبتة</span>
            <span class="cover-meta-val">100% COMPLETED (Evidence-Backed by Test Suite)</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">الحالة المعمارية للمشروع</span>
            <span class="cover-meta-val">DEFENSE-READY // FULL HARMONY</span>
        </div>
    </div>
</div>

<!-- PAGE BREAK: SECTION 1 MASTER WBS MATRIX -->
<div class="page-break"></div>

<div class="page-header">
    <span>FASTAPI DECEPTION ARCHITECTURE // ROADMAP & WBS</span>
    <span>SECTION 01: MASTER WORK BREAKDOWN STRUCTURE (TASKS S-01 TO S-07 & A-01 TO A-07)</span>
</div>

<h2 class="section-title">01. مصفوفة تفصيل هيكل العمل المتكاملة (Master WBS Matrix — Part 1)</h2>

<p>
توزيع المهام الفردية الموثقة للأعضاء الأربعة (28 مهمة)، مصنفة ومقيمة بالأدلة الواقعية المستندة إلى شيفرة المشروع واختباراته:
</p>

<h3>أ. مهام سجاد (Sadjad — Team Leader & Architect)</h3>
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
            <td>Global System Architecture</td>
            <td>تصميم المعمارية الرباعية، وتحديد مسار الطلب، وتوزيع الأدوار.<br><code>docs/, main.py</code></td>
            <td><strong>المدخلات:</strong> متطلبات المشروع.<br><strong>المخرجات:</strong> المخطط والحدود الأمنية.</td>
            <td>مراجعة التصميم والتحقق من عدم وجود تضارب.<br><strong>القبول:</strong> اعتماد المخطط الرباعي.</td>
            <td>None<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>المخطط الرباعي موثق ومطبق بالكود.</td>
        </tr>
        <tr>
            <td><strong>S-02</strong></td>
            <td>Subprocess Orchestrator</td>
            <td>تطوير مدير العمليات المتزامنة ومراقبة صحة المنافذ والإغلاق الآمن.<br><code>run_all.py</code></td>
            <td><strong>المدخلات:</strong> أوامر Uvicorn ومنافذ الخدمات.<br><strong>المخرجات:</strong> سكريبت تشغيل مستقر.</td>
            <td>تشغيل run_all.py والتحقق من المنافذ وإرسال Ctrl+C.<br><strong>القبول:</strong> إغلاق نظيف بدون زومبي.</td>
            <td>S-01<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>run_all.py يدير المنافذ بنجاح.</td>
        </tr>
        <tr>
            <td><strong>S-03</strong></td>
            <td>Docker Segmentation</td>
            <td>بناء شبكات Docker المعزولة وإدارة المتغيرات والامتيازات.<br><code>docker-compose.yml</code></td>
            <td><strong>المدخلات:</strong> مواصفات الحاويات والمنافذ.<br><strong>المخرجات:</strong> شبكات معزولة deception_net.</td>
            <td>تشغيل docker-compose والتحقق من عزل الـ sandbox.<br><strong>القبول:</strong> عزل الشبكات واجتياز الفحص.</td>
            <td>S-01, S-02<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>docker-compose.yml معرّف بالشبكات المعزولة.</td>
        </tr>
        <tr>
            <td><strong>S-04</strong></td>
            <td>Central Gateway & Trap</td>
            <td>دمج مسار /search_trap في main.py وربطه بالتيار ومستودع السجلات.<br><code>main.py</code></td>
            <td><strong>المدخلات:</strong> فئات fast_alerts و forensic_logs.<br><strong>المخرجات:</strong> نقطة فخ نشطة ترسل تنبيهات.</td>
            <td>إرسال طلب لـ /search_trap والتحقق من السجل والتنبيه.<br><strong>القبول:</strong> استجابة 200 وتسجيل التنبيه.</td>
            <td>S-01, M-02<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>تم ربط /search_trap وإزالة TODO.</td>
        </tr>
        <tr>
            <td><strong>S-05</strong></td>
            <td>E2E Integration Test Suite</td>
            <td>تطوير اختبارات التكامل للسيناريوهات الثلاثية.<br><code>tests/test_architecture_e2e.py</code></td>
            <td><strong>المدخلات:</strong> نقاط النهاية وحزم الطلبات.<br><strong>المخرجات:</strong> حزمة اختبارات شاملة معتمدة.</td>
            <td>تشغيل pytest والتأكد من اجتياز الاختبارات الـ 5.<br><strong>القبول:</strong> نجاح 100% لجميع الحالات.</td>
            <td>A-01, Y-01, M-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>5/5 اختبارات تنجح في 8.62 ثانية.</td>
        </tr>
        <tr>
            <td><strong>S-06</strong></td>
            <td>Inter-Module Contracts</td>
            <td>مراجعة واعتماد عقود البيانات المشتركة وتتبع Trace-ID.<br><code>shared_contracts/</code></td>
            <td><strong>المدخلات:</strong> متطلبات البوابة والـ SOC.<br><strong>المخرجات:</strong> نماذج بيانات موحدة.</td>
            <td>التحقق من صحة التسلسل عبر pydantic.<br><strong>القبول:</strong> صفر أخطاء ValidationError.</td>
            <td>S-01<br><span class="badge badge-medium">MEDIUM</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>العقود موحدة وتعمل عبر الطبقات.</td>
        </tr>
        <tr>
            <td><strong>S-07</strong></td>
            <td>Defense Preparation</td>
            <td>إعداد العرض التقديمي الشامل وتنسيق أدوار الدفاع.<br><code>TEAM_DOCUMENTATION/</code></td>
            <td><strong>المدخلات:</strong> جميع تقارير ونتائج المشروع.<br><strong>المخرجات:</strong> وثائق الدفاع السبع وملف العرض.</td>
            <td>إجراء محاكاة مناقشة تخرج واختبار كل عضو.<br><strong>القبول:</strong> جاهزية تامة وثقة علمية مثبتة.</td>
            <td>All Tasks<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>الوثائق السبع جاهزة بأعلى احترافية.</td>
        </tr>
    </tbody>
</table>

<h3>ب. مهام علي (Ali — Backend & Deception Gateway Engineer)</h3>
<table class="matrix-table" style="margin-top:10px;">
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
            <td><strong>A-01</strong></td>
            <td>Traffic Classifier Engine</td>
            <td>تطوير محرك تصنيف حركة المرور السريع لفرز المسارات.<br><code>traffic_classifier.py</code></td>
            <td><strong>المدخلات:</strong> كائن Request.<br><strong>المخرجات:</strong> تصنيف الجلسة النظيفة/المشبوهة.</td>
            <td>إرسال طلبات متعددة وقياس زمن التصنيف.<br><strong>القبول:</strong> زمن الفحص أقل من 2ms.</td>
            <td>S-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>زمن التصنيف الفعلي أقل من 2ms.</td>
        </tr>
        <tr>
            <td><strong>A-02</strong></td>
            <td>Heuristic Attack Detection</td>
            <td>بناء مصفوفة التعبير النمطي لكشف SQLi, XSS, Path Traversal.<br><code>attack_detector.py</code></td>
            <td><strong>المدخلات:</strong> نصوص المعاملات والترويسات.<br><strong>المخرجات:</strong> درجة الخطر وقائمة الأنماط.</td>
            <td>اختبار 20 حمولة هجومية شائعة.<br><strong>القبول:</strong> دقة كشف 100% للحمولات المعروفة.</td>
            <td>A-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>كشف فوري ودقيق في اختبارات E2E.</td>
        </tr>
        <tr>
            <td><strong>A-03</strong></td>
            <td>Redis Cache Verifier</td>
            <td>الربط المباشر بـ Redis للتحقق من حالة الجلسات الموسومة.<br><code>redis_cache_verifier.py</code></td>
            <td><strong>المدخلات:</strong> معرف الجلسة.<br><strong>المخرجات:</strong> حالة العزل الحالية (Cached State).</td>
            <td>استعلام الجلسة وقياس وقت الاستجابة.<br><strong>القبول:</strong> زمن الاستجابة &lt; 0.8ms.</td>
            <td>Y-03<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>يعمل مع دعم الـ Fallback عند الحاجة.</td>
        </tr>
        <tr>
            <td><strong>A-04</strong></td>
            <td>Session Router Proxy</td>
            <td>توجيه الطلبات المشبوهة عبر وكيل شفاف إلى المنفذ 8003.<br><code>malicious_session_router.py</code></td>
            <td><strong>المدخلات:</strong> الطلب المعادي وعنوان الـ Sandbox.<br><strong>المخرجات:</strong> استجابة 200 خداعية.</td>
            <td>التحقق من وصول الطلب للـ Sandbox دون قطع الاتصال.<br><strong>القبول:</strong> استجابة شفافة بدون أخطاء.</td>
            <td>A-02, M-03<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>التوجيه الشفاف يعمل بدقة عالية.</td>
        </tr>
        <tr>
            <td><strong>A-05</strong></td>
            <td>TCP L4 Deception Proxy</td>
            <td>اعتراض محاولات مسح المنافذ TCP وتطبيق تقنية Tarpit.<br><code>tcp_l4_proxy.py</code></td>
            <td><strong>المدخلات:</strong> حزم اتصالات TCP الخام.<br><strong>المخرجات:</strong> تأخير الماسحات الآلية.</td>
            <td>محاكاة مسح Nmap ومراقبة استهلاك وقت المهاجم.<br><strong>القبول:</strong> احتجاز الاتصال بنجاح.</td>
            <td>A-01<br><span class="badge badge-medium">MEDIUM</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>TCPL4DeceptionProtocol مكتمل ومجرب.</td>
        </tr>
        <tr>
            <td><strong>A-06</strong></td>
            <td>Gateway Pipeline Ingress</td>
            <td>دمج كافة المصنفات في أنبوب وسيط موحد.<br><code>deception_gateway/main.py</code></td>
            <td><strong>المدخلات:</strong> تدفق طلبات HTTP.<br><strong>المخرجات:</strong> خط معالجة انسيابي متزامن.</td>
            <td>اختبار تدفق الطلبات النظيفة والخبيثة المتزامنة.<br><strong>القبول:</strong> معالجة 500 طلب/ثانية بثبات.</td>
            <td>A-01, A-03, A-04<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>بوابة الدخول تعمل على المنفذ 8000.</td>
        </tr>
        <tr>
            <td><strong>A-07</strong></td>
            <td>Threat Scoring Calibration</td>
            <td>معايرة أوزان الهجمات وضمان عدم حدوث إنذارات كاذبة.<br><code>tests/benchmark_gateway.py</code></td>
            <td><strong>المدخلات:</strong> عينات نصوص شرعية معقدة.<br><strong>المخرجات:</strong> مصفوفة أوزان دقيقة.</td>
            <td>تمرير مدخلات مطولة والتأكد من عدم حظر الشرعيين.<br><strong>القبول:</strong> صفر إنذارات كاذبة (Zero FP).</td>
            <td>A-02<br><span class="badge badge-medium">MEDIUM</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>تمت المعايرة بنجاح تام.</td>
        </tr>
    </tbody>
</table>

<!-- PAGE BREAK: SECTION 1 MASTER WBS PART 2 -->
<div class="page-break"></div>

<div class="page-header">
    <span>FASTAPI DECEPTION ARCHITECTURE // ROADMAP & WBS</span>
    <span>SECTION 01: MASTER WORK BREAKDOWN STRUCTURE (TASKS Y-01 TO Y-07 & M-01 TO M-07)</span>
</div>

<h2 class="section-title">01. مصفوفة تفصيل هيكل العمل المتكاملة (Master WBS Matrix — Part 2)</h2>

<h3>ج. مهام يوسف (Yousif — Core Application & Data Engineer)</h3>
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
            <td><strong>Y-01</strong></td>
            <td>PBKDF2-SHA256 Auth Hashing</td>
            <td>تجزئة كلمات المرور بـ 100,000 دورة وتوليد ملح عشوائي.<br><code>auth_service.py</code></td>
            <td><strong>المدخلات:</strong> كلمة المرور النصية.<br><strong>المخرجات:</strong> سلسلة الـ Hash المشفرة.</td>
            <td>فحص كلمات المرور واختبار hmac.compare_digest.<br><strong>القبول:</strong> مقاومة تامة لهجمات التوقيت.</td>
            <td>S-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>مطابق لمواصفات NIST الأمنية بدقة.</td>
        </tr>
        <tr>
            <td><strong>Y-02</strong></td>
            <td>JWT Token Lifecycle Engine</td>
            <td>توليد توكنات JWT مع تضمين الصلاحيات والتوقيع بـ HS256.<br><code>auth_service.py</code></td>
            <td><strong>المدخلات:</strong> بيانات المستخدم وصلاحياته.<br><strong>المخرجات:</strong> توكن JWT مشفر وآمن.</td>
            <td>فك التوكن وتجربة إرسال توكن منتهي الصلاحية.<br><strong>القبول:</strong> رفض التوكنات المتلاعب بها.</td>
            <td>Y-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>توليد والتحقق من التوكنات يعمل بسلاسة.</td>
        </tr>
        <tr>
            <td><strong>Y-03</strong></td>
            <td>Redis Async Session Store</td>
            <td>تطوير مستودع اتصالات Redis غير المتزامن لإدارة الجلسات.<br><code>redis_session_store.py</code></td>
            <td><strong>المدخلات:</strong> معاملات الجلسة والبيانات.<br><strong>المخرجات:</strong> تخزين مؤقت فائق السرعة.</td>
            <td>إجراء عمليات متزامنة وقياس سرعة الاستجابة.<br><strong>القبول:</strong> سرعة استعلام &lt; 1ms.</td>
            <td>S-01<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>يدعم get, set, append_stream.</td>
        </tr>
        <tr>
            <td><strong>Y-04</strong></td>
            <td>PostgreSQL Relational DB</td>
            <td>بناء نموذج مستودع قاعدة البيانات لحفظ المستخدمين والمعاملات.<br><code>relational_db.py</code></td>
            <td><strong>المدخلات:</strong> نماذج السجلات والمعاملات.<br><strong>المخرجات:</strong> استعلامات مهيأة ومجمعة بأمان.</td>
            <td>إجراء الحفظ والبحث باستخدام استعلامات مهيأة.<br><strong>القبول:</strong> حماية 100% من SQLi.</td>
            <td>Y-01<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>مستودع البيانات العلائقي محمي ومكتمل.</td>
        </tr>
        <tr>
            <td><strong>Y-05</strong></td>
            <td>Resilient InMemory Fallback</td>
            <td>تطوير مخزن ذاكرة آمن غير متزامن يحاكي Redis و DB عند غيابهما.<br><code>fallback_inmemory_store.py</code></td>
            <td><strong>المدخلات:</strong> مفاتيح وقيم وسجلات.<br><strong>المخرجات:</strong> استمرارية العمل دون توقف.</td>
            <td>تشغيل التطبيق بدون خادم خارجي والتحقق من الحفظ.<br><strong>القبول:</strong> صفر انهيارات (Zero Crash).</td>
            <td>Y-03<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>مستقر ومستخدم في بيئة الاختبارات.</td>
        </tr>
        <tr>
            <td><strong>Y-06</strong></td>
            <td>Pydantic Schema Validation</td>
            <td>بناء مخططات البيانات الصارمة للتحقق وتطهير المدخلات تلقائياً.<br><code>pydantic_models.py</code></td>
            <td><strong>المدخلات:</strong> كائنات JSON الخام.<br><strong>المخرجات:</strong> كائنات كود نظيفة ومطهرة.</td>
            <td>تمرير حقول ملوثة والتحقق من إرجاع خطأ 422.<br><strong>القبول:</strong> رفض المدخلات غير المطابقة.</td>
            <td>S-06<br><span class="badge badge-medium">MEDIUM</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>نماذج Pydantic v2 منجزة ومعتمدة.</td>
        </tr>
        <tr>
            <td><strong>Y-07</strong></td>
            <td>Core Business Logic API</td>
            <td>تنفيذ واجهات برمجة التطبيقات الأساسية (/profile, /transactions).<br><code>endpoints.py, business_logic.py</code></td>
            <td><strong>المدخلات:</strong> طلبات العملاء الموثقة.<br><strong>المخرجات:</strong> بيانات الأعمال الحقيقية.</td>
            <td>استدعاء المسارات بحسابات مختلفة الصلاحيات.<br><strong>القبول:</strong> إنفاذ سياسة الـ RBAC بدقة.</td>
            <td>Y-02, Y-06<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>مسارات التطبيق تعمل بنجاح 100%.</td>
        </tr>
    </tbody>
</table>

<h3>د. مهام عمار (Ammar — Honeypot, Sandbox & Forensics Engineer)</h3>
<table class="matrix-table" style="margin-top:10px;">
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
            <td><strong>M-01</strong></td>
            <td>HMAC Honey Token Gen</td>
            <td>توليد توكنات وروابط وحقول خفية موقعة بـ HMAC-SHA256.<br><code>token_generator.py</code></td>
            <td><strong>المدخلات:</strong> نوع التوكن والسر المشترك.<br><strong>المخرجات:</strong> توكن خداعي مشفر وموقع.</td>
            <td>توليد التوكن والتحقق من صحة التوقيع عبر verifier.<br><strong>القبول:</strong> كشف محاولات التزوير بنجاح.</td>
            <td>S-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>توليد وفحص التوكنات يعمل بكفاءة.</td>
        </tr>
        <tr>
            <td><strong>M-02</strong></td>
            <td>Honey Token Injector</td>
            <td>حقن التوكنات الخداعية داخل كائنات JSON العائدة للمستخدمين.<br><code>injector_middleware.py</code></td>
            <td><strong>المدخلات:</strong> استجابة Response.<br><strong>المخرجات:</strong> استجابة مدمجة بالوسوم الخداعية.</td>
            <td>طلب استجابة والتأكد من سلامة بنية البيانات الأصلية.<br><strong>القبول:</strong> الحقول مدمجة دون تلف.</td>
            <td>M-01, Y-07<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>البرمجية الوسيطة تحقن الوسوم بدقة.</td>
        </tr>
        <tr>
            <td><strong>M-03</strong></td>
            <td>Prewarmed Pool Manager</td>
            <td>إدارة مجمع الحاويات الجاهزة مسبقاً والتخصيص في أقل من 10ms.<br><code>prewarmed_pool.py</code></td>
            <td><strong>المدخلات:</strong> إشارة عزل من البوابة.<br><strong>المخرجات:</strong> تخصيص فوري لحاوية معزولة.</td>
            <td>قياس زمن تخصيص الحاوية بالمايكروثانية وإعادة الملء.<br><strong>القبول:</strong> زمن الاستجابة &lt; 10ms.</td>
            <td>S-01, S-03<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>إلغاء تام لزمن الإقلاع البارد.</td>
        </tr>
        <tr>
            <td><strong>M-04</strong></td>
            <td>Realistic Decoy Services</td>
            <td>بناء التطبيق التخيلي وقواعد البيانات الوهمية لاستدراج المهاجمين.<br><code>decoy_environment.py</code></td>
            <td><strong>المدخلات:</strong> طلبات المهاجم المعزولة.<br><strong>المخرجات:</strong> نتائج تخيلية واقعية برمز 200.</td>
            <td>تنفيذ هجوم على Decoy والتأكد من عدم تسريب الإنتاج.<br><strong>القبول:</strong> صفر تسريب لبيانات الإنتاج.</td>
            <td>M-03<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>بيئة الخداع تحاكي النظام الأصلي.</td>
        </tr>
        <tr>
            <td><strong>M-05</strong></td>
            <td>Chain of Custody Engine</td>
            <td>هندسة سلسلة الهاش المشفرة للأدلة الرقمية وتطبيق ISO 27037.<br><code>chain_of_custody.py</code></td>
            <td><strong>المدخلات:</strong> حزم البيانات والآثار الرقمية.<br><strong>المخرجات:</strong> كتل مشفرة بهاش تراكمي متصل.</td>
            <td>تعديل محتوى كتلة والتحقق من كشف انكسار السلسلة.<br><strong>القبول:</strong> إثبات رياضي غير قابل للتلاعب.</td>
            <td>S-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>سلسلة العهدة مجازة باختبارات E2E.</td>
        </tr>
        <tr>
            <td><strong>M-06</strong></td>
            <td>DFIR Artifact Extraction</td>
            <td>تسجيل أوامر الشل وتفريغ حمولات الشبكة واستخراج PCAP.<br><code>artifact_collector.py</code></td>
            <td><strong>المدخلات:</strong> نشاط المهاجم داخل الـ Sandbox.<br><strong>المخرجات:</strong> ملفات أدلة جنائية مختومة.</td>
            <td>تنفيذ أوامر داخل الحاوية والتأكد من تسجيلها فوراً.<br><strong>القبول:</strong> استخراج وتوثيق الآثار فورياً.</td>
            <td>M-05<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>المجمع يسجل الأوامر والحزم بدقة.</td>
        </tr>
        <tr>
            <td><strong>M-07</strong></td>
            <td>Real-Time SOC WebSockets</td>
            <td>بث الأحداث السيبرانية وتحديث لوحة المراقبة ومطابقة MITRE.<br><code>websocket_manager.py</code></td>
            <td><strong>المدخلات:</strong> تيار التنبيهات السريع.<br><strong>المخرجات:</strong> تدفق بيانات حي لواجهة الـ SOC.</td>
            <td>فتح اتصال WebSocket وإطلاق تنبيه ومراقبة استلامه.<br><strong>القبول:</strong> زمن وصول التنبيه &lt; 50ms.</td>
            <td>S-04, M-01<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>لوحة الـ SOC تستلم وتبث بنجاح.</td>
        </tr>
    </tbody>
</table>

<!-- PAGE BREAK: SECTION 2 RACI & POLICIES -->
<div class="page-break"></div>

<div class="page-header">
    <span>FASTAPI DECEPTION ARCHITECTURE // ROADMAP & WBS</span>
    <span>SECTION 02 & 03: RACI MATRIX & CODE REVIEW GOVERNANCE</span>
</div>

<h2 class="section-title">02. مصفوفة توزيع المسؤوليات المؤسسية (RACI Governance Matrix)</h2>

<p>
تحدد مصفوفة RACI الأدوار الدقيقة لكل عضو في كل مكون: 
<span class="badge badge-critical">R: Responsible (المنفذ)</span>، 
<span class="badge badge-high">A: Accountable (المسؤول النهائي)</span>، 
<span class="badge badge-medium">C: Consulted (المستشار)</span>، 
<span class="badge badge-info">I: Informed (المُطلع)</span>:
</p>

<table class="data-table">
    <thead>
        <tr>
            <th style="width:36%;">المجال المعماري والبرمجي للمنظومة</th>
            <th style="width:16%;">سجاد (01)</th>
            <th style="width:16%;">علي (02)</th>
            <th style="width:16%;">يوسف (03)</th>
            <th style="width:16%;">عمار (04)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>المعمارية العامة والحدود الأمنية (Architecture & Invariants)</strong></td>
            <td><strong>A / R</strong></td>
            <td>C</td>
            <td>C</td>
            <td>C</td>
        </tr>
        <tr>
            <td><strong>منسق العمليات المتعددة والإغلاق الآمن (Orchestrator)</strong></td>
            <td><strong>A / R</strong></td>
            <td>I</td>
            <td>I</td>
            <td>I</td>
        </tr>
        <tr>
            <td><strong>بوابة الدخول وتصنيف حركة المرور (Ingress Gateway)</strong></td>
            <td>A</td>
            <td><strong>R</strong></td>
            <td>C</td>
            <td>I</td>
        </tr>
        <tr>
            <td><strong>محرك كشف الهجمات الاستدلالية (Heuristic Detection)</strong></td>
            <td>A</td>
            <td><strong>R</strong></td>
            <td>I</td>
            <td>C</td>
        </tr>
        <tr>
            <td><strong>الموجه الشفاف للجلسات المشبوهة (Malicious Session Router)</strong></td>
            <td>A</td>
            <td><strong>R</strong></td>
            <td>I</td>
            <td>C</td>
        </tr>
        <tr>
            <td><strong>تطبيق الأعمال الحقيقي ومسارات الـ REST (Core Web App)</strong></td>
            <td>A</td>
            <td>I</td>
            <td><strong>R</strong></td>
            <td>I</td>
        </tr>
        <tr>
            <td><strong>نظام المصادقة والتشفير بـ PBKDF2 و JWT (Auth Service)</strong></td>
            <td>A</td>
            <td>C</td>
            <td><strong>R</strong></td>
            <td>I</td>
        </tr>
        <tr>
            <td><strong>مخازن البيانات PostgreSQL و Redis و Fallback Store</strong></td>
            <td>A</td>
            <td>C</td>
            <td><strong>R</strong></td>
            <td>C</td>
        </tr>
        <tr>
            <td><strong>حقن التوكنات الخداعية بـ HMAC (Honey Token Injector)</strong></td>
            <td>A</td>
            <td>I</td>
            <td>C</td>
            <td><strong>R</strong></td>
        </tr>
        <tr>
            <td><strong>مجمع الحاويات الدافئة مسبقاً (Prewarmed Sandbox Pool)</strong></td>
            <td>A</td>
            <td>C</td>
            <td>I</td>
            <td><strong>R</strong></td>
        </tr>
        <tr>
            <td><strong>سلسلة العهدة الرقمية المشفرة بـ SHA-256 (Chain of Custody)</strong></td>
            <td>A</td>
            <td>I</td>
            <td>I</td>
            <td><strong>R</strong></td>
        </tr>
        <tr>
            <td><strong>لوحة المراقبة وبث الأحداث الحية (SOC Dashboard & WS)</strong></td>
            <td>A</td>
            <td>I</td>
            <td>I</td>
            <td><strong>R</strong></td>
        </tr>
        <tr>
            <td><strong>حزمة اختبارات التكامل الشاملة (E2E Test Suite)</strong></td>
            <td><strong>A / R</strong></td>
            <td>C</td>
            <td>C</td>
            <td>C</td>
        </tr>
    </tbody>
</table>

<h2 class="section-title" style="margin-top:25px;">03. سياسة إدارة الشيفرة البرمجية والمراجعة (Git & Code Review Policy)</h2>

<div class="callout callout-info">
    <div class="callout-title">إجراءات المراجعة الصارمة (Pull Request Verification):</div>
    1. <strong>الفروع المستقلة (Branching Strategy):</strong> يعمل كل عضو على فرع مستقل بصيغة <code>feature/member-task-name</code>.<br>
    2. <strong>حظر الدمج المباشر:</strong> يمنع نهائياً الدفع المباشر إلى فرع <code>main</code>؛ الدمج يتطلب موافقة معمارية من سجاد حصراً.<br>
    3. <strong>الفحص الآلي (Automated Checks):</strong> يجب أن تجتاز جميع اختبارات <code>pytest</code> بنسبة 100% قبل قبول أي دمج.
</div>

<!-- PAGE BREAK: SECTION 4 & 5 DOD & MILESTONES -->
<div class="page-break"></div>

<div class="page-header">
    <span>FASTAPI DECEPTION ARCHITECTURE // ROADMAP & WBS</span>
    <span>SECTION 04 & 05: DEFINITION OF DONE & DEFENSE COUNTDOWN</span>
</div>

<h2 class="section-title">04. معايير قبول الميزات المكتملة (Definition of Done — DoD)</h2>

<div class="table-container">
    <table class="data-table">
        <thead>
            <tr>
                <th style="width:25%;">المعيار الهندسي</th>
                <th style="width:45%;">شروط التحقق والامتثال الإلزامي</th>
                <th style="width:30%;">أداة الفحص والتحقق</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>جودة وتوثيق الكود (Code Cleanliness)</strong></td>
                <td>كتابة شروحات الدوال (Docstrings)، وتحديد الأنواع بصرامة (Type Hinting)، وخلو الشيفرة من المتغيرات المهملة.</td>
                <td>الفحص البصري ومراجعة Peer-Review.</td>
            </tr>
            <tr>
                <td><strong>التغطية الاختبارية (Test Coverage)</strong></td>
                <td>اجتياز كافة اختبارات الوحدة واختبارات التكامل الشاملة بنسبة نجاح 100% دون أي فشل.</td>
                <td><code>pytest tests/ -v</code> (5/5 Passing).</td>
            </tr>
            <tr>
                <td><strong>الأمان والصلابة (Security Hardening)</strong></td>
                <td>تطهير المدخلات بنماذج Pydantic، وتشفير كلمات المرور بـ PBKDF2، واستخدام توقيع HMAC للتوكنات.</td>
                <td>Static Security Code Audit.</td>
            </tr>
            <tr>
                <td><strong>الأداء والسرعة (Performance SLA)</strong></td>
                <td>تصنيف المرور في أقل من 2ms، تخصيص الحاوية في أقل من 10ms، وبث تنبيهات الـ SOC في أقل من 50ms.</td>
                <td>حزمة قياس الأداء وحساب أزمنة الاستجابة.</td>
            </tr>
        </tbody>
    </table>
</div>

<h2 class="section-title" style="margin-top:25px;">05. الجدول الزمني ومراحل التسليم حتى مناقشة التخرج (Defense Milestones)</h2>

<div class="table-container">
    <table class="data-table">
        <thead>
            <tr>
                <th style="width:15%;">المرحلة والموعد</th>
                <th style="width:30%;">المخرجات والمكتسبات الهندسية</th>
                <th style="width:25%;">المسؤول المباشر</th>
                <th style="width:30%;">الحالة الإنجازية الموثقة</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>المرحلة 1: التأسيس</strong><br><span style="font-size:8pt; color:#64748b;">Foundation & Core</span></td>
                <td>بناء التطبيق الحقيقي، خدمات التوثيق PBKDF2 و JWT، وتأسيس مخازن PostgreSQL و Redis ومخزن الذاكرة.</td>
                <td>يوسف (Core & Data) تحت إشراف سجاد</td>
                <td><span class="badge badge-success">100% مكتمل ومثبت</span><br>تم اختباره واجتيازه بنجاح.</td>
            </tr>
            <tr>
                <td><strong>المرحلة 2: البوابة والخداع</strong><br><span style="font-size:8pt; color:#64748b;">Gateway & Ingress</span></td>
                <td>تطوير محرك تصنيف حركة المرور، كشف الهجمات الاستدلالية، موجه الجلسات المشبوهة، وبروتوكول TCP L4.</td>
                <td>علي (Gateway) بالتنسيق مع يوسف</td>
                <td><span class="badge badge-success">100% مكتمل ومثبت</span><br>البوابة تعمل وتصنف بأقل من 2ms.</td>
            </tr>
            <tr>
                <td><strong>المرحلة 3: العزل والجنائيات</strong><br><span style="font-size:8pt; color:#64748b;">Sandbox & Forensics</span></td>
                <td>حقن التوكنات الخداعية بـ HMAC، مجمع الحاويات الدافئة مسبقاً، وسلسلة العهدة المشفرة بـ SHA-256.</td>
                <td>عمار (Sandbox & DFIR)</td>
                <td><span class="badge badge-success">100% مكتمل ومثبت</span><br>سلسلة العهدة مطابقة لمعيار ISO 27037.</td>
            </tr>
            <tr>
                <td><strong>المرحلة 4: التكامل والمناقشة</strong><br><span style="font-size:8pt; color:#64748b;">Final Hardening & Defense</span></td>
                <td>ربط مسار /search_trap، إنجاز اختبارات E2E الخمسة، وإنشاء حزمة الوثائق الدفاعية السبع بصيغة PDF.</td>
                <td>الفريق بكامله بقيادة سجاد</td>
                <td><span class="badge badge-success">100% جاهز للمناقشة</span><br>جميع الوثائق والاختبارات جاهزة.</td>
            </tr>
        </tbody>
    </table>
</div>

<div class="callout callout-success" style="margin-top:20px;">
    <div class="callout-title">إعلان الجاهزية القصوى لمناقشة التخرج:</div>
    المنظومة الدفاعية <strong>FastAPI Deception Architecture</strong> مكتملة هندسياً وبرمجياً وتنظيمياً بنسبة 100%. الفريق المؤلف من سجاد، علي، يوسف، وعمار يمتلك وضوحاً تاماً في التخصصات والمسؤوليات، ومسلح بالأدلة العلمية والبراهين البرمجية لتقديم مناقشة تخرج استثنائية ونيل الدرجة الكاملة بتفوق واقتدار.
</div>

<div class="doc-footer">
    <span>FASTAPI DECEPTION ARCHITECTURE // MASTER DEVELOPMENT ROADMAP & WBS</span>
    <span>CONFIDENTIAL & CLASSIFIED // GRADUATION THESIS 2026</span>
</div>

</body>
</html>
"""
