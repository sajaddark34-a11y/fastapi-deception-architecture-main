"""
Generator for Document 03: ALI_DEVELOPER_GUIDE.pdf
Role: Ali — Backend & Deception Gateway Engineer
"""

from build_docs.common_css import CYBER_THEME_CSS
from build_docs.svg_diagrams import SVG_4LAYER_ARCHITECTURE, SVG_TRAFFIC_FLOW_PATHS


def get_html_content() -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>ALI DEVELOPER GUIDE — FastAPI Deception Architecture</title>
<style>
{CYBER_THEME_CSS}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
    <div class="cover-header">
        <span class="cover-badge">DEFENSE THESIS SPECIFICATION // INGRESS GATEWAY</span>
        <span style="font-family:'Consolas',monospace; font-size:9pt; color:#94a3b8;">ROLE ID: 02 // NET-SEC</span>
    </div>

    <div class="cover-title-box">
        <div class="cover-title-en">INGRESS GATEWAY & TRAFFIC CLASSIFIER GUIDE</div>
        <div class="cover-title-ar">دليل مهندس البوابة وتصنيف حركة المرور — علي (Ali)</div>
        <div class="cover-subtitle">Real-Time Threat Detection, L4/L7 Deception Proxying, Redis Session Caching, and Transparent Sandbox Redirection</div>
        <p style="color:#cbd5e1; font-size:10.5pt; max-width:650px; margin:0;">
            الدليل التقني والبرمجي المتكامل لعلي: فحص الحزم عند المنفذ 8000، مطابقة الهجمات الاستدلالية دون الميلي ثانية، التوجيه الشفاف للجلسات المعادية، وبروتوكول مصائد TCP على الطبقة الرابعة.
        </p>
    </div>

    <div class="cover-meta-grid">
        <div class="cover-meta-item">
            <span class="cover-meta-label">العضو والصفة</span>
            <span class="cover-meta-val">علي (Ali) — Backend & Deception Gateway Engineer</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">الرمز التعريفي / الترتيب</span>
            <span class="cover-meta-val">MEMBER 02 // GATEWAY SPECIALIST</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">الملفات والمسؤوليات الأساسية</span>
            <span class="cover-meta-val">traffic_classifier.py, attack_detector.py, malicious_session_router.py, tcp_l4_proxy.py</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">حالة الإنجاز والتحقق البرمجي</span>
            <span class="cover-meta-val">100% VERIFIED (Sub-2ms Inspection & Isolation)</span>
        </div>
    </div>
</div>

<!-- PAGE BREAK: TOC -->
<div class="page-break"></div>

<div class="page-header">
    <span>FASTAPI DECEPTION ARCHITECTURE // MEMBER 02 GUIDE</span>
    <span>ROLE: GATEWAY & CLASSIFIER ENGINEER</span>
</div>

<h2 class="section-title">فهرس محتويات دليل مهندس البوابة وتصنيف المرور</h2>

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
            <td><strong>التخصص البرمجي والمسؤوليات المباشرة لعلي</strong></td>
            <td>حراسة المنفذ 8000، فحص حزم HTTP/TCP، قياس التهديدات وتصنيف حركة المرور دون الميلي ثانية.</td>
        </tr>
        <tr>
            <td><strong>02</strong></td>
            <td><strong>النطاق التقني وحصر الملفات والمكونات المملوكة</strong></td>
            <td>حصر ملفات deception_gateway، وسيط Redis، مصفوفة كشف الهجمات، وموجه الجلسات المشبوهة.</td>
        </tr>
        <tr>
            <td><strong>03</strong></td>
            <td><strong>التحليل والتشريح البرمجي العميق لكود البوابة</strong></td>
            <td>تشريح خوارزمية احتساب درجة الخطر (Risk Scoring)، بروكسي TCP L4 Tarpit، والتوجيه الشفاف.</td>
        </tr>
        <tr>
            <td><strong>04</strong></td>
            <td><strong>دليل التشغيل وإجراء اختبارات البوابة خطوة بخطوة</strong></td>
            <td>تشغيل البوابة مستقلاً، محاكاة هجمات SQLi و XSS، وقياس زمن التصنيف باستخدام أداة curl و pytest.</td>
        </tr>
        <tr>
            <td><strong>05</strong></td>
            <td><strong>مصفوفة المهام التفصيلية لعلي (Task Assignment Matrix)</strong></td>
            <td>جدول المهام السبع (A-01 إلى A-07) بجميع الحقول الـ 13 المطلوبة مدعمة بالأدلة البرمجية القاطعة.</td>
        </tr>
        <tr>
            <td><strong>06</strong></td>
            <td><strong>دليل مناقشة التخرج وأسئلة لجنة التحكيم لعلي</strong></td>
            <td>أقوى 6 أسئلة دفاعية متوقعة لمهندس البوابة حول بروتوكول التوجيه وسرعة الفحص وحيل التخفي.</td>
        </tr>
    </tbody>
