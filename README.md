<div align="center">

# 🔌 MNAM Backend API | خادم منَام

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red?style=flat-square)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)

</div>

---

## 📖 نظرة عامة

خادم REST API لنظام إدارة العقارات والحجوزات، مبني بـ FastAPI مع PostgreSQL. يتضمن محرك تسعير ديناميكي وتكامل مع قنوات الحجز (Channex).

---

## 🏗️ هيكل المشروع

```
mnam-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # نقطة الدخول
│   ├── config.py            # إعدادات التطبيق
│   ├── database.py          # اتصال قاعدة البيانات
│   │
│   ├── models/              # نماذج SQLAlchemy
│   │   ├── user.py          # المستخدمين والصلاحيات
│   │   ├── owner.py         # الملاك
│   │   ├── project.py       # المشاريع
│   │   ├── unit.py          # الوحدات
│   │   ├── booking.py       # الحجوزات
│   │   ├── customer.py      # العملاء
│   │   ├── transaction.py   # المعاملات المالية
│   │   ├── pricing.py       # 🆕 سياسات التسعير
│   │   ├── channel_integration.py  # 🆕 تكامل القنوات
│   │   └── employee_performance.py  # أداء الموظفين
│   │
│   ├── routers/             # API Endpoints
│   │   ├── auth.py          # المصادقة
│   │   ├── users.py         # إدارة المستخدمين
│   │   ├── owners.py        # إدارة الملاك
│   │   ├── projects.py      # إدارة المشاريع
│   │   ├── units.py         # إدارة الوحدات
│   │   ├── bookings.py      # إدارة الحجوزات
│   │   ├── customers.py     # إدارة العملاء
│   │   ├── transactions.py  # المعاملات المالية
│   │   ├── dashboard.py     # ملخص لوحة التحكم
│   │   ├── ai.py            # المساعد الذكي
│   │   ├── pricing.py       # 🆕 محرك التسعير
│   │   ├── integrations.py  # 🆕 تكامل Channex
│   │   └── employee_performance.py  # أداء الموظفين
│   │
│   ├── schemas/             # Pydantic Schemas
│   │   ├── pricing.py       # 🆕 schemas التسعير
│   │   └── integration.py   # 🆕 schemas التكامل
│   │
│   ├── services/            # منطق الأعمال
│   │   ├── pricing_engine.py     # 🆕 محرك التسعير
│   │   ├── channex_client.py     # 🆕 عميل Channex API
│   │   ├── channex_webhook.py    # 🆕 معالج Webhooks
│   │   └── outbox_worker.py      # 🆕 معالج الأحداث
│   │
│   └── utils/               # أدوات مساعدة
│       ├── security.py      # تشفير وJWT
│       ├── dependencies.py  # FastAPI Dependencies
│       └── rate_limiter.py  # Rate Limiting
│
├── alembic/                 # Alembic migrations
├── tests/                   # 🆕 اختبارات
├── docs/                    # 🆕 وثائق التصميم
├── requirements.txt         # المتطلبات
├── Procfile                 # Railway deployment
└── railway.json             # إعدادات Railway
```

---

## 📊 نماذج البيانات

### User (المستخدم)
```python
- id, username, email, hashed_password
- first_name, last_name, phone
- role: system_owner | admin | owners_agent | customers_agent
- is_active, is_system_owner
```

### Owner (المالك)
```python
- id, owner_name, owner_mobile_phone
- paypal_email, note
- projects (relationship)
```

### Project (المشروع)
```python
- id, owner_id, name
- city, district, map_url
- contract_no, contract_status, contract_duration
- commission_percent, bank_name, bank_iban
- units (relationship)
- channel_connections (relationship)  # 🆕
```

### Unit (الوحدة)
```python
- id, project_id, unit_name, unit_type
- rooms, floor_number, unit_area
- status: متاحة | محجوزة | صيانة | ...
- price_days_of_week, price_in_weekends
- amenities, description, permit_no
- pricing_policy (relationship)     # 🆕 تُنشأ تلقائياً
- external_mappings (relationship)  # 🆕
```

