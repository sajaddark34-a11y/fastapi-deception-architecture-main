"""
Generator for Document 01: TEAM_MASTER_GUIDE.pdf
"""

from build_docs.common_css import CYBER_THEME_CSS
from build_docs.svg_diagrams import SVG_4LAYER_ARCHITECTURE, SVG_CHAIN_OF_CUSTODY


def get_html_content() -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>TEAM MASTER GUIDE — FastAPI Deception Architecture</title>
<style>
{CYBER_THEME_CSS}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
    <div class="cover-header">
        <span class="cover-badge">DEFENSE THESIS SPECIFICATION // VER 2.0</span>
        <span style="font-family:'Consolas',monospace; font-size:9pt; color:#94a3b8;">SEC-CLASSIFIED: RESTRICTED</span>
    </div>

    <div class="cover-title-box">
        <div class="cover-title-en">FASTAPI DECEPTION ARCHITECTURE</div>
        <div class="cover-title-ar">الدليل الماستر الشامل ومعمارية المنظومة الدفاعية</div>
        <div class="cover-subtitle">Enterprise Active Threat Deception, Sub-Millisecond Session Isolation, and Tamper-Evident Digital Forensics Extraction</div>
        <p style="color:#cbd5e1; font-size:10.5pt; max-width:650px; margin:0;">
            المرجع المعماري والتنفيذي الموحد لمشروع التخرج: هندسة الدفاع السيبراني النشط، توجيه حركة المرور غير المتزامن، مجمع حاويات العزل السريعة، وسلسلة العهدة الرقمية المقاومة للتلاعب.
        </p>
    </div>

    <div class="cover-meta-grid">
        <div class="cover-meta-item">
            <span class="cover-meta-label">قائد الفريق والمهندس المعماري</span>
            <span class="cover-meta-val">سجاد (Sadjad) — Team Leader & System Architect</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">مهندس البوابة وتصنيف المرور</span>
            <span class="cover-meta-val">علي (Ali) — Backend & Deception Gateway Engineer</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">مهندس التطبيق الحقيقي والبيانات</span>
            <span class="cover-meta-val">يوسف (Yousif) — Core Application & Data Engineer</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">مهندس الشراك والعزل والجنائيات</span>
            <span class="cover-meta-val">عمار (Ammar) — Honeypot, Sandbox & Forensics Engineer</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">تاريخ الإصدار والتحقق</span>
            <span class="cover-meta-val">نوفمبر 2026 // Production Verified</span>
        </div>
        <div class="cover-meta-item">
            <span class="cover-meta-label">حالة الاختبارات والاعتماد</span>
            <span class="cover-meta-val" style="color:#4ade80;">100% Passed (5 of 5 Test Suites Active)</span>
        </div>
    </div>

    <div class="cover-footer">
        <span>FastAPI-Driven Deception Architecture Project Organization</span>
        <span>Confidential — For Graduation Committee & Development Team Only</span>
    </div>
</div>

<!-- PAGE 2: EXECUTIVE SUMMARY & OBJECTIVES -->
<div class="page-break">
    <div class="doc-running-header">
        <span>FASTAPI DECEPTION ARCHITECTURE // MASTER SYSTEM GUIDE</span>
        <span>SECTION 1: الملخص التنفيذي والأهداف</span>
    </div>

    <h1>1. الملخص التنفيذي والأهداف الاستراتيجية للمشروع</h1>
    
    <div class="alert-box alert-note">
        <div class="alert-title">📌 الرؤية الهندسية للمشروع (Core Engineering Vision)</div>
        مشروع <strong>معمارية الخداع السيبراني المبنية على FastAPI لكشف التهديدات واستخراج الأدلة الجنائية</strong> هو نظام دفاع سيبراني نشط (Active Cyber Defense) تم تصميمه وفق معايير المؤسسات الكبرى (Enterprise-Grade). يهدف إلى نقل المؤسسة من الدفاع السلبي التقليدي إلى استدراج المهاجمين واحتجازهم داخل بيئات وهمية معزولة شبكياً واستخراج أدلة إدانتهم بدقة قانونية قطعية.
    </div>

    <h2>1.1 المشكلة الهندسية في منظومات الحماية التقليدية</h2>
    <p>
        تعتمد منظومات الحماية الشائعة مثل الجدران النارية (Firewalls / WAF) وأنظمة كشف ومنع التسلل (IDS / IPS) على مبدأ <strong>الحظر المباشر (Direct Drop / Block)</strong> عند رصد أي سلوك مشبوه. هذا النهج يمتلك ثغرات استراتيجية:
    </p>
    <ul>
        <li><strong>إشعار المهاجم بكشفه (Attacker Alerting)</strong>: عندما يستلم المهاجم رد <code>403 Forbidden</code> أو تنقطع جلسته، يدرك فوراً أن أسلوبه أو عنوان IP الخاص به قد تم وسمه، فيلجأ لتغيير عنوانه أو تعديل تقنيات الهجوم لتجاوز الجدار الناري.</li>
        <li><strong>فقدان الاستخبارات الأمنية (Loss of Threat Intelligence)</strong>: لا يتيح الحظر للمدافعين معرفة نوايا المهاجم النهائية، أو أدوات استغلال الثغرات (Exploits) التي يمتلكها، أو عناوين سيرفرات القيادة والسيطرة (C2) التي يحاول الاتصال بها.</li>
        <li><strong>كثرة الإنذارات الكاذبة (High False Positive Rates)</strong>: تؤدي قواعد الفحص الفضفاضة في WAF إلى حظر مستخدمين شرعيين، مما يعطل أعمال المؤسسة.</li>
    </ul>

    <h2>1.2 الحل المبتكر: الدفاع بالخداع التفاعلي (Interactive Deception Architecture)</h2>
    <p>
        يقوم مشروعنا على قلب المعادلة: بدلاً من حظر المهاجم، نقوم بما يلي:
    </p>
    <ol>
        <li><strong>حقن الشراك الخداعية الموقعة (HMAC-SHA256 Signed Lures)</strong>: توليد ترويسات HTTP مزيفة (مثل <code>X-Internal-Debug-Token</code>) وروابط مخفية في JSON (مثل <code>/api/v1/internal/vault-keys</code>) وتضمينها داخل استجابات التطبيق الحقيقي.</li>
        <li><strong>التحويل التلقائي والشفاف (Transparent Sub-Millisecond Routing)</strong>: عند محاولة المهاجم أو أداة الفحص استغلال هذا الطُعم، تقوم البوابة <code>deception_gateway</code> بتصعيد حالته فوراً وتحويل جلسته إلى <strong>بيئة عزل ديناميكية مُحمّاة مسبقاً (Prewarmed Sandbox)</strong> دون انقطاع اتصاله.</li>
        <li><strong>محاكاة البيئة الواقعية (High-Interaction Emulation)</strong>: يتفاعل المهاجم مع نظام ملفات لينكس وهمي وشل تفاعلي وخزائن مفاتيح مصطنعة، مما يستنزف وقته وموارده ويوهمه بأنه سيطر على السيرفر.</li>
        <li><strong>التحقيق الجنائي الرقمي اللحظي (Automated DFIR)</strong>: تسجيل كل أمر، وحزمة شبكة (PCAP)، ونداء نواة (eBPF)، وربطها بسلسلة عهدة رقمية مشفرة (Tamper-Evident Chain of Custody) مقبولة قانونياً.</li>
    </ol>

    <h2>1.3 بطاقة الهوية التقنية للمشروع (Technology Stack)</h2>
    <table>
        <thead>
            <tr><th>المكون (Component)</th><th>التقنية المستخدمة (Technology)</th><th>الإصدار / المواصفة</th><th>الدور المعماري في المشروع</th></tr>
        </thead>
        <tbody>
            <tr><td><strong>Core Framework</strong></td><td>FastAPI (Async/Await)</td><td>&gt;= 0.110.0</td><td>بناء الخوادم غير المتزامنة عالية الأداء للطبقات الأربع</td></tr>
            <tr><td><strong>ASGI Server</strong></td><td>Uvicorn Standard</td><td>&gt;= 0.29.0</td><td>تشغيل الخوادم الخمسة مع بروتوكول L4 الخادع المخصص</td></tr>
            <tr><td><strong>Data Validation</strong></td><td>Pydantic v2 Core</td><td>&gt;= 2.7.0</td><td>توحيد عقود البيانات الصارمة في <code>shared_contracts</code></td></tr>
            <tr><td><strong>Session & Streams</strong></td><td>Redis 7 & fakeredis</td><td>&gt;= 5.0.0</td><td>تخزين حالات الجلسات فائقة السرعة وبث التنبيهات عبر Streams</td></tr>
            <tr><td><strong>Relational Database</strong></td><td>SQLAlchemy 2.0 + AsyncPG</td><td>&gt;= 2.0.30</td><td>التخزين الجنائي وسجلات الإنتاج مع Fallback إلى aiosqlite</td></tr>
            <tr><td><strong>Containerization</strong></td><td>Docker & Docker Compose</td><td>Engine v25+</td><td>عزل الشبكات الثلاث وحاويات الخداع المعزولة شبكياً</td></tr>
            <tr><td><strong>Cryptography</strong></td><td>PBKDF2-HMAC & RFC-7519</td><td>Native hashlib / hmac</td><td>تجزئة كلمات المرور (260 ألف دورة) وتوقيع توكنات JWT</td></tr>
            <tr><td><strong>Testing Engine</strong></td><td>Pytest + AnyIO</td><td>&gt;= 8.0.0</td><td>تنفيذ الاختبارات الشاملة (E2E Integration Test Suite)</td></tr>
        </tbody>
    </table>
