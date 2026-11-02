# Todo List API

یک API REST ساده برای مدیریت کارهای روزانه، ساخته‌شده با Python، Django و Django REST Framework.
ذخیره‌سازی داده‌ها در SQLite انجام می‌شود و فرانت‌اند ندارد؛ همه قابلیت‌ها از طریق API در دسترس‌اند.

## امکانات

- ساخت، دریافت فهرست، دریافت جزئیات، ویرایش کامل و جزئی و حذف کار
- تغییر وضعیت انجام کار با یک درخواست (toggle)
- اعتبارسنجی عنوان (خالی یا بیش از ۲۰۰ کاراکتر مجاز نیست)
- پاسخ ۴۰۴ برای شناسه‌های ناموجود
- ثبت مدل Task در پنل Admin
- ۱۹ تست خودکار

## پیش‌نیازها

- Python 3.12 یا بالاتر
- Git

## نصب

```bash
git clone <آدرس-مخزن>
cd django-todo

python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
```

## اجرا

```bash
python manage.py runserver
```

سرور روی `http://127.0.0.1:8000/` بالا می‌آید و صفحه اصلی به `/api/` منتقل می‌شود.

برای دسترسی به پنل Admin:

```bash
python manage.py createsuperuser
```

سپس به `http://127.0.0.1:8000/admin/` بروید.

## اجرای تست‌ها

```bash
python manage.py test
```

## Endpointها

| متد | آدرس | عملکرد | کد موفق |
|---|---|---|---|
| GET | `/api/tasks/` | دریافت فهرست کارها | 200 |
| POST | `/api/tasks/` | ایجاد کار جدید | 201 |
| GET | `/api/tasks/<id>/` | دریافت جزئیات یک کار | 200 |
| PUT | `/api/tasks/<id>/` | ویرایش کامل | 200 |
| PATCH | `/api/tasks/<id>/` | ویرایش بخشی | 200 |
| DELETE | `/api/tasks/<id>/` | حذف کار | 204 |
| PATCH | `/api/tasks/<id>/toggle/` | تغییر وضعیت انجام کار | 200 |

## مدل Task

| فیلد | نوع | توضیح |
|---|---|---|
| id | AutoField | شناسه خودکار |
| title | CharField(200) | عنوان، اجباری |
| description | TextField | توضیحات، اختیاری |
| is_completed | BooleanField | پیش‌فرض False |
| created_at | DateTimeField | زمان ایجاد (خودکار) |
| updated_at | DateTimeField | زمان آخرین ویرایش (خودکار) |

## نمونه درخواست‌ها و پاسخ‌ها

مثال‌ها با `curl.exe` در Windows نوشته شده‌اند. در Linux/macOS به‌جای `curl.exe` از `curl` و به‌جای بدنه داخل `"..."` با `\"` ، از بدنه داخل `'...'` استفاده کنید، مثلاً:
`-d '{"title": "Learn Django"}'`

مقدارهای `id` و تاریخ‌ها در اجرای شما متفاوت خواهند بود.

### ایجاد کار

```bash
curl.exe -i -X POST http://127.0.0.1:8000/api/tasks/ -H "Content-Type: application/json" -d "{\"title\": \"Learn Django\", \"description\": \"Finish the tutorial\"}"
```

پاسخ `201 Created`:

```http
HTTP/1.1 201 Created
Content-Type: application/json
Allow: GET, POST, HEAD, OPTIONS
```

```json
{
  "id": 7,
  "title": "Learn Django",
  "description": "Finish the tutorial",
  "is_completed": false,
  "created_at": "2026-11-02T23:11:34.433687Z",
  "updated_at": "2026-11-02T23:11:34.434688Z"
}
```

### دریافت فهرست

```bash
curl.exe -i http://127.0.0.1:8000/api/tasks/
```

پاسخ `200 OK`: آرایه‌ای از کارها (جدیدترین اول).

```http
HTTP/1.1 200 OK
Content-Type: application/json
Allow: GET, POST, HEAD, OPTIONS
```