#### 🆕 إنشاء سياسة التسعير تلقائياً
عند إنشاء/تعديل وحدة، يتم إنشاء `PricingPolicy` تلقائياً:
```json
POST /api/units/
{
  "unit_name": "شقة 101",
  "price_days_of_week": 100,
  "price_in_weekends": 250,
  // حقول التسعير الجديدة (اختياري)
  "base_weekday_price": 100,
  "weekend_markup_percent": 150,
  "discount_16_percent": 10,
  "discount_21_percent": 20,
  "discount_23_percent": 30
}
```

### Booking (الحجز)
```python
- id, unit_id, customer_id
- guest_name, guest_phone, guest_email
- check_in_date, check_out_date
- total_price, status, notes
- channel_source, external_reservation_id  # 🆕 تتبع الحجوزات الخارجية
```

### Customer (العميل)
```python
- id, name, phone (unique - normalized Saudi format)
- email, gender
- booking_count, completed_booking_count, total_revenue
- is_banned, ban_reason
- is_profile_complete
```

### 🆕 PricingPolicy (سياسة التسعير)
```python
- unit_id (1:1 مع Unit)
- base_weekday_price         # السعر الأساسي لأيام الأسبوع
- weekend_markup_percent     # نسبة زيادة نهاية الأسبوع
- discount_16_percent        # خصم من الساعة 16:00
- discount_21_percent        # خصم من الساعة 21:00
- discount_23_percent        # خصم من الساعة 23:00
- timezone                   # المنطقة الزمنية (Asia/Riyadh)
- weekend_days               # أيام نهاية الأسبوع (4,5 للسعودية)
```

### 🆕 ChannelConnection (اتصال القناة)
```python
- project_id
- provider: "channex"
- api_key, channex_property_id
- status: active | inactive | error
```

### 🆕 ExternalMapping (ربط خارجي)
```python
- connection_id, unit_id
- channex_room_type_id, channex_rate_plan_id
```

---

## 🧮 محرك التسعير الديناميكي

### الصيغة الحسابية

```
base = base_weekday_price (مثال: 100 ريال)

day_price = base if is_weekday else base * (1 + weekend_markup% / 100)
    → مثال: 100 * 2.5 = 250 ريال (بزيادة 150%)

active_discount = حسب الوقت المحلي:
    - قبل 16:00  → 0%
    - 16:00-20:59 → discount_16_percent
    - 21:00-22:59 → discount_21_percent
    - 23:00-23:59 → discount_23_percent

final_price = round(day_price * (1 - active_discount% / 100), 2)
    → مثال: 250 * 0.90 = 225 ريال (بخصم 10%)
```

### مثال عملي

| الوقت | اليوم | السعر الأساسي | الزيادة | الخصم | السعر النهائي |
|-------|-------|---------------|---------|-------|---------------|
| 10:00 | الأحد | 100 | - | - | **100 ريال** |
| 10:00 | الجمعة | 100 | +150% | - | **250 ريال** |
| 18:00 | الجمعة | 100 | +150% | -10% | **225 ريال** |
| 22:00 | الجمعة | 100 | +150% | -20% | **200 ريال** |

---

## 🔗 تكامل Channex

### تدفق البيانات

```
📤 Outbound (MNAM → Channex):
   تحديث الأسعار ← PricingPolicy تتغير
   تحديث التوفر ← Booking يُنشأ/يُلغى
   
📥 Inbound (Channex → MNAM):
   Webhook → حجز جديد من Airbnb/Booking.com
   Webhook → تعديل حجز
   Webhook → إلغاء حجز
```

### Webhook Endpoint
```
POST /api/integrations/channex/webhook
```

---

## 🔐 نظام الصلاحيات

```
👑 system_owner (4) - كل الصلاحيات
    │
    └── 🔑 admin (3) - كل شي ما عدا System Owner
            │
            └── 👔 owners_agent (2) - الملاك، المشاريع، الوحدات
                    │
                    └── 👤 customers_agent (1) - الوحدات + الحجوزات
```

---

## 🚀 التشغيل