</div>

<!-- PAGE 3: 4-LAYER ARCHITECTURE & DIAGRAM -->
<div class="page-break">
    <div class="doc-running-header">
        <span>FASTAPI DECEPTION ARCHITECTURE // MASTER SYSTEM GUIDE</span>
        <span>SECTION 2: المعمارية الهندسية ذات الطبقات الأربع</span>
    </div>

    <h1>2. المعمارية الهندسية ذات الطبقات الأربع (Four-Layer System Architecture)</h1>
    <p>
        تم بناء المنظومة على هيكلية طبقية مفصولة المسؤوليات (Separation of Concerns)، بحيث تنعزل شبكات المهاجمين المعزولين كلياً عن شبكات وتطبيقات الإنتاج:
    </p>

    <div class="diagram-container">
        {SVG_4LAYER_ARCHITECTURE}
        <div class="diagram-caption">شكل (1): المعمارية الهندسية ذات الطبقات الأربع وتدفق حركة المرور الشرعية مقابل المحتجزة</div>
    </div>

    <h2>2.1 تفصيل الطبقات الهندسية الأربع</h2>
    <div class="grid-2">
        <div class="card">
            <div class="card-title">الطبقة الأولى: بوابة الخداع وفحص المرور (Layer 1)</div>
            <p><strong>المسؤول: علي (Ali) — المنفذ: 8000</strong></p>
            <p>تمثل نقطة الدخول والمصد الدفاعي الأول للمنظومة عبر <code>deception_gateway</code>. تقوم بالتحقق اللحظي من حالة الجلسات عبر استعلام Redis في أجزاء من الميلي ثانية، وتفحص الحمولات الواردة لكشف التهديدات وتمرير المرور الشرعي إلى Layer 2 مع عزل المهاجمين في Layer 3.</p>
        </div>
        <div class="card">
            <div class="card-title">الطبقة الثانية: التطبيق الحقيقي ومحقن الشراك (Layer 2)</div>
            <p><strong>المسؤول: يوسف (App) وعمار (Injector) — المنفذ: 8001</strong></p>
            <p>تستضيف خدمات الويب المؤسسية الحقيقية والمصادقة المشددة <code>core_web_app</code>. ترتبط بها طبقة وسيطة <code>honey_token_injector</code> تحقن ترويسات وروابط خادعة وموقعة رقمياً بـ HMAC داخل ردود التطبيق الطبيعية لخداع المهاجمين.</p>
        </div>
        <div class="card">
            <div class="card-title">الطبقة الثالثة: بيئة العزل ومحرك التحقيق الجنائي (Layer 3)</div>
            <p><strong>المسؤول: عمار (Ammar) — المنافذ: 8080 و 8090</strong></p>
            <p>تدير مجمع حاويات العزل السريعة <code>isolation_sandbox</code> المعزولة شبكياً، مع خادم خادع تفاعلي ومحاكي لينكس. يعمل بالتوازي معها محرك الأدلة الجنائية <code>forensic_extraction_engine</code> لتسجيل الأوامر وحزم PCAP وسلسلة العهدة المشفرة.</p>
        </div>
        <div class="card">
            <div class="card-title">الطبقة الرابعة: التخزين وغرفة العمليات (Layer 4)</div>
            <p><strong>المسؤول: يوسف (Storage) وعمار (SOC) — المنفذ: 8500</strong></p>
            <p>توفر مستودعات التخزين غير المتزامنة في Redis و PostgreSQL لحفظ الأدلة وسجلات الحوادث. تغذي مباشرة لوحة تحكم مركز العمليات الأمنية <code>soc_dashboard</code> المزودة بالبث اللحظي بالـ WebSockets وخريطة MITRE ATT&CK وأزرار SOAR.</p>
        </div>
    </div>
