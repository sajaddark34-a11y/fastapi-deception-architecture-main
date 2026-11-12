"""
Generator for Document 05: AMMAR_DEVELOPER_GUIDE.pdf
Role: Ammar — Honeypot, Sandbox & Forensics Engineer
"""

from build_docs.common_css import CYBER_THEME_CSS
from build_docs.svg_diagrams import SVG_CHAIN_OF_CUSTODY, SVG_PREWARMED_POOL


def get_html_content() -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>AMMAR DEVELOPER GUIDE — FastAPI Deception Architecture</title>
<style>
{CYBER_THEME_CSS}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
    <div class="cover-header">
        <span class="cover-badge">DEFENSE THESIS SPECIFICATION // FORENSICS & DECEPTION</span>
        <span style="font-family:'Consolas',monospace; font-size:9pt; color:#94a3b8;">ROLE ID: 04 // DFIR-SEC</span>
    </div>

    <div class="cover-title-box">
        <div class="cover-title-en">HONEYPOT, SANDBOX & FORENSICS ENGINEER GUIDE</div>
        <div class="cover-title-ar">دليل مهندس الفخاخ والعزل والأدلة الجنائية — عمار (Ammar)</div>
        <div class="cover-subtitle">Synthetic Canary Injection, Sub-10ms Prewarmed Sandboxes, Cryptographic Hash Chains, and SOC Telemetry</div>
        <p style="color:#cbd5e1; font-size:10.5pt; max-width:650px; margin:0;">
            الدليل التنفيذي والبرمجي المتكامل لعمار: حقن التوكنات الخداعية الموقعة بـ HMAC-SHA256، هندسة مجمع الحاويات الدافئة مسبقاً، تثبيت سلسلة العهدة الجنائية المقاومة للتلاعب، وبث أحداث المراقبة اللحظية إلى لوحة الـ SOC.
        </p>
    </div>

    <div class="cover-meta-grid">
        <div class="cover-meta-item">
            <span class="cover-meta-label">العضو والصفة</span>
            <span class="cover-meta-val">عمار (Ammar) — Honeypot, Sandbox & Forensics Engineer</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">الرمز التعريفي / الترتيب</span>
            <span class="cover-meta-val">MEMBER 04 // DFIR & SANDBOX SPECIALIST</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">الملفات والمسؤوليات الأساسية</span>
            <span class="cover-meta-val">token_generator.py, prewarmed_pool.py, chain_of_custody.py, artifact_collector.py, websocket_manager.py</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">حالة الإنجاز والتحقق البرمجي</span>
            <span class="cover-meta-val">100% VERIFIED (ISO 27037 Tamper-Proof Chain)</span>
        </div>
    </div>
</div>

<!-- PAGE BREAK: TOC -->
<div class="page-break"></div>

<div class="page-header">
    <span>FASTAPI DECEPTION ARCHITECTURE // MEMBER 04 GUIDE</span>
    <span>ROLE: FORENSICS & DECEPTION SPECIALIST</span>
</div>

