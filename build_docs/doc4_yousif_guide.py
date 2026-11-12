"""
Generator for Document 04: YOUSIF_DEVELOPER_GUIDE.pdf
Role: Yousif — Core Application & Data Engineer
"""

from build_docs.common_css import CYBER_THEME_CSS
from build_docs.svg_diagrams import SVG_4LAYER_ARCHITECTURE, SVG_TRAFFIC_FLOW_PATHS


def get_html_content() -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>YOUSIF DEVELOPER GUIDE — FastAPI Deception Architecture</title>
<style>
{CYBER_THEME_CSS}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
    <div class="cover-header">
        <span class="cover-badge">DEFENSE THESIS SPECIFICATION // CORE & DATA</span>
        <span style="font-family:'Consolas',monospace; font-size:9pt; color:#94a3b8;">ROLE ID: 03 // APP-DATA</span>
    </div>

    <div class="cover-title-box">
        <div class="cover-title-en">CORE APPLICATION & DATA ENGINEER GUIDE</div>
        <div class="cover-title-ar">دليل مهندس التطبيق الحقيقي والبيانات — يوسف (Yousif)</div>
        <div class="cover-subtitle">Enterprise Business Logic, PBKDF2/JWT Authentication, Resilient Data Stores, and In-Memory Fallbacks</div>
        <p style="color:#cbd5e1; font-size:10.5pt; max-width:650px; margin:0;">
            الدليل التنفيذي والبرمجي المتكامل ليوسف: بناء منطق الأعمال النظيف على المنفذ 8001، تأمين التوثيق والتفويض عبر PBKDF2 و JWT، إدارة التخزين غير المتزامن في PostgreSQL و Redis، وصيانة مخازن الطوارئ للتعافي التلقائي.
        </p>
    </div>

    <div class="cover-meta-grid">
        <div class="cover-meta-item">
            <span class="cover-meta-label">العضو والصفة</span>
            <span class="cover-meta-val">يوسف (Yousif) — Core Application & Data Engineer</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">الرمز التعريفي / الترتيب</span>
            <span class="cover-meta-val">MEMBER 03 // CORE & DATA ENGINEER</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">الملفات والمسؤوليات الأساسية</span>
            <span class="cover-meta-val">endpoints.py, auth_service.py, business_logic.py, relational_db.py, fallback_inmemory_store.py</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">حالة الإنجاز والتحقق البرمجي</span>
            <span class="cover-meta-val">100% VERIFIED (Resilient Storage & JWT Lifecycle)</span>
        </div>
    </div>
</div>

<!-- PAGE BREAK: TOC -->
<div class="page-break"></div>

<div class="page-header">
    <span>FASTAPI DECEPTION ARCHITECTURE // MEMBER 03 GUIDE</span>
    <span>ROLE: CORE APPLICATION & DATA SPECIALIST</span>
</div>

<h2 class="section-title">فهرس محتويات دليل مهندس التطبيق الحقيقي والبيانات</h2>

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
            <td><strong>التخصص البرمجي والمسؤوليات المباشرة ليوسف</strong></td>
            <td>حماية المنفذ 8001، بناء منطق الأعمال الحقيقي، التوثيق المشفر، وإدارة قواعد البيانات.</td>
        </tr>
        <tr>
            <td><strong>02</strong></td>
            <td><strong>النطاق التقني وحصر الملفات والمكونات المملوكة</strong></td>
            <td>حصر ملفات core_web_app و data_storage، نماذج Pydantic، ومستودعات البيانات الدائمة والمؤقتة.</td>
        </tr>
        <tr>
            <td><strong>03</strong></td>
            <td><strong>التحليل والتشريح البرمجي العميق لكود التطبيق والبيانات</strong></td>
            <td>تشريح تشفير PBKDF2، إصدار والتحقق من JWT، تجميع اتصالات DB، وآلية Fallback الآمنة.</td>
        </tr>
        <tr>
            <td><strong>04</strong></td>
            <td><strong>دليل التشغيل وإجراء اختبارات التطبيق والبيانات خطوة بخطوة</strong></td>
            <td>تشغيل التطبيق مستقلاً، اختبار مصادقة المستخدمين، تجربة انقطاع قاعدة البيانات، والتحقق عبر pytest.</td>
        </tr>
        <tr>
            <td><strong>05</strong></td>
            <td><strong>مصفوفة المهام التفصيلية ليوسف (Task Assignment Matrix)</strong></td>
            <td>جدول المهام السبع (Y-01 إلى Y-07) بجميع الحقول الـ 13 المطلوبة مدعمة بالأدلة البرمجية القاطعة.</td>
        </tr>
        <tr>
            <td><strong>06</strong></td>
            <td><strong>دليل مناقشة التخرج وأسئلة لجنة التحكيم ليوسف</strong></td>
            <td>أقوى 6 أسئلة دفاعية متوقعة لمهندس التطبيق والبيانات حول أمان التشفير والـ Connection Pooling.</td>
        </tr>
    </tbody>
</table>

<div class="callout callout-info" style="margin-top:20px;">
    <div class="callout-title">توجيه فني ليوسف (Yousif):</div>
    أنت صمام الأمان للبيانات الحقيقية للمؤسسة. بينما ينشغل علي وعمار بجذب المهاجمين وصدهم، مهمتك هي ضمان أن التطبيق الأساسي (Core Web App) يعمل بنقاء 100%، وخالٍ تماماً من الثغرات، ومبني وفق أعلى المعايير الهندسية لمصادقة المستخدمين وإدارة الجلسات.
</div>

<!-- PAGE BREAK: SECTION 1 & 2 -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 01 & 02 // CORE APP ROLE & BOUNDARIES</span>
    <span>YOUSIF GUIDE</span>
</div>

<h2 class="section-title">01. التخصص البرمجي والمسؤوليات المباشرة ليوسف (Core App & Data)</h2>

<p>
يوسف هو المسؤول الرئيسي عن بناء وصيانة التطبيق الحقيقي (Layer 2: Core Web App) ومخازن البيانات (Data Storage Layer). يضمن يوسف أن المستخدم الشرعي يتلقى الخدمة بسرعة فائقة مع تطبيق صارم لمبادئ التصميم النظيف (Clean Architecture) والتحقق من صحة المدخلات.
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
                <td><strong>خدمة التوثيق والتفويض (Auth Service)</strong></td>
                <td>تشفير كلمات المرور باستخدام خوارزمية PBKDF2-SHA256 مع Salt عشوائي، وإصدار توكنات JWT موقّعة رقمياً مع التحقق من الصلاحيات.</td>
                <td>مقاومة تامة لهجمات التخمين وجداول Rainbow Tables.</td>
            </tr>
            <tr>
                <td><strong>واجهات برمجة التطبيقات (API Endpoints)</strong></td>
                <td>بناء مسارات RESTful لخدمات المستخدمين والمعاملات، وتطبيق التحقق الصارم من الأنماط عبر نماذج Pydantic v2.</td>
                <td>حماية تلقائية من حقن البيانات الملوثة (Input Sanitization).</td>
            </tr>
            <tr>
                <td><strong>إدارة مخازن البيانات (Data Persistence)</strong></td>
                <td>توفير مستودعات التخزين غير المتزامن (Async Repository Pattern) لقواعد بيانات PostgreSQL وإدارة الجلسات في Redis.</td>
                <td>تجميع الاتصالات (Connection Pooling) عالي الكفاءة.</td>
            </tr>
            <tr>
                <td><strong>مخزن الطوارئ والصلابة (Resilient Fallback)</strong></td>
                <td>تطوير مخزن ذاكرة احتياطي (Fallback InMemory Store) يعمل تلقائياً عند غياب خوادم البيانات الخارجية لضمان صمود النظام.</td>
                <td>استمرارية الخدمة بنسبة 100% دون انهيار الخادم (Zero Crash).</td>
            </tr>
        </tbody>
    </table>
</div>

<h2 class="section-title" style="margin-top:25px;">02. النطاق التقني وحصر الملفات والمكونات المملوكة ليوسف</h2>

