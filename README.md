# mnam-backend

نظام Backend لإدارة العقارات والحجوزات باستخدام FastAPI + SQLAlchemy

## 🚀 التشغيل السريع

### 1. إنشاء البيئة الافتراضية
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# أو
source venv/bin/activate  # Linux/Mac
```

### 2. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 3. تشغيل السيرفر
```bash
uvicorn app.main:app --reload
```

### 4. فتح التوثيق
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 هيكل المشروع
```
mnam-backend/
├── app/
│   ├── main.py           # نقطة الدخول
│   ├── config.py         # الإعدادات
│   ├── database.py       # قاعدة البيانات
│   ├── models/           # نماذج SQLAlchemy
│   ├── schemas/          # Pydantic schemas
│   ├── routers/          # API endpoints
│   └── utils/            # أدوات مساعدة
├── .env                  # متغيرات البيئة
└── requirements.txt      # المتطلبات
```

## 🔐 المصادقة
- المستخدم الافتراضي: `admin` / `admin`
- JWT tokens للمصادقة
- Role-based access (admin/agent)

## 📝 API Endpoints
- `/api/auth` - المصادقة
- `/api/users` - المستخدمين
- `/api/owners` - الملاك
- `/api/projects` - المشاريع
- `/api/units` - الوحدات
- `/api/bookings` - الحجوزات
- `/api/transactions` - المعاملات المالية
- `/api/dashboard` - لوحة التحكم
- `/api/ai` - الذكاء الاصطناعي