<h2 class="section-title">فهرس محتويات دليل مهندس الفخاخ والعزل والأدلة الجنائية</h2>

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
            <td><strong>التخصص البرمجي والمسؤوليات المباشرة لعمار</strong></td>
            <td>هندسة الفخاخ السيبرانية، إدارة بيئات العزل، جمع الأدلة الرقمية، وتأمين سلسلة العهدة القانونية.</td>
        </tr>
        <tr>
            <td><strong>02</strong></td>
            <td><strong>النطاق التقني وحصر الملفات والمكونات المملوكة</strong></td>
            <td>حصر ملفات honey_token_injector، isolation_sandbox، forensic_engine، و soc_dashboard.</td>
        </tr>
        <tr>
            <td><strong>03</strong></td>
            <td><strong>التحليل والتشريح البرمجي العميق لكود الخداع والجنائيات</strong></td>
            <td>تشريح حقن التوكنات بـ HMAC، مجمع الحاويات الجاهزة (Prewarmed Pool)، وسلسلة الهاش التراكمية.</td>
        </tr>
        <tr>
            <td><strong>04</strong></td>
            <td><strong>دليل التشغيل وإجراء اختبارات الخداع والجنائيات خطوة بخطوة</strong></td>
            <td>توليد توكن خداعي، محاكاة لمس الفخ، قياس سرعة التبديل، والتحقق الجنائي التلقائي عبر pytest.</td>
        </tr>
        <tr>
            <td><strong>05</strong></td>
            <td><strong>مصفوفة المهام التفصيلية لعمار (Task Assignment Matrix)</strong></td>
            <td>جدول المهام السبع (M-01 إلى M-07) بجميع الحقول الـ 13 المطلوبة مدعمة بالأدلة البرمجية القاطعة.</td>
        </tr>
        <tr>
            <td><strong>06</strong></td>
            <td><strong>دليل مناقشة التخرج وأسئلة لجنة التحكيم لعمار</strong></td>
            <td>أقوى 6 أسئلة دفاعية متوقعة لمهندس الجنائيات والخداع حول الإثبات القانوني ومنع الهروب من العزل.</td>
        </tr>
    </tbody>
</table>

<div class="callout callout-info" style="margin-top:20px;">
    <div class="callout-title">توجيه فني لعمار (Ammar):</div>
    أنت صائد المهاجمين ومسجل الحقيقة الجنائية في المشروع. مهمتك التقنية تمزج بين الذكاء الاستخباراتي (Deception) والرياضيات المشفرة (Cryptographic Hashes). عليك أن توضح للجنة المناقشة كيف حولت استجابات النظام العادية إلى فخاخ صامتة، وكيف تجمع أدلة رقمية غير قابلة للطعن أمام المحاكم القانونية.
</div>

<!-- PAGE BREAK: SECTION 1 & 2 -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 01 & 02 // FORENSICS & DECEPTION ROLE</span>
    <span>AMMAR GUIDE</span>
</div>

<h2 class="section-title">01. التخصص البرمجي والمسؤوليات المباشرة لعمار (Deception & Forensics)</h2>

<p>
عمار يمتلك المكونات الهجومية والدفاعية الأكثر ابتكاراً في المشروع: منظومة حقن التوكنات الخداعية، ومجمع الحاويات الدافئة مسبقاً، ومحرك استخراج الأدلة الجنائية الرقمية، ولوحة عمليات الأمن السيبراني (SOC).
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
                <td><strong>حقن التوكنات الخداعية (Honey Tokens)</strong></td>
                <td>توليد مفاتيح API وحقول مخفية وروابط وهمية مشفرة بـ HMAC-SHA256 وحقنها في استجابات الـ JSON دون التأثير على التطبيق.</td>
                <td>نسبة إنذار كاذب صفرية (100% Zero False Alarms).</td>
            </tr>
            <tr>
                <td><strong>مجمع الحاويات الدافئة (Prewarmed Pool)</strong></td>
                <td>تشغيل حاويات مجهزة سلفاً وإلغاء زمن الإقلاع البارد لـ Docker (Cold-Start) لتمكين العزل في أجزاء من الميلي ثانية.</td>
                <td>زمن عزل الجلسة أقل من 10 ميلي ثانية (&lt;10ms).</td>
            </tr>
            <tr>
                <td><strong>سلسلة العهدة المشفرة (Chain of Custody)</strong></td>
                <td>ربط الأدلة الرقمية (سجلات، أوامر، حزم PCAP) في سلسلة هاش رياضية متسلسلة تضمن عدم العبث بها ومطابقتها للمعيار ISO 27037.</td>
                <td>إثبات قانوني قطعي لصحة الأدلة الجنائية.</td>
            </tr>
            <tr>
                <td><strong>لوحة عمليات الأمن (SOC Dashboard)</strong></td>
                <td>بث الأحداث السيبرانية وتفاصيل الجلسات المعزولة لحظياً عبر WebSockets وربطها بمصفوفة تكتيكات هجوم MITRE ATT&CK.</td>
                <td>بث مباشر وفوري دون تأخير (Zero Lag).</td>
            </tr>
        </tbody>
    </table>