</div>

<!-- PAGE 4: REQUEST LIFECYCLE & SEQUENCE -->
<div class="page-break">
    <div class="doc-running-header">
        <span>FASTAPI DECEPTION ARCHITECTURE // MASTER SYSTEM GUIDE</span>
        <span>SECTION 3: دورة حياة الطلب ومسارات الحركة</span>
    </div>

    <h1>3. دورة حياة الطلب (Request Lifecycle Analysis)</h1>
    <p>
        يتبع النظام استراتيجية فرز حتمية مبنية على الحالة (State-Driven Deterministic Routing). يوضح الجدول والمخطط أدناه الفرق الجوهري بين تدفق طلب المستخدم الشرعي وطلب المهاجم:
    </p>

    <table>
        <thead>
            <tr><th>مرحلة التدفق</th><th>مسار المستخدم الشرعي (Legitimate Path)</th><th>مسار المهاجم المحتجز (Trapped Attacker Path)</th></tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>1. نقطة الدخول</strong></td>
                <td>يصل الطلب إلى البوابة: <code>GET /api/v1/records</code></td>
                <td>يصل الطلب إلى البوابة متضمناً شِركاً: <code>GET /api/v1/internal/vault-keys</code></td>
            </tr>
            <tr>
                <td><strong>2. فحص Redis</strong></td>
                <td>تستعلم البوابة من <code>redis_cache_verifier</code>: الجلسة نظيفة (Clean).</td>
                <td>تستعلم البوابة: إذا كانت الجلسة معزولة مسبقاً، تُحول فوراً بدون فحص جديد.</td>
            </tr>
            <tr>
                <td><strong>3. كشف التهديدات</strong></td>
                <td>يفحص <code>attack_detector</code> الترويسات والحمولة: لا توجد مؤشرات هجوم.</td>
                <td>يكتشف <code>attack_detector</code> التوكن الخادع أو بصمة هجومية (SQLi/L4 Scan).</td>
            </tr>
            <tr>
                <td><strong>4. تصعيد الحالة</strong></td>
                <td>لا يحدث أي تصعيد؛ الـ Risk Score يبقى 0.0.</td>
                <td>يُصعد الـ Risk Score إلى 100.0، والحالة إلى <code>MALICIOUS_TRAPPED</code>.</td>
            </tr>
            <tr>
                <td><strong>5. نشر التنبيه</strong></td>
                <td>لا يصدر أي تنبيه؛ استمرار الهدوء الأمني.</td>
                <td>يُبث تنبيه فوري عبر Redis Streams إلى لوحة الـ SOC (وميض أحمر بالـ WebSocket).</td>
            </tr>
            <tr>
                <td><strong>6. توجيه الطلب</strong></td>
                <td>يُوجه الطلب إلى التطبيق الحقيقي <code>CORE_WEB_APP</code> (منفذ 8001).</td>
                <td>يُوجه الطلب فوراً إلى الحاوية المعزولة <code>PREWARMED_SANDBOX</code> (منفذ 8080).</td>
            </tr>
            <tr>
                <td><strong>7. معالجة الرد</strong></td>
                <td>يُرجع التطبيق السجلات الحقيقية من قاعدة بيانات الإنتاج.</td>
                <td>يُرجع الخادم الخادع بيانات مفاتيح مشفرة ومصطنعة (Decoy Vault Keys).</td>
            </tr>
            <tr>
                <td><strong>8. التعزيز بالشراك</strong></td>
                <td>يحقن <code>HoneyTokenInjector</code> ترويسات وروابط خادعة داخل الرد الشرعي.</td>
                <td>لا يتم حقن شراك إضافية؛ بل يتم تثبيت المهاجم داخل بيئة العزل وتتبع أوامره.</td>
            </tr>
            <tr>
                <td><strong>9. التحقيق الجنائي</strong></td>
                <td>لا يتم التقاط أي أدلة جنائية.</td>
                <td>يسجل محرك التحقيق الجنائي أوامر الشل، وحزم PCAP، وسلسلة العهدة المشفرة.</td>
            </tr>
        </tbody>
    </table>

    <div class="alert-box alert-crit">
        <div class="alert-title">🔒 مبدأ العزل المطلق لشبكة الاحتجاز (Air-Gapped Sandbox Network)</div>
        الحاويات الخادعة داخل <code>sandbox_containment_net</code> مُعرفة في Docker Compose بخيار <code>internal: true</code>. هذا يعني هندسياً وقانونياً:
        1) لا يمكن للمهاجم الخروج للإنترنت أو إطلاق هجمات DDoS.
        2) لا يمكن للمهاجم الوصول إلى قاعدة بيانات الإنتاج أو سيرفر الـ SOC.
        3) أي محاولة اتصال خارجي يتم اعتراضها داخلياً عبر محاكي C2 لجمع أدوات المهاجم دون تسريب أي بيانات.
    </div>