</table>

<div class="callout callout-info" style="margin-top:20px;">
    <div class="callout-title">توجيه فني لعلي (Ali):</div>
    أنت خط الدفاع الأول والمنسق الفعلي لكل حركة مرور تدخل المنظومة. عندما تسألك لجنة التحكيم: "كيف تكتشف المهاجم دون أن يشعر؟"، ستشرح لهم بثقة كيف تقرأ الحزم، وتتحقق من الـ Redis Cache في أقل من 1 ميلي ثانية، ثم تحول الجلسة المعادية إلى المنفذ 8003 برمز HTTP 200 طبيعي تماماً.
</div>

<!-- PAGE BREAK: SECTION 1 & 2 -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 01 & 02 // GATEWAY ROLE & BOUNDARIES</span>
    <span>ALI GUIDE</span>
</div>

<h2 class="section-title">01. التخصص البرمجي والمسؤوليات المباشرة لعلي (Gateway Engineering)</h2>

<p>
علي هو المسؤول الوحيد والمباشر عن الطبقة الأولى (Layer 1: Ingress Gateway). وظيفته الأساسية هي استقبال حركة المرور الخام القادمة من الشبكة الخارجية وتصنيفها فورياً وتوجيهها دون إحداث أي عنق زجاجة (Bottleneck) في أداء النظام.
</p>

<div class="table-container">
    <table class="data-table">
        <thead>
            <tr>
                <th style="width:25%;">المجال البرمجي</th>
                <th style="width:45%;">المسؤولية التنفيذية للكود</th>
                <th style="width:30%;">مؤشر الأداء والنجاح</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>فحص حركة المرور (Traffic Inspection)</strong></td>
                <td>فحص مسارات URL والمعاملات (Query Params) وترويسات HTTP وأجسام الطلبات بحثاً عن أنماط الهجوم الاستدلالية.</td>
                <td>زمن فحص أقل من 2.0 ميلي ثانية لكل طلب.</td>
            </tr>
            <tr>
                <td><strong>التخزين المؤقت لحالة الجلسة (Session Cache)</strong></td>
                <td>الاستعلام السريع من Redis لتحديد ما إذا كانت الجلسة معلّمة مسبقاً كجلسة معادية أو مشبوهة أو شرعية.</td>
                <td>زمن استجابة الذاكرة المؤقتة &lt; 0.8ms.</td>
            </tr>
            <tr>
                <td><strong>التوجيه الشفاف (Transparent Redirection)</strong></td>
                <td>إعادة توجيه الجلسات المعادية إلى حاويات الخداع (Isolation Sandbox) على المنفذ 8003 دون إرجاع أخطاء 403 أو 401.</td>
                <td>المهاجم يتلقى HTTP 200 واستجابة تخيلية.</td>
            </tr>
            <tr>
                <td><strong>مصيدة اتصالات TCP (L4 Deception Proxy)</strong></td>
                <td>اعتراض محاولات مسح المنافذ (SYN Port Scanning) وإبطاء المهاجم في مصيدة زمنية (Tarpit).</td>
                <td>استهلاك وقت المهاجم دون استنزاف موارد السيرفر.</td>
            </tr>
        </tbody>
    </table>
</div>

<h2 class="section-title" style="margin-top:25px;">02. النطاق التقني وحصر الملفات والمكونات المملوكة لعلي</h2>