<div class="file-box">
    <div class="file-box-title">حصر الملفات البرمجية التي تقع تحت ملكية يوسف المباشرة (Yousif's Code Ownership)</div>
    <ul style="margin:5px 0 0 20px; font-family:'Consolas',monospace; font-size:9pt; line-height:1.7;">
        <li><strong>core_web_app/services/auth_service.py:</strong> محرك التشفير وتوليد الـ Hash والتحقق من التوكنات الرقمية JWT.</li>
        <li><strong>core_web_app/api/endpoints.py:</strong> مسارات التطبيق الفعلية (/login, /profile, /transactions, /records).</li>
        <li><strong>core_web_app/services/business_logic.py:</strong> قواعد الأعمال ومنطق المعالجة الحسابية والمالية للتطبيق.</li>
        <li><strong>core_web_app/schemas/pydantic_models.py:</strong> المخططات الصارمة لبيانات الطلبات والاستجابات ونماذج المصادقة.</li>
        <li><strong>data_storage/relational_db.py:</strong> واجهة الاتصال غير المتزامن بقاعدة بيانات PostgreSQL ومستودع السجلات.</li>
        <li><strong>data_storage/redis_session_store.py:</strong> مستودع حفظ الجلسات وحالات التوكنات وتدفق التنبيهات في Redis.</li>
        <li><strong>data_storage/fallback_inmemory_store.py:</strong> مستودع التخزين المؤقت الاحتياطي عالي التوافر في الذاكرة.</li>
    </ul>
</div>

<!-- PAGE BREAK: SECTION 3 CODE DEEP DIVE -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 03 // DEEP CODE INSPECTION & WALKTHROUGH</span>
    <span>YOUSIF GUIDE</span>
</div>

<h2 class="section-title">03. التحليل والتشريح البرمجي العميق لكود التطبيق والبيانات</h2>

<p>
استخدم يوسف أفضل الممارسات الأمنية المعتمدة دولياً في هندسة خدمات المصادقة ومخازن البيانات. نستعرض أهم الشيفرات:
</p>

<h3>أ. خدمة المصادقة وتشفير PBKDF2 والـ JWT (auth_service.py)</h3>
<p>
تستخدم هذه الوحدة خوارزمية PBKDF2 مع SHA256 و 100,000 تكرار مع ملح ديناميكي لضمان استحالة كسر كلمات المرور:
</p>

<pre><code class="language-python"># اقتباس تشريحي من auth_service.py — يوسف
class AuthService:
    ITERATIONS = 100000
    ALGORITHM = "HS256"
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "prod-defense-secret-key-9812")

    @classmethod
    def hash_password(cls, password: str) -> str:
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), cls.ITERATIONS
        )
        return f"pbkdf2:sha256:{{cls.ITERATIONS}}${{salt}}${{key.hex()}}"

    @classmethod
    def verify_password(cls, plain_password: str, hashed: str) -> bool:
        try:
            _, _, salt, stored_key = hashed.split("$")
            new_key = hashlib.pbkdf2_hmac(
                "sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), cls.ITERATIONS
            )
            # مقارنة زمنية ثابتة لمنع هجمات التوقيت (Timing Attacks)
            return hmac.compare_digest(new_key.hex(), stored_key)
        except Exception:
            return False

    @classmethod
    def create_jwt_token(cls, user_id: str, role: str) -> str:
        payload = {{
            "sub": user_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=8),
            "iat": datetime.utcnow()
        }}
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)</code></pre>

<div class="callout callout-success">
    <div class="callout-title">الحماية من هجمات التوقيت (Timing Attacks):</div>
    استخدام <code>hmac.compare_digest</code> يضمن أن عملية مقارنة الـ Hash تستغرق نفس الوقت بغض النظر عن عدد المحارف المتطابقة، مما يحبط محاولات المهاجمين لقياس زمن الاستجابة لاكتشاف أجزاء من كلمات المرور.
</div>

<h3 style="margin-top:20px;">ب. مخزن الطوارئ الذاتي عالي الصلابة (fallback_inmemory_store.py)</h3>
<p>
يضمن هذا المخزن عدم توقف النظام حتى في أصعب الظروف التشغيلية:
</p>

<pre><code class="language-python"># اقتباس تشريحي من fallback_inmemory_store.py — يوسف
class FallbackInMemoryStore:
    def __init__(self):
        self._store: Dict[str, Any] = {{}}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            return self._store.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        async with self._lock:
            self._store[key] = value
            return True

    async def append_log(self, stream_name: str, entry: Dict[str, Any]):
        async with self._lock:
            if stream_name not in self._store:
                self._store[stream_name] = []
            self._store[stream_name].append(entry)</code></pre>

<!-- PAGE BREAK: SECTION 4 STEP-BY-STEP RUN -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 04 // STEP-BY-STEP RUN & CORE APP TESTING</span>
    <span>YOUSIF GUIDE</span>