### متطلبات
- Python 3.10+
- PostgreSQL 13+

### التثبيت
```bash
# إنشاء بيئة افتراضية
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# تثبيت المتطلبات
pip install -r requirements.txt
```

### متغيرات البيئة (`.env`)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/mnam_db
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=development
```

### تشغيل الخادم
```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 🌐 API Endpoints

### 🔐 Auth
| Method | Endpoint | الوصف |
|--------|----------|-------|
| POST | `/api/auth/login` | تسجيل الدخول |
| POST | `/api/auth/refresh` | تجديد الجلسة |
| POST | `/api/auth/logout` | تسجيل الخروج |
| GET | `/api/auth/me` | بيانات المستخدم الحالي |

### 👥 Users
| Method | Endpoint | الوصف |
|--------|----------|-------|
| GET | `/api/users/` | قائمة المستخدمين |
| POST | `/api/users/` | إنشاء مستخدم |
| PUT | `/api/users/{id}` | تعديل مستخدم |
| DELETE | `/api/users/{id}` | حذف مستخدم |

### � 💰 Pricing (التسعير)
| Method | Endpoint | الوصف |
|--------|----------|-------|
| POST | `/api/pricing/policies` | إنشاء سياسة تسعير |
| GET | `/api/pricing/policies/{unit_id}` | جلب سياسة الوحدة |
| PUT | `/api/pricing/policies/{unit_id}` | تحديث السياسة |
| GET | `/api/pricing/calendar/{unit_id}` | تقويم الأسعار |
| GET | `/api/pricing/realtime/{unit_id}` | السعر اللحظي |
| POST | `/api/pricing/calculate-booking` | حساب إجمالي الحجز |

### � 🔗 Integrations (التكامل)
| Method | Endpoint | الوصف |
|--------|----------|-------|
| POST | `/api/integrations/connections` | إنشاء اتصال |
| GET | `/api/integrations/connections/{id}/health` | صحة الاتصال |
| POST | `/api/integrations/connections/{id}/sync` | مزامنة يدوية |
| POST | `/api/integrations/mappings` | ربط وحدة |
| POST | `/api/integrations/channex/webhook` | استقبال Webhooks |
| GET | `/api/integrations/outbox` | أحداث قيد الانتظار |
| GET | `/api/integrations/logs` | سجلات التكامل |

### 📊 Dashboard
| Method | Endpoint | الوصف |
|--------|----------|-------|
| GET | `/api/dashboard/summary` | ملخص لوحة التحكم |

---

## 📚 API Documentation

بعد تشغيل الخادم، الوثائق التفاعلية متاحة على:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧪 الاختبارات

```bash
# تشغيل جميع الاختبارات
pytest tests/ -v

# اختبار محرك التسعير
pytest tests/test_pricing_engine.py -v

# اختبار Webhooks
pytest tests/test_channex_webhook.py -v
```

---

## 🚀 النشر على Railway

### Procfile
```
web: alembic upgrade head && gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

### متغيرات البيئة على Railway
1. `DATABASE_URL` - من PostgreSQL service
2. `SECRET_KEY` - مفتاح سري قوي
3. `ALGORITHM` - HS256
4. `ACCESS_TOKEN_EXPIRE_MINUTES` - 1440
5. `REFRESH_TOKEN_EXPIRE_DAYS` - 7
6. `ENVIRONMENT` - production

---

## 🗄️ DB Migrations

### إضافة Migration جديد
```bash
# Windows
migrate.bat new "add_new_column"

# أو مباشرة
alembic revision --autogenerate -m "add_new_column"
```

### أوامر مفيدة
```bash
alembic upgrade head       # تطبيق كل migrations
alembic downgrade -1       # التراجع migration واحد
alembic current            # عرض الحالة الحالية
alembic history            # عرض التاريخ
```

---

## 👤 المستخدمين الافتراضيين

| Username | Password | Role |
|----------|----------|------|
| Head_Admin | H112as112! | system_owner |
| admin | Admin123! | admin |

---

<div align="center">

**جزء من نظام مِنَام العقاري 🏠**

</div>
# mnam-backend