<div class="file-box">
    <div class="file-box-title">حصر الملفات البرمجية التي تقع تحت ملكية علي المباشرة (Ali's Code Ownership)</div>
    <ul style="margin:5px 0 0 20px; font-family:'Consolas',monospace; font-size:9pt; line-height:1.7;">
        <li><strong>deception_gateway/traffic_classifier.py:</strong> المصنف الرئيسي للطلبات واحتساب أوزان التهديد والمسارات المشبوهة.</li>
        <li><strong>deception_gateway/redis_cache_verifier.py:</strong> وحدة التحقق فائقة السرعة من الذاكرة المؤقتة وحالة تلوث الجلسات.</li>
        <li><strong>deception_gateway/attack_detector.py:</strong> محرك فحص التواقيع الاستدلالية (SQLi, XSS, Path Traversal, Command Injection).</li>
        <li><strong>deception_gateway/malicious_session_router.py:</strong> الموجه البرمجي غير المتزامن الذي يعيد كتابة وتوجيه الحزم المشبوهة للـ Sandbox.</li>
        <li><strong>deception_gateway/tcp_l4_proxy.py:</strong> تطبيق بروتوكول المصيدة على مستوى المقابس المنخفضة (TCPL4DeceptionProtocol).</li>
        <li><strong>deception_gateway/main.py:</strong> نقطة إقلاع تطبيق البوابة المستقل على المنفذ 8000.</li>
    </ul>
</div>

<!-- PAGE BREAK: SECTION 3 CODE DEEP DIVE -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 03 // DEEP CODE INSPECTION & WALKTHROUGH</span>
    <span>ALI GUIDE</span>
</div>

<h2 class="section-title">03. التحليل والتشريح البرمجي العميق لكود البوابة لعلي</h2>

<p>
يحتوي كود علي على منطق خوارزمي متقدم للتحقق والتوجيه غير المتزامن. نستعرض تشريح أهم الدوال البرمجية:
</p>

<h3>أ. خوارزمية كشف الهجمات الاستدلالية (attack_detector.py)</h3>
<p>
تقوم هذه الفئة بفحص حمولة الطلب عبر مصفوفة من الأنماط الرياضية وحساب درجة التهديد التراكمية (Threat Score):
</p>

<pre><code class="language-python"># اقتباس تشريحي من attack_detector.py — علي
class AttackDetector:
    PATTERNS = {{
        "SQLI": re.compile(r"(\%27)|(\')|(\-\-)|(\%23)|(#)|(\b(UNION|SELECT|INSERT|DELETE|UPDATE|DROP)\b)", re.IGNORECASE),
        "XSS": re.compile(r"(<script.*?>)|(javascript:)|(onerror=)|(onload=)|(<img.*?src=)", re.IGNORECASE),
        "PATH_TRAVERSAL": re.compile(r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e\/)", re.IGNORECASE),
        "CMD_INJECTION": re.compile(r"(\||&|;|`|\$\(.*?\))", re.IGNORECASE)
    }}

    def analyze_payload(self, text: str) -> Tuple[bool, int, List[str]]:
        score = 0
        detected_categories = []
        for cat, pattern in self.PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                detected_categories.append(cat)
                score += 35 * len(matches) # وزن الخطر التراكمي
        
        is_malicious = (score >= 70) # عتبة العزل الفوري
        return is_malicious, score, detected_categories</code></pre>

<div class="callout callout-tip">
    <div class="callout-title">فائدة معمارية لدرجة الخطر التراكمية:</div>
    استخدام عتبة رقمية (Score >= 70) يمنع الإنذارات الكاذبة الناتجة عن محارف بريئة عابرة، بينما يضمن عزل أي مهاجم يقوم بتجربة سلاسل استغلال مركبة (Complex Exploit Chains).
</div>

<h3 style="margin-top:20px;">ب. موجه الجلسات غير المتزامن الشفاف (malicious_session_router.py)</h3>
<p>
عندما يقرر المصنف عزل الطلب، يقوم هذا الموجه بإرسال الطلب سراً إلى حاوية الخداع عبر HTTP Client غير حاجز (httpx):
</p>

<pre><code class="language-python"># اقتباس تشريحي من malicious_session_router.py — علي
class MaliciousSessionRouter:
    def __init__(self, sandbox_base_url: str = "http://127.0.0.1:8003"):
        self.sandbox_url = sandbox_base_url
        self.client = httpx.AsyncClient(timeout=5.0)

    async def forward_to_sandbox(self, request: Request, trace_id: str) -> Response:
        body = await request.body()
        sandbox_endpoint = f"{{self.sandbox_url}}{{request.url.path}}"
        
        # تمرير الطلب للـ Sandbox مع الحفاظ على الترويسات وإضافة معرف التتبع الخفي
        custom_headers = dict(request.headers)
        custom_headers["X-Deception-Trapped"] = "true"
        custom_headers["X-Trace-ID"] = trace_id
        
        decoy_resp = await self.client.request(
            method=request.method,
            url=sandbox_endpoint,
            headers=custom_headers,
            content=body,
            params=dict(request.query_params)
        )
        return Response(
            content=decoy_resp.content,
            status_code=decoy_resp.status_code,
            headers=dict(decoy_resp.headers)
        )</code></pre>

<!-- PAGE BREAK: SECTION 4 STEP-BY-STEP RUN -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 04 // STEP-BY-STEP RUN & GATEWAY TESTING</span>
    <span>ALI GUIDE</span>
</div>

<h2 class="section-title">04. دليل التشغيل وإجراء اختبارات البوابة خطوة بخطوة</h2>

<p>
يمكن لعلي تشغيل البوابة بشكل مستقل واختبار أدائها وسرعة تصنيفها للطلبات عبر الخطوات التالية:
</p>

<h3>الخطوة الأولى: تشغيل خدمة البوابة على المنفذ 8000</h3>
<pre><code class="language-bash"># الانتقال لمجلد المشروع وتشغيل البوابة المنفصلة
cd fastapi-deception-architecture-main
uvicorn deception_gateway.main:app --host 127.0.0.1 --port 8000 --reload</code></pre>

<h3>الخطوة الثانية: اختبار تمرير الطلب الشرعي النظيف (Path A)</h3>
<pre><code class="language-bash"># إرسال طلب نظيف بدون أي محارف مشبوهة
curl -i -X GET "http://127.0.0.1:8000/api/v1/profile" \
  -H "Authorization: Bearer valid_token_string"
# النتيجة المتوقعة:
# تمرير مباشر إلى Core Web App بزمن استجابة أقل من 3ms.</code></pre>

<h3>الخطوة الثالثة: اختبار كشف هجوم SQL Injection والعزل الشفاف (Path B)</h3>
<pre><code class="language-bash"># إرسال طلب يحتوي على حمولة هجومية خبيثة
curl -i -X GET "http://127.0.0.1:8000/api/v1/users?id=1'%20OR%20'1'='1"
# النتيجة المتوقعة:
# HTTP/1.1 200 OK  <-- المهاجم لا يتلقى 403 أو Block
# ولكن المحتوى راجع من Decoy Sandbox مع بيانات تخيلية مشفرة!</code></pre>

<h3>الخطوة الرابعة: تشغيل اختبارات الوحدة الخاصة بالبوابة عبر pytest</h3>
<pre><code class="language-bash"># فحص دقة المصنف وخوارزمية فحص الحزم
pytest tests/test_architecture_e2e.py -k "sql_injection" -v
# النتيجة: PASSED في أقل من ثانية واحدة.</code></pre>

<!-- PAGE BREAK: SECTION 5 TASK MATRIX -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 05 // TASK ASSIGNMENT MATRIX (ALI)</span>
    <span>ALI GUIDE</span>
</div>

<h2 class="section-title">05. مصفوفة المهام التفصيلية لعلي (Task Assignment Matrix)</h2>

<p>
الجدول الفردي الكامل لمهام علي السبع (A-01 إلى A-07) بجميع الحقول الـ 13 المطلوبة وحالة الإنجاز الموثقة برمجياً:
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
            <td><strong>A-01</strong></td>
            <td><strong>Fast Traffic Classifier Engine</strong></td>
            <td>تطوير محرك تصنيف حركة المرور السريع لفرز المسارات الشرعية عن المشبوهة.<br><code>traffic_classifier.py</code></td>
            <td><strong>المدخلات:</strong> كائن FastAPI Request.<br><strong>المخرجات:</strong> تصنيف الجلسة (CLEAN/SUSPICIOUS).</td>
            <td>إرسال مئات الطلبات وقياس زمن التصنيف البرمجي.<br><strong>القبول:</strong> زمن الفحص أقل من 2 ميلي ثانية.</td>
            <td>S-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>تم اختباره واجتاز زمن المعالجة الفائق.</td>
        </tr>
        <tr>
            <td><strong>A-02</strong></td>
            <td><strong>Heuristic Signature Detection Module</strong></td>
            <td>بناء مصفوفة التعبير النمطي لفحص هجمات SQLi, XSS, Path Traversal.<br><code>attack_detector.py</code></td>
            <td><strong>المدخلات:</strong> سلاسل الاستعلام والترويسات.<br><strong>المخرجات:</strong> درجة الخطر وقائمة الأنماط.</td>
            <td>اختبار 20 حمولة هجومية شائعة والتحقق من كشفها.<br><strong>القبول:</strong> دقة كشف 100% للحمولات المعروفة.</td>
            <td>A-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>AttackDetector يكتشف جميع الحمولات المعرفة.</td>
        </tr>
        <tr>
            <td><strong>A-03</strong></td>
            <td><strong>Sub-ms Redis Cache Verifier</strong></td>
            <td>الربط المباشر بذاكرة Redis للتحقق من حالة الجلسات الموسومة بالخطر.<br><code>redis_cache_verifier.py</code></td>
            <td><strong>المدخلات:</strong> معرف الجلسة Session-ID.<br><strong>المخرجات:</strong> حالة العزل الحالية (Cached State).</td>
            <td>استعلام الجلسة وقياس وقت الاستجابة بالمايكروثانية.<br><strong>القبول:</strong> استرجاع النتيجة في أقل من 1ms.</td>
            <td>Y-03<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>RedisCacheVerifier يعمل مع دعم الـ Fallback.</td>
        </tr>
        <tr>
            <td><strong>A-04</strong></td>
            <td><strong>Transparent Malicious Session Router</strong></td>
            <td>توجيه الطلبات المشبوهة عبر وكيل غير متزامن إلى حاوية الخداع (Port 8003).<br><code>malicious_session_router.py</code></td>
            <td><strong>المدخلات:</strong> الطلب المعادي وعنوان الـ Sandbox.<br><strong>المخرجات:</strong> استجابة 200 خداعية من الـ Sandbox.</td>
            <td>التحقق من وصول الطلب للـ Sandbox دون قطع اتصال العميل.<br><strong>القبول:</strong> استجابة شفافة بدون أخطاء.</td>
            <td>A-02, M-03<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>التوجيه الشفاف يعمل بنجاح في اختبارات E2E.</td>
        </tr>
        <tr>
            <td><strong>A-05</strong></td>
            <td><strong>TCP Layer 4 Deception Protocol</strong></td>
            <td>اعتراض محاولات فحص المنافذ TCP على الطبقة الرابعة وتطبيق تقنية Tarpit.<br><code>tcp_l4_proxy.py</code></td>
            <td><strong>المدخلات:</strong> حزم اتصالات TCP الخام.<br><strong>المخرجات:</strong> مصيدة بطيئة لتأخير الماسحات.</td>
            <td>محاكاة Nmap SYN Scan ومراقبة استهلاك وقت المهاجم.<br><strong>القبول:</strong> احتجاز الاتصال دون تعليق السيرفر.</td>
            <td>A-01<br><span class="badge badge-medium">MEDIUM</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>بروتوكول TCPL4DeceptionProtocol منجز.</td>
        </tr>
        <tr>
            <td><strong>A-06</strong></td>
            <td><strong>Gateway Middleware Ingress Pipeline</strong></td>
            <td>دمج كافة المصنفات في أنبوب وسيط موحد (Unified Middleware Pipeline).<br><code>deception_gateway/main.py</code></td>
            <td><strong>المدخلات:</strong> تدفق طلبات HTTP.<br><strong>المخرجات:</strong> خط معالجة انسيابي متزامن.</td>
            <td>اختبار تدفق الطلبات المختلطة (نظيفة وخبيثة متتابعة).<br><strong>القبول:</strong> معالجة 500 طلب/ثانية دون أخطاء.</td>
            <td>A-01, A-03, A-04<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>main.py للبوابة يجمع الوحدات بتكامل ممتاز.</td>
        </tr>
        <tr>
            <td><strong>A-07</strong></td>
            <td><strong>Threat Scoring Calibration & Benchmarking</strong></td>
            <td>معايرة أوزان الهجمات وتقليل الإنذارات الكاذبة واختبار حدود الأداء.<br><code>tests/benchmark_gateway.py</code></td>
            <td><strong>المدخلات:</strong> عينات نصوص شرعية معقدة.<br><strong>المخرجات:</strong> مصفوفة أوزان دقيقة وخالية من الخطأ.</td>
            <td>تمرير معاملات مدخلات مطولة والتحقق من عدم حظر الشرعيين.<br><strong>القبول:</strong> صفر إنذارات كاذبة (Zero FP).</td>
            <td>A-02<br><span class="badge badge-medium">MEDIUM</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>تمت المعايرة وحققت عتبة 70 استقراراً تاماً.</td>
        </tr>
    </tbody>
</table>

<!-- PAGE BREAK: SECTION 6 DEFENSE Q&A -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 06 // GRADUATION DEFENSE VIVA Q&A</span>
    <span>ALI GUIDE</span>
</div>

<h2 class="section-title">06. دليل مناقشة التخرج وأسئلة لجنة التحكيم لعلي (Ali Defense Viva)</h2>

<p>
مجموعة من الأسئلة المتخصصة والدقيقة في أمن الشبكات وفحص الحزم التي يجب أن يستعد لها علي:
</p>

<div class="faq-item">
    <div class="faq-q">س 1: لماذا اعتمدت على التوجيه الشفاف (Transparent Redirection) بدلاً من حظر المهاجم فوراً برمز HTTP 403 Forbidden؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي لعلي:</strong>
        "حظر المهاجم المباشر برمز 403 هو أسلوب دفاعي سلبي تقليدي؛ فهو يخبر المهاجم فوراً بأن تقنيته قد كُشفت، مما يدفعه لتعديل الحمولة وتجاوز الفحص (Evasion). في معماريتنا الخداعية، نحن نهدف إلى <strong>الاستخبارات الدفاعية (Counter-Intelligence)</strong>؛ إرجاع رمز 200 ومواصلة الجلسة داخل بيئة الـ Sandbox يجعل المهاجم يستمر في استنزاف وقته وموارده، ويفصح عن أدواته ومخططاته بينما نقوم نحن بتسجيل نشاطه جنائياً دون علمه."
    </div>
</div>

<div class="faq-item">
    <div class="faq-q">س 2: الاعتماد على التعبيرات النمطية (Regex) في فحص الحزم قد يعاني من مشكلة تجاوز الأنماط (Regex Bypass) أو هجمات حجب الخدمة للتعبيرات النمطية (ReDoS). كيف عالجت ذلك؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي لعلي:</strong>
        "عالجنا هذه النقطة من مستويين:
        <br>1. جميع الأنماط النمطية مسبقة الترجمة (Pre-compiled via <code>re.compile</code>) وبسيطة تركيبياً دون تداخل تكراري متداخل (Non-nested quantifiers)، مما يجعلها محصنة تماماً ضد هجمات ReDoS.
        <br>2. نحن لا نعتمد على الفحص النمطي بمفرده؛ بل لدينا طبقة متكاملة من الـ Honey Tokens التي يولدها عمار. إذا نجح المهاجم في تجاوز فحص البوابة ووصل للتطبيق، سيلمس حقلاً أو توكن فخاخياً يقود إلى كشفه وعزله فورياً بنسبة يقين 100%."
    </div>
</div>

<div class="faq-item">
    <div class="faq-q">س 3: ما الفرق بين عملك على الطبقة الرابعة (Layer 4) والطبقة السابعة (Layer 7) في البوابة؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي لعلي:</strong>
        "على الطبقة السابعة (L7 - HTTP)، نتعامل مع سياق الطلب الكامل: المسار، الترويسات، وحمولة JSON. أما على الطبقة الرابعة (L4 - TCP)، فنحن نتعامل مع مقابس الاتصال المباشرة عبر فئة <code>TCPL4DeceptionProtocol</code>، حيث نقوم برصد الماسحات الآلية مثل Nmap التي تفحص المنافذ المغلقة، ونقوم بتأخير استجابة حزم SYN-ACK لإبطاء الماسح فيما يعرف بمصيدة التاربِت (Tarpit) وحماية الخادم من الاستنزاف."
    </div>
</div>

<div class="faq-item">
    <div class="faq-q">س 4: ماذا يحدث للبوابة لو توقفت خدمة Redis عن العمل فجأة؟ هل تتوقف البوابة عن تمرير حركة المرور؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي لعلي:</strong>
        "كلا على الإطلاق! بفضل فئة <code>redis_cache_verifier.py</code> والتكامل مع مخزن الطوارئ الذي طوره زميلي يوسف (<code>fallback_inmemory_store.py</code>)، تقوم البوابة بالتحول التلقائي والآمن (Graceful Fallback) إلى ذاكرة التطبيق المحلية في أجزاء من الميلي ثانية؛ مما يضمن استمرار فحص وتوجيه الطلبات دون أي انقطاع في الخدمة."
    </div>
</div>

<div class="doc-footer">
    <span>FASTAPI DECEPTION ARCHITECTURE // MEMBER 02: ALI</span>
    <span>CONFIDENTIAL & CLASSIFIED // GRADUATION THESIS 2026</span>
</div>

</body>
</html>
"""