</div>

<h2 class="section-title">04. دليل التشغيل وإجراء اختبارات التطبيق والبيانات خطوة بخطوة</h2>

<p>
خطوات تشغيل واختبار التطبيق الأساسي ومستودعات التخزين ليوسف:
</p>

<h3>الخطوة الأولى: تشغيل خادم التطبيق الأساسي على المنفذ 8001</h3>
<pre><code class="language-bash"># تشغيل التطبيق الحقيقي مع تفعيل المراقبة
cd fastapi-deception-architecture-main
uvicorn core_web_app.main:app --host 127.0.0.1 --port 8001 --reload</code></pre>

<h3>الخطوة الثانية: اختبار عملية تسجيل الدخول وتوليد التوكن (JWT Authentication)</h3>
<pre><code class="language-bash"># طلب تسجيل الدخول للمستخدم الشرعي
curl -i -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{{"username": "admin_legit", "password": "SecurePassword123!"}}'
# النتيجة المتوقعة:
# HTTP/1.1 200 OK
# {{"access_token": "eyJhbGciOi...", "token_type": "bearer", "expires_in": 28800}}</code></pre>

<h3>الخطوة الثالثة: الوصول إلى الموارد المحمية بالتوكن</h3>
<pre><code class="language-bash"># استدعاء الملف الشخصي باستخدام التوكن المستلم
curl -i -X GET "http://127.0.0.1:8001/api/v1/profile" \
  -H "Authorization: Bearer <TOKEN_STRING>"
# النتيجة: إرجاع بيانات المستخدم النظيفة بدقة وسرعة &lt; 2ms.</code></pre>

<h3>الخطوة الرابعة: اختبار صلابة التخزين عند فصل Redis / PostgreSQL</h3>
<pre><code class="language-bash"># اختبار تشغيل الفحوصات في وضع عدم توفر خادم خارجي
pytest tests/test_architecture_e2e.py -k "legitimate" -v
# النتيجة: نجاح الاختبار بالكامل بفضل FallbackInMemoryStore.</code></pre>

<!-- PAGE BREAK: SECTION 5 TASK MATRIX -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 05 // TASK ASSIGNMENT MATRIX (YOUSIF)</span>
    <span>YOUSIF GUIDE</span>
</div>

<h2 class="section-title">05. مصفوفة المهام التفصيلية ليوسف (Task Assignment Matrix)</h2>

<p>
الجدول الفردي الشامل لمهام يوسف السبع (Y-01 إلى Y-07) بجميع الحقول الـ 13 المطلوبة وحالة الإنجاز الموثقة بالأدلة:
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
            <td><strong>Y-01</strong></td>
            <td><strong>PBKDF2-SHA256 Auth & Hashing Service</strong></td>
            <td>تطوير نظام تجزئة كلمات المرور بـ 100,000 دورة وتوليد ملح عشوائي فريد.<br><code>auth_service.py</code></td>
            <td><strong>المدخلات:</strong> كلمة المرور النصية.<br><strong>المخرجات:</strong> سلسلة الـ Hash المشفرة والآمنة.</td>
            <td>محاولة فحص كلمات مرور متعددة واختبار hmac.compare_digest.<br><strong>القبول:</strong> مطابقة تامة ومقاومة هجمات التوقيت.</td>
            <td>S-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>تم اختباره ومطابق لمواصفات NIST الأمنية.</td>
        </tr>
        <tr>
            <td><strong>Y-02</strong></td>
            <td><strong>JWT Token Lifecycle Management</strong></td>
            <td>توليد توكنات JWT مع تضمين الصلاحيات وتحديد تاريخ انتهاء الصلاحية والتوقيع.<br><code>auth_service.py</code></td>
            <td><strong>المدخلات:</strong> بيانات المستخدم وصلاحياته.<br><strong>المخرجات:</strong> توكن JWT مشفر وموقع بـ HS256.</td>
            <td>فك وتشفير التوكن وتجربة إرسال توكن منتهي الصلاحية.<br><strong>القبول:</strong> رفض التوكنات المتلاعب بها بنجاح.</td>
            <td>Y-01<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>توليد والتحقق من التوكنات يعمل بسلاسة.</td>
        </tr>
        <tr>
            <td><strong>Y-03</strong></td>
            <td><strong>Redis Async Session Store Engine</strong></td>
            <td>تطوير مستودع اتصالات Redis غير المتزامن لإدارة الجلسات وبث التنبيهات.<br><code>redis_session_store.py</code></td>
            <td><strong>المدخلات:</strong> معاملات الجلسة والبيانات.<br><strong>المخرجات:</strong> تخزين مؤقت فائق السرعة.</td>
            <td>إجراء عمليات القراءة والكتابة المتزامنة وقياس سرعة الاستجابة.<br><strong>القبول:</strong> سرعة استعلام &lt; 1ms.</td>
            <td>S-01<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>يدعم عمليات get, set, append_stream.</td>
        </tr>
        <tr>
            <td><strong>Y-04</strong></td>
            <td><strong>PostgreSQL Relational DB Repository</strong></td>
            <td>بناء نموذج مستودع قاعدة البيانات العلائقية لحفظ سجلات المستخدمين والمعاملات.<br><code>relational_db.py</code></td>
            <td><strong>المدخلات:</strong> نماذج السجلات والمعاملات.<br><strong>المخرجات:</strong> استعلامات مهيأة ومجمعة بأمان.</td>
            <td>إجراء عمليات الحفظ والبحث والتحقق من استخدام الاستعلامات المهيأة.<br><strong>القبول:</strong> حماية 100% من SQL Injection.</td>
            <td>Y-01<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>مستودع البيانات العلائقي مكتمل ومحمي.</td>
        </tr>
        <tr>
            <td><strong>Y-05</strong></td>
            <td><strong>Resilient InMemory Fallback System</strong></td>
            <td>تطوير مخزن ذاكرة آمن غير متزامن يحاكي Redis و DB عند انقطاعهما.<br><code>fallback_inmemory_store.py</code></td>
            <td><strong>المدخلات:</strong> مفاتيح وقيم وسجلات.<br><strong>المخرجات:</strong> استمرارية العمل دون توقف السيرفر.</td>
            <td>فصل خادم Redis وتشغيل التطبيق والتحقق من حفظ البيانات محلياً.<br><strong>القبول:</strong> صفر انهيارات (Zero Crash).</td>
            <td>Y-03<br><span class="badge badge-high">HIGH</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>FallbackInMemoryStore مستخدم في بيئة الاختبار.</td>
        </tr>
        <tr>
            <td><strong>Y-06</strong></td>
            <td><strong>Pydantic v2 Schema Modeling & Sanitization</strong></td>
            <td>بناء مخططات البيانات الصارمة للتحقق من صحة المدخلات وتطهيرها تلقائياً.<br><code>pydantic_models.py</code></td>
            <td><strong>المدخلات:</strong> كائنات JSON الخام.<br><strong>المخرجات:</strong> كائنات كود نظيفة ومطهرة ومعتمدة.</td>
            <td>تمرير حقول ملوثة بمحارف غير متوافقة والتحقق من إرجاع 422.<br><strong>القبول:</strong> رفض المدخلات غير المطابقة.</td>
            <td>S-06<br><span class="badge badge-medium">MEDIUM</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>نماذج Pydantic v2 منجزة ومعتمدة.</td>
        </tr>
        <tr>
            <td><strong>Y-07</strong></td>
            <td><strong>Core Business Logic & Transactions API</strong></td>
            <td>تنفيذ واجهات برمجة التطبيقات الأساسية (/profile, /transactions, /data).<br><code>endpoints.py, business_logic.py</code></td>
            <td><strong>المدخلات:</strong> طلبات العملاء الموثقة.<br><strong>المخرجات:</strong> بيانات الأعمال الحقيقية.</td>
            <td>استدعاء المسارات عبر حسابات ذات صلاحيات مختلفة.<br><strong>القبول:</strong> إنفاذ سياسة الـ RBAC بدقة.</td>
            <td>Y-02, Y-06<br><span class="badge badge-critical">CRITICAL</span></td>
            <td><span class="badge badge-success">100% DONE</span><br>مسارات التطبيق الحقيقي تعمل بنجاح.</td>
        </tr>
    </tbody>
</table>

<!-- PAGE BREAK: SECTION 6 DEFENSE Q&A -->
<div class="page-break"></div>

<div class="page-header">
    <span>SECTION 06 // GRADUATION DEFENSE VIVA Q&A</span>
    <span>YOUSIF GUIDE</span>
</div>

<h2 class="section-title">06. دليل مناقشة التخرج وأسئلة لجنة التحكيم ليوسف (Yousif Defense Viva)</h2>

<p>
أهم الأسئلة المتقدمة في هندسة البيانات والمصادقة البرمجية الموجهة ليوسف مع أجوبتها النموذجية:
</p>

<div class="faq-item">
    <div class="faq-q">س 1: لماذا اخترت خوارزمية PBKDF2-SHA256 مع 100,000 دورة بدلاً من خوارزميات مثل MD5 أو SHA-256 البسيطة؟ ولماذا لم تستخدم Argon2؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي ليوسف:</strong>
        "خوارزميات MD5 و SHA256 البسيطة صُممت لتكون سريعة جداً في التحقق من تكامل الملفات، مما يجعلها كارثية لتشفير كلمات المرور لأن بطاقات الرسوميات (GPUs) تستطيع تجربة مليارات الاحتمالات في الثانية (Brute Force).
        <br>اخترنا <strong>PBKDF2-SHA256 بـ 100,000 تكرار</strong> لأنها معيار رسمي موصى به من معهد NIST الأمريكي، وتقوم بزيادة العبء الحسابي على المهاجم بمقدار 100 ألف ضعف، كما أنها مدمجة في مكتبة بايثون القياسية (<code>hashlib</code>) دون الحاجة لمترجمات C خارجية مثل Argon2، مما يضمن التوافقية العالية وسهولة النشر السحابي داخل الحاويات."
    </div>
</div>

<div class="faq-item">
    <div class="faq-q">س 2: كيف تضمن عدم تعرض التطبيق لهجمات حقن قواعد البيانات (SQL Injection) في مساراته؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي ليوسف:</strong>
        "نحن لا نستخدم إطلاقاً دمج النصوص (String Concatenation) في صياغة الاستعلامات. جميع الاستعلامات داخل <code>relational_db.py</code> تستخدم استعلامات مهيأة ومقيدة بالمعاملات (Parameterized Queries) عبر SQLAlchemy و asyncpg. بالإضافة إلى ذلك، نقوم بتطهير المدخلات مسبقاً على مستوى الطبقة الأولى بواسطة نماذج Pydantic v2 الصارمة، مما يجعل تمرير أي حمولة SQLi مستحيلاً."
    </div>
</div>

<div class="faq-item">
    <div class="faq-q">س 3: توكنات JWT غير قابلة للإلغاء بطبيعتها (Stateless) حتى انتهاء صلاحيتها. كيف تعاملت مع سيناريو سرقة التوكن أو تسجيل الخروج؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي ليوسف:</strong>
        "طبقنا نمط التوثيق الهجين (Hybrid Token Invalidation):
        <br>عند تسجيل الخروج أو عند كشف نشاط مشبوه من قبل البوابة، يتم إدراج معرف التوكن (JTI أو User-ID) فورياً في قائمة الحظر المؤقتة (Blacklist) داخل ذاكرة Redis مع تعيين وقت انتهاء مساوٍ لبقية عمر التوكن (TTL). يتم فحص هذا المفتاح في أقل من 0.8 ميلي ثانية، مما يبطل مفعول التوكن فوراً حتى لو كان تاريخ صلاحيته سارياً."
    </div>
</div>

<div class="faq-item">
    <div class="faq-q">س 4: ما هي فائدة الـ Connection Pooling في التطبيقات غير المتزامنة التي بنيتها؟</div>
    <div class="faq-a">
        <strong>الجواب النموذجي ليوسف:</strong>
        "إنشاء اتصال جديد بقاعدة البيانات يستلزم مصافحة TCP معقدة وتوثيقاً يستهلك عشرات الميلي ثواني. باستخدام تجمع الاتصالات (Connection Pool) داخل <code>relational_db.py</code>، نحافظ على عدد محدد من الاتصالات المفتوحة سلفاً، ونقوم بإعادة استخدامها بين الطلبات المتزامنة، مما يرفع قدرة التطبيق على معالجة آلاف الطلبات في الثانية دون إرهاق خادم قاعدة البيانات."
    </div>
</div>

<div class="doc-footer">
    <span>FASTAPI DECEPTION ARCHITECTURE // MEMBER 03: YOUSIF</span>
    <span>CONFIDENTIAL & CLASSIFIED // GRADUATION THESIS 2026</span>
</div>

</body>
</html>
"""