</div>

<!-- PAGE 5: TEAM STRUCTURE & WORK BREAKDOWN -->
<div class="page-break">
    <div class="doc-running-header">
        <span>FASTAPI DECEPTION ARCHITECTURE // MASTER SYSTEM GUIDE</span>
        <span>SECTION 4: الهيكلية التنظيمية ومصفوفة المهام العامة</span>
    </div>

    <h1>4. الهيكلية التنظيمية للفريق وتوزيع المسؤوليات (Team Architecture)</h1>
    <p>
        تم تقسيم المشروع بدقة بين المهندسين الأربعة لضمان ملكية برمجية مستقلة لكل ملف، مع تكامل وظيفي محكم:
    </p>

    <table>
        <thead>
            <tr><th>المهندس</th><th>المسمى التخصصي</th><th>المكونات والملفات المملوكة</th><th>المهام الرئيسية والتسليمات</th></tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>سجاد (Sadjad)</strong></td>
                <td>Team Leader &amp;<br>System Architect</td>
                <td>
                    <code>run_all.py</code><br>
                    <code>main.py</code><br>
                    <code>docker-compose.yml</code><br>
                    <code>START_PROJECT.bat</code><br>
                    <code>tests/test_architecture_e2e.py</code><br>
                    <code>shared_contracts/</code>
                </td>
                <td>
                    • القيادة المعمارية وتنسيق الخوادم الخمسة.<br>
                    • إدارة البنية التحتية والشبكات المعزولة.<br>
                    • إدارة ومراجعة جودة الكود والدمج عبر Git.<br>
                    • الإشراف على جناح الاختبارات الشاملة.<br>
                    • قيادة سيناريو العرض الحي أمام اللجنة.
                </td>
            </tr>
            <tr>
                <td><strong>علي (Ali)</strong></td>
                <td>Backend &amp; Deception<br>Gateway Engineer</td>
                <td>
                    <code>deception_gateway/main.py</code><br>
                    <code>deception_gateway/gateway_router.py</code><br>
                    <code>deception_gateway/traffic_classifier.py</code><br>
                    <code>deception_gateway/attack_detector.py</code><br>
                    <code>deception_gateway/malicious_session_router.py</code><br>
                    <code>deception_gateway/redis_cache_verifier.py</code>
                </td>
                <td>
                    • حراسة البوابة وتصنيف حركة المرور اللحظي.<br>
                    • كشف هجمات SQLi والمسارات الحساسة وأدوات الفحص.<br>
                    • تطوير بروتوكول <code>TCPL4DeceptionProtocol</code>.<br>
                    • توجيه الجلسات المحتجزة والخداع المدمج البديل.
                </td>
            </tr>
            <tr>
                <td><strong>يوسف (Yousif)</strong></td>
                <td>Core Application &amp;<br>Data Engineer</td>
                <td>
                    <code>core_web_app/main.py</code><br>
                    <code>core_web_app/legitimate_request_routes.py</code><br>
                    <code>core_web_app/authentication/*</code><br>
                    <code>core_web_app/database_connector/*</code><br>
                    <code>data_storage/postgresql_store/*</code><br>
                    <code>data_storage/redis_store/*</code>
                </td>
                <td>
                    • بناء التطبيق الحقيقي ومسارات الأعمال المؤسسية.<br>
                    • تشفير PBKDF2 (260 ألف دورة) وتوليد رموز JWT.<br>
                    • عزل جداول الإنتاج عن جداول الأدلة الجنائية.<br>
                    • إدارة قواعد بيانات PostgreSQL و Redis ومحركات Fallback.
                </td>
            </tr>
            <tr>
                <td><strong>عمار (Ammar)</strong></td>
                <td>Honeypot, Sandbox &amp;<br>Forensics Engineer</td>
                <td>
                    <code>honey_token_injector/*</code><br>
                    <code>isolation_sandbox/*</code><br>
                    <code>forensic_extraction_engine/*</code><br>
                    <code>soc_dashboard/*</code><br>
                    <code>templates/index.html</code>
                </td>
                <td>
                    • توليد وتدقيق الشراك الخداعية الموقعة بـ HMAC.<br>
                    • مجمع حاويات العزل السريعة بزمن استجابة صفر.<br>
                    • فك تعتيم الأوامر ومطابقة MITRE ATT&CK.<br>
                    • اقتناص PCAP ومجسات eBPF وبناء سلسلة العهدة.<br>
                    • تطوير لوحة مركز العمليات ومصيدة البحث في المتجر.
                </td>
            </tr>
        </tbody>
    </table>
</div>

<!-- PAGE 6: TESTING, VERIFICATION & GRADUATION DEFENSE -->
<div class="page-break">
    <div class="doc-running-header">
        <span>FASTAPI DECEPTION ARCHITECTURE // MASTER SYSTEM GUIDE</span>
        <span>SECTION 5: الاختبارات وجلسة مناقشة التخرج</span>
    </div>

    <h1>5. استراتيجية الاختبارات والتأهيل ليوم المناقشة النهائي</h1>

    <h2>5.1 نتائج جناح الاختبارات الشاملة (E2E Verification Evidence)</h2>
    <p>تم اختبار النظام برمجياً عبر الأمر المعتمد <code>pytest</code> واجتاز بنسبة 100%:</p>
    
    <div class="code-block">
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\\Users\\Marhaba\\Downloads\\fastapi-deception-architecture-main
configfile: pytest.ini
collected 5 items

fastapi-deception-architecture-main\\tests\\test_architecture_e2e.py ..... [100%]
======================== 5 passed, 1 warning in 8.62s =========================
    </div>

    <h2>5.2 سيناريو العرض الحي أمام لجنة المناقشة (Live Defense Script)</h2>
    <ol>
        <li><strong>التشغيل الفوري</strong>: فتح المشروع والضغط على <code>START_PROJECT.bat</code> لعرض تشغيل الخدمات الخمس المتزامنة.</li>
        <li><strong>استعراض الهدوء الأمني</strong>: فتح لوحة الـ SOC على <code>http://127.0.0.1:8500/admin/soc</code> لإظهار العدادات الصفرية.</li>
        <li><strong>استعراض الشرك الخادع</strong>: فتح <code>http://127.0.0.1:8000/api/v1/records</code> وإظهار الترويسات التي حُقن فيها التوكن الخادع <code>X-Internal-Debug-Token</code>.</li>
        <li><strong>شن الهجوم واستدراج المهاجم</strong>: فتح الرابط الخادع <code>http://127.0.0.1:8000/api/v1/internal/vault-keys</code>، وإظهار وميض الإنذار الأحمر في لوحة الـ SOC عبر الـ WebSocket في نفس اللحظة!</li>
        <li><strong>تنفيذ أمر شل في العزل</strong>: طلب الشل <code>http://127.0.0.1:8000/api/v1/internal/debug-console?cmd=whoami%20%26%26%20cat%20/etc/shadow</code> وإظهار الرد الخادع الواقعي.</li>
        <li><strong>الإثبات القانوني لسلسلة العهدة</strong>: فتح مسار تدقيق العهدة وإظهار تحقق التوقيع الرياضي <code>overall_integrity_verified: true</code> واستعراض ملف الـ PCAP وملف الـ eBPF الناتجين.</li>
    </ol>
</div>

</body>
</html>
"""