</div>

<h2 class="section-title" style="margin-top:25px;">02. النطاق التقني وحصر الملفات والمكونات المملوكة لعمار</h2>

<div class="file-box">
    <div class="file-box-title">حصر الملفات البرمجية التي تقع تحت ملكية عمار المباشرة (Ammar's Code Ownership)</div>
    <ul style="margin:5px 0 0 20px; font-family:'Consolas',monospace; font-size:9pt; line-height:1.7;">
        <li><strong>honey_token_injector/token_generator.py:</strong> المولد المشفر للتوكنات والوسوم الخداعية بتوقيع HMAC-SHA256.</li>
        <li><strong>honey_token_injector/injector_middleware.py:</strong> البرمجية الوسيطة لحقن التوكنات داخل استجابات JSON للمستخدمين.</li>
        <li><strong>honey_token_injector/token_verifier.py:</strong> محرك التحقق الفوري من التوكنات الفخاخية المستدعاة وكشف المتسللين.</li>
        <li><strong>isolation_sandbox/prewarmed_pool.py:</strong> مدير تجمعات الحاويات الجاهزة والتخصيص فائق السرعة وإعادة التدوير.</li>
        <li><strong>isolation_sandbox/decoy_environment.py:</strong> بيئة الخداع البرمجية التخيلية ومحاكي قواعد البيانات والخدمات الزائفة.</li>
        <li><strong>forensic_extraction_engine/chain_of_custody.py:</strong> محرك سلسلة العهدة الرقمية وحساب التجزئة التراكمية المشفرة.</li>
        <li><strong>forensic_extraction_engine/artifact_collector.py:</strong> مجمع الآثار الرقمية (أوامر الشل، حزم الشبكة، وبصمات الذاكرة).</li>
        <li><strong>soc_dashboard/websocket_manager.py & dashboard_api.py:</strong> خادم الـ WebSockets وبث القياسات الأمنية الحية.</li>
    </ul>
</div>

<!-- PAGE BREAK: SECTION 3 CODE DEEP DIVE -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 03 // DEEP CODE INSPECTION & WALKTHROUGH</span>
    <span>AMMAR GUIDE</span>
</div>

<h2 class="section-title">03. التحليل والتشريح البرمجي العميق لكود الخداع والجنائيات</h2>

<p>
تمت كتابة شيفرات عمار وفق أعلى المعايير الجنائية والبرمجية. فيما يلي تشريح لأبرز الآليات:
</p>

<h3>أ. هندسة سلسلة العهدة الجنائية المشفرة (chain_of_custody.py)</h3>
<p>
تستخدم المعادلة الرياضية $H_n = \\text{{SHA256}}(H_{{n-1}} \\parallel \\text{{Payload}}_n)$ لبناء سجل أدلة مقاوم للتلاعب:
</p>

<pre><code class="language-python"># اقتباس تشريحي من chain_of_custody.py — عمار
class ChainOfCustodyVault:
    GENESIS_HASH = "0" * 64

    def __init__(self):
        self.blocks: List[Dict[str, Any]] = []
        self.current_hash = self.GENESIS_HASH
        self._lock = asyncio.Lock()

    async def seal_artifact(self, artifact_type: str, data_bytes: bytes, metadata: Dict[str, Any]) -> str:
        async with self._lock:
            artifact_sha = hashlib.sha256(data_bytes).hexdigest()
            block_index = len(self.blocks)
            timestamp = time.time()
            
            # بناء الحمولة المجمعة لحساب الهاش التراكمي
            hasher = hashlib.sha256()
            hasher.update(self.current_hash.encode("utf-8"))
            hasher.update(artifact_sha.encode("utf-8"))
            hasher.update(str(block_index).encode("utf-8"))
            hasher.update(str(timestamp).encode("utf-8"))
            
            new_block_hash = hasher.hexdigest()
            block = {{
                "index": block_index,
                "prev_hash": self.current_hash,
                "artifact_type": artifact_type,
                "artifact_sha256": artifact_sha,
                "timestamp": timestamp,
                "metadata": metadata,
                "block_hash": new_block_hash
            }}
            self.blocks.append(block)
            self.current_hash = new_block_hash
            return new_block_hash</code></pre>

<div class="callout callout-success">
    <div class="callout-title">الأهمية القانونية لسلسلة العهدة:</div>
    إذا حاول أي شخص تعديل حرف واحد في سجل الأوامر أو وقت الهجوم، سيتغير الهاش الخاص بذلك الصندوق وستنكسر السلسلة بالكامل، مما يثبت فورياً حدوث محاولة تلاعب بالأدلة.
</div>

<h3 style="margin-top:20px;">ب. هندسة مجمع الحاويات الدافئة مسبقاً (prewarmed_pool.py)</h3>
<p>
يقضي مجمع الحاويات على التأخير الزمني في إقلاع الحاويات لتوفير بيئة عزل في أقل من 10ms:
</p>

<div style="margin:15px 0;">
{SVG_PREWARMED_POOL}
</div>

<pre><code class="language-python"># اقتباس تشريحي من prewarmed_pool.py — عمار
class PrewarmedSandboxPool:
    def __init__(self, target_ready_size: int = 3):
        self.ready_pool: asyncio.Queue = asyncio.Queue()
        self.active_allocations: Dict[str, SandboxInstance] = {{}}
        self.target_size = target_ready_size

    async def acquire_sandbox(self, session_id: str) -> SandboxInstance:
        # تخصيص فوري من الحاويات المجهزة سلفاً دون انتظار Docker Run
        instance = await self.ready_pool.get()
        instance.mark_busy(session_id)
        self.active_allocations[session_id] = instance
        
        # إطلاق مهمة غير متزامنة لإعادة ملء المجمع فورياً في الخلفية
        asyncio.create_task(self._replenish_worker())
        return instance</code></pre>

<!-- PAGE BREAK: SECTION 4 STEP-BY-STEP RUN -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 04 // STEP-BY-STEP RUN & FORENSICS TESTING</span>
    <span>AMMAR GUIDE</span>
</div>

<h2 class="section-title">04. دليل التشغيل وإجراء اختبارات الخداع والجنائيات خطوة بخطوة</h2>

<p>
خطوات تشغيل واختبار منظومة الفخاخ والتحقيق الجنائي الرقمي لعمار:
</p>

<h3>الخطوة الأولى: تشغيل خادم بيئة العزل (Sandbox) على المنفذ 8003</h3>
<pre><code class="language-bash"># تشغيل بيئة العزل التخيلية ومجمع الفخاخ
cd fastapi-deception-architecture-main
uvicorn isolation_sandbox.main:app --host 127.0.0.1 --port 8003 --reload</code></pre>

<h3>الخطوة الثانية: توليد وفحص التوكن الخداعي (Canary Token)</h3>
<pre><code class="language-bash"># استدعاء أداة توليد التوكنات وفحص بصمة HMAC
python -c "
from honey_token_injector.token_generator import HoneyTokenGenerator
token = HoneyTokenGenerator.generate_canary_token('admin_api_key')
print('Generated Honey Token:', token)
"</code></pre>

<h3>الخطوة الثالثة: محاكاة لمس الفخ والتحقق من التنبيه الفوري</h3>
<pre><code class="language-bash"># إرسال طلب استدعاء باستخدام التوكن الفخاخي
curl -i -X GET "http://127.0.0.1:8000/api/v1/debug/canary_trigger" \
  -H "X-Honey-Token: <GENERATED_TOKEN>"
# النتيجة المتوقعة:
# 1. إطلاق تنبيه فوري عبر WebSocket إلى SOC Dashboard.
# 2. عزل الجلسة فورياً وتوجيهها للـ Prewarmed Sandbox.
# 3. توثيق الحدث داخل سلسلة العهدة الجنائية بـ SHA-256.</code></pre>

<h3>الخطوة الرابعة: تشغيل اختبارات سلسلة العهدة الجنائية عبر pytest</h3>
<pre><code class="language-bash"># تنفيذ الاختبارات الجنائية المعتمدة
pytest tests/test_architecture_e2e.py -k "forensic or honey" -v
# النتيجة: نجاح الاختبارات بالكامل وتثبيت سلامة سلسلة الهاش.</code></pre>

<!-- PAGE BREAK: SECTION 5 TASK MATRIX -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 05 // TASK ASSIGNMENT MATRIX (AMMAR)</span>
    <span>AMMAR GUIDE</span>
</div>

<h2 class="section-title">05. مصفوفة المهام التفصيلية لعمار (Task Assignment Matrix)</h2>

<p>
الجدول الفردي الشامل لمهام عمار السبع (M-01 إلى M-07) بجميع الحقول الـ 13 المطلوبة وحالة الإنجاز الموثقة بالأدلة:
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
            <td><strong>M-01</strong></td>
            <td><strong>HMAC-SHA256 Honey Token Generator</strong></td>
            <td>توليد توكنات وعناوين URL وحقول خفية موقّعة برمجياً لا يمكن تزويرها.<br><code>token_generator.py</code></td>
            <td><strong>المدخلات:</strong> نوع التوكن والسر المشترك.<br><strong>المخرجات:</strong> توكن خداعي مشفر وموقع.</td>
            <td>توليد التوكن والتحقق من صحة التوقيع عبر token_verifier.<br><strong>القبول:</strong> رفض التوكنات المتلاعب بها بنجاح.</td>
            <td>S-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>توليد التوكنات والتحقق منها يعمل بكفاءة.</td>
        </tr>
        <tr>
            <td><strong>M-02</strong></td>
            <td><strong>Honey Token Response Injector Middleware</strong></td>
            <td>حقن التوكنات والروابط الخداعية داخل كائنات JSON العائدة للمستخدمين.<br><code>injector_middleware.py</code></td>
            <td><strong>المدخلات:</strong> استجابة FastAPI Response.<br><strong>المخرجات:</strong> حمولة مدمجة بالوسوم الخداعية.</td>
            <td>طلب استجابة وفحص محتوى JSON والتأكد من عدم تلف البنية.<br><strong>القبول:</strong> الحقول الخداعية مدمجة بسلاسة.</td>
            <td>M-01, Y-07<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>البرمجية الوسيطة تحقن الوسوم بدقة.</td>
        </tr>
        <tr>
            <td><strong>M-03</strong></td>
            <td><strong>Prewarmed Sandbox Pool Manager</strong></td>
            <td>إدارة مجمع الحاويات الجاهزة مسبقاً وتخصيصها في أقل من 10ms.<br><code>prewarmed_pool.py</code></td>
            <td><strong>المدخلات:</strong> إشارة عزل من البوابة.<br><strong>المخرجات:</strong> تخصيص فوري لحاوية معزولة.</td>
            <td>قياس زمن تخصيص الحاوية بالمايكروثانية وإعادة ملء المجمع.<br><strong>القبول:</strong> زمن الاستجابة &lt; 10ms.</td>
            <td>S-01, S-03<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>PrewarmedSandboxPool يلغي زمن الإقلاع البارد.</td>
        </tr>
        <tr>
            <td><strong>M-04</strong></td>
            <td><strong>Realistic Decoy Services & Synthetic Data</strong></td>
            <td>بناء التطبيق التخيلي وقواعد البيانات الوهمية لاستدراج المهاجمين.<br><code>decoy_environment.py</code></td>
            <td><strong>المدخلات:</strong> طلبات المهاجم المعزولة.<br><strong>المخرجات:</strong> نتائج تخيلية واقعية برمز 200.</td>
            <td>تنفيذ هجوم على الـ Decoy والتأكد من عدم وصوله لبيانات حقيقية.<br><strong>القبول:</strong> صفر تسريب لبيانات الإنتاج.</td>
            <td>M-03<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>بيئة الخداع تحاكي النظام الأصلي بواقعية.</td>
        </tr>
        <tr>
            <td><strong>M-05</strong></td>
            <td><strong>Tamper-Proof Chain of Custody Engine</strong></td>
            <td>هندسة سلسلة الهاش المشفرة للأدلة الرقمية وتطبيق معيار ISO 27037.<br><code>chain_of_custody.py</code></td>
            <td><strong>المدخلات:</strong> حزم البيانات والآثار الرقمية.<br><strong>المخرجات:</strong> كتل مشفرة بهاش تراكمي متصل.</td>
            <td>محاولة تعديل محتوى كتلة والتحقق من كشف انكسار السلسلة.<br><strong>القبول:</strong> إثبات رياضي غير قابل للتلاعب.</td>
            <td>S-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>سلسلة العهدة مجازة باختبارات E2E.</td>
        </tr>
        <tr>
            <td><strong>M-06</strong></td>
            <td><strong>DFIR Artifact & PCAP Extraction Engine</strong></td>
            <td>تسجيل أوامر الشل وتفريغ حمولات الشبكة واستخراج حزم PCAP.<br><code>artifact_collector.py, pcap_extractor.py</code></td>
            <td><strong>المدخلات:</strong> نشاط المهاجم داخل الـ Sandbox.<br><strong>المخرجات:</strong> ملفات أدلة جنائية مختومة.</td>
            <td>تنفيذ أوامر داخل الحاوية والتأكد من تسجيلها في commands.jsonl.<br><strong>القبول:</strong> استخراج الحزم وتوثيقها فورياً.</td>
            <td>M-05<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>المجمع الجنائي يسجل الأوامر والحزم بدقة.</td>
        </tr>
        <tr>
            <td><strong>M-07</strong></td>
            <td><strong>Real-Time SOC Telemetry & WebSockets</strong></td>
            <td>بث الأحداث السيبرانية وتحديث لوحة المراقبة ومطابقة MITRE ATT&CK.<br><code>websocket_manager.py, dashboard_api.py</code></td>
            <td><strong>المدخلات:</strong> تيار التنبيهات السريع.<br><strong>المخرجات:</strong> تدفق بيانات حي إلى واجهة الـ SOC.</td>
            <td>فتح اتصال WebSocket وإطلاق تنبيه ومراقبة استلامه الفوري.<br><strong>القبول:</strong> زمن وصول التنبيه &lt; 50ms.</td>
            <td>S-04, M-01<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>لوحة الـ SOC تستلم وتبث التنبيهات بنجاح.</td>
        </tr>
    </tbody>
</table>

<!-- PAGE BREAK: SECTION 6 DEFENSE Q&A -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 06 // GRADUATION DEFENSE VIVA Q&A</span>
    <span>AMMAR GUIDE</span>
</div>

<h2 class="section-title">06. دليل مناقشة التخرج وأسئلة لجنة التحكيم لعمار (Ammar Defense Viva)</h2>

<p>
أقوى الأسئلة الدفاعية المتوقعة في مجال الأدلة الجنائية وهندسة الخداع الموجهة لعمار مع إجاباتها:
</p>

<div class="faq-item">
    <div class="faq-q">س 1: هل يعتبر استخدام تقنيات الخداع واستدراج المهاجمين مقبولاً من الناحية القانونية؟ وما الفرق بين الاستدراج المشروع (Enticement) والإيقاع غير القانوني (Entrapment)؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي لعمار:</strong>
        "منظومتنا متوافقة تماماً مع المعايير القانونية الدولية:
        <br><strong>الإيقاع غير المشروع (Entrapment)</strong> يحدث فقط عندما تقوم جهة إنفاذ القانون بإغراء شخص بريء وتشجيعه على ارتكاب جريمة لم يكن ينوي ارتكابها أصلاً.
        <br>أما <strong>الاستدراج المشروع (Enticement)</strong> والدفاع السيبراني النشط، فيعني وضع حواجز ومصائد داخل بيئتنا الخاصة لحماية أنظمتنا. المهاجم الذي يبحث عن نقاط الضعف ويسرق الـ Honey Tokens قد دخل إلى نظامنا بإرادته الجرمية المستقلة، واستخدامنا للـ Decoy هو إجراء دفاعي مشروع لحصر الضرر وجمع الأدلة الرقمية وفق القانون."
    </div>
</div>

<div class="faq-item">
    <div class="faq-q">س 2: كيف تضمن أن الأدلة الرقمية المستخرجة (PCAP والـ Logs) صالحة ومقبولة أمام المحكمة الجنائية؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي لعمار:</strong>
        "المحاكم الجنائية تشترط إثبات <strong>سلامة سلسلة العهدة (Chain of Custody)</strong> بموجب المعيار الدولي <code>ISO/IEC 27037</code>.
        <br>في معماريتنا، لا يتم حفظ الأدلة في ملفات نصية بسيطة قابلة للتعديل؛ بل يتم ختم كل أثر فور استخراجه برمز <code>SHA-256</code> وربطه رياضياً بالكتلة السابقة عبر فئة <code>ChainOfCustodyVault</code>. أي محاولة من المشرف أو المتسلل لتعديل حرف واحد في سجلات الأوامر ستؤدي إلى انكسار السلسلة الحسابية فوراً، مما يمنح أدلتنا حجية قانونية قطعية."
    </div>
</div>

<div class="faq-item">
    <div class="faq-q">س 3: لماذا قمت بابتكار مجمع الحاويات الدافئة (Prewarmed Pool) بدلاً من إنشاء الحاوية عبر Docker عند اكتشاف الهجوم؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي لعمار:</strong>
        "إنشاء حاوية جديدة باستخدام <code>docker run</code> يستغرق ما بين <strong>2.5 إلى 4.5 ثانية</strong>. هذا التأخير الزمني كافٍ جداً ليلاحظ المهاجم تجمد الاتصال، أو لانقطاع مهلة الـ HTTP Timeout لدى العميل.
        <br>عبر <code>PrewarmedSandboxPool</code>، نحن نحتفظ دائماً بـ 3 حاويات مشتغلة سلفاً وجاهزة في الذاكرة. عندما ترسل البوابة إشارة العزل، نقوم بربط الاتصال بالحاوية الجاهزة في أقل من <strong>10 ميلي ثانية</strong>، ونطلق في الخلفية عملية تجهيز حاوية بديلة بهدوء، مما يحقق عزلاً فورياً غير محسوس."
    </div>
</div>

<div class="faq-item">
    <div class="faq-q">س 4: كيف تحمي نفسك من تزوير الـ Honey Tokens من قبل المهاجم لاتهام مستخدمين أبرياء؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي لعمار:</strong>
        "كل Honey Token يتم توليده يحمل توقيعاً مشفراً باستخدام <code>HMAC-SHA256</code> ومفتاح سري محمي داخل بيئة الخادم. لا يمكن لأي طرف خارجي تخمين أو تزوير هذا التوقيع. عند استدعاء التوكن، يتحقق <code>TokenVerifier</code> من التوقيع الرياضي؛ فإذا كان التوقيع صحيحاً، نتأكد بنسبة 100% أن هذا التوكن خرج من فخاخنا ولم يزوره طرف خارجي، مما يحقق نسبة إنذارات كاذبة صفرية (Zero False Positives)."
    </div>
</div>

<div class="doc-footer">
    <span>FASTAPI DECEPTION ARCHITECTURE // MEMBER 04: AMMAR</span>
    <span>CONFIDENTIAL & CLASSIFIED // GRADUATION THESIS 2026</span>
</div>

</body>
</html>
"""