```json
[
  {
    "id": 7,
    "title": "Learn Django",
    "description": "Finish the tutorial",
    "is_completed": false,
    "created_at": "2026-11-02T23:11:34.433687Z",
    "updated_at": "2026-11-02T23:11:34.434688Z"
  },
  {
    "id": 6,
    "title": "test curl",
    "description": "from curl",
    "is_completed": false,
    "created_at": "2026-10-31T22:44:16.496224Z",
    "updated_at": "2026-10-31T22:44:16.497223Z"
  },
  {
    "id": 2,
    "title": "test2",
    "description": "this is test2",
    "is_completed": true,
    "created_at": "2026-10-31T19:23:17.974191Z",
    "updated_at": "2026-11-02T18:59:20.043235Z"
  }
]
```

### دریافت جزئیات

```bash
curl.exe -i http://127.0.0.1:8000/api/tasks/2/
```

پاسخ `200 OK`:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
```

```json
{
  "id": 2,
  "title": "test2",
  "description": "this is test2",
  "is_completed": true,
  "created_at": "2026-10-31T19:23:17.974191Z",
  "updated_at": "2026-11-02T18:59:20.043235Z"
}
```

### ویرایش کامل (PUT)

در PUT باید همه فیلدهای اجباری (حداقل `title`) ارسال شوند.

```bash
curl.exe -i -X PUT http://127.0.0.1:8000/api/tasks/2/ -H "Content-Type: application/json" -d "{\"title\": \"Learn DRF\", \"description\": \"Serializers and ViewSets\", \"is_completed\": true}"
```

پاسخ `200 OK` همراه با کار به‌روزشده:

```json
{
  "id": 2,
  "title": "Learn DRF",
  "description": "Serializers and ViewSets",
  "is_completed": true,
  "created_at": "2026-10-31T19:23:17.974191Z",
  "updated_at": "2026-11-02T23:21:22.703737Z"
}
```

### ویرایش بخشی (PATCH)

فقط فیلدهای ارسال‌شده تغییر می‌کنند.

```bash
curl.exe -i -X PATCH http://127.0.0.1:8000/api/tasks/2/ -H "Content-Type: application/json" -d "{\"is_completed\": true}"
```

پاسخ `200 OK`:

```json
{
  "id": 2,
  "title": "Learn DRF",
  "description": "Serializers and ViewSets",
  "is_completed": true,
  "created_at": "2026-10-31T19:23:17.974191Z",
  "updated_at": "2026-11-02T23:27:41.525820Z"
}
```

### تغییر وضعیت انجام کار (toggle)

بدون بدنه؛ وضعیت `is_completed` برعکس می‌شود.

```bash
curl.exe -i -X PATCH http://127.0.0.1:8000/api/tasks/2/toggle/
```

پاسخ `200 OK` (در این مثال کار از «انجام‌شده» به «انجام‌نشده» تغییر کرده است):

```http
HTTP/1.1 200 OK
Content-Type: application/json
Allow: PATCH, OPTIONS
```

```json
{
  "id": 2,
  "title": "Learn DRF",
  "description": "Serializers and ViewSets",
  "is_completed": false,
  "created_at": "2026-10-31T19:23:17.974191Z",
  "updated_at": "2026-11-02T23:28:58.328446Z"
}
```

### حذف

```bash
curl.exe -i -X DELETE http://127.0.0.1:8000/api/tasks/7/
```

پاسخ `204 No Content` (بدون بدنه):

```http
HTTP/1.1 204 No Content
```

### خطای اعتبارسنجی

```bash
curl.exe -i -X POST http://127.0.0.1:8000/api/tasks/ -H "Content-Type: application/json" -d "{\"title\": \"\"}"
```

پاسخ `400 Bad Request`:

```json
{"title": ["This field may not be blank."]}
```

### شناسه ناموجود

```bash
curl.exe -i http://127.0.0.1:8000/api/tasks/9999/
```

پاسخ `404 Not Found`:

```json
{"detail": "No Task matches the given query."}
```

## ساختار پروژه

```
django-todo/
├── config/            # تنظیمات پروژه (settings, urls)
├── tasks/
│   ├── migrations/    # Migrationهای دیتابیس
│   ├── admin.py       # ثبت مدل در Admin
│   ├── models.py      # مدل Task
│   ├── serializers.py # TaskSerializer و اعتبارسنجی
│   ├── views.py       # TaskViewSet و اکشن toggle
│   ├── urls.py        # Router
│   └── tests.py       # تست‌های API
├── manage.py
├── requirements.txt
└── README.md
```