# 🚀 Deployment Guide - Streamlit Cloud

## ✅ متطلبات الـ Deploy

تم رفع المشروع بنجاح على GitHub: https://github.com/Madow2026/ksa-projects

---

## 📦 طريقة الـ Deploy على Streamlit Cloud (مجاناً)

### الخطوة 1️⃣: إنشاء حساب Streamlit Cloud

1. اذهب إلى: https://share.streamlit.io/
2. اضغط **Sign up** أو **Continue with GitHub**
3. قم بتسجيل الدخول باستخدام حساب GitHub الخاص بك (Madow2026)

### الخطوة 2️⃣: Deploy التطبيق

1. بعد تسجيل الدخول، اضغط **"New app"**
2. املأ البيانات التالية:
   ```
   Repository: Madow2026/ksa-projects
   Branch: main
   Main file path: app.py
   ```
3. اضغط **"Deploy!"**

### الخطوة 3️⃣: إضافة Secrets (API Keys)

1. في صفحة التطبيق، اضغط على **Settings** (⚙️)
2. اضغط على **Secrets** في القائمة الجانبية
3. أضف الـ secrets التالية:

```toml
# نسخ المحتوى من .streamlit/secrets.toml.example
OPENAI_API_KEY = "your_actual_openai_api_key_here"

# يمكن ترك الباقي كما هو
DATABASE_URL = "sqlite:///data/projects.db"
APP_MODE = "production"
DEBUG = false
AI_MODEL = "gpt-4-turbo-preview"
AI_TEMPERATURE = 0.3
CONFIDENCE_THRESHOLD = 0.7
SCRAPING_ENABLED = true
```

4. اضغط **Save**

### الخطوة 4️⃣: انتظر حتى يكتمل الـ Deploy

- سيستغرق الأمر 3-5 دقائق
- ستظهر لك رسالة **"Your app is live!"**
- سيكون الرابط بهذا الشكل:
  ```
  https://madow2026-ksa-projects-app-xxxxxx.streamlit.app
  ```

---

## 🌐 طرق Deploy أخرى

### 2️⃣ Deploy على Heroku

```bash
# تثبيت Heroku CLI
# إنشاء Procfile
echo "web: streamlit run app.py" > Procfile

# Deploy
heroku create ksa-projects
git push heroku main
heroku open
```

### 3️⃣ Deploy باستخدام Docker

```dockerfile
# Dockerfile موجود بالفعل في المشروع
docker build -t ksa-projects .
docker run -p 8501:8501 ksa-projects
```

### 4️⃣ Deploy على AWS/Azure/GCP

راجع [ARCHITECTURE.md](ARCHITECTURE.md) للتفاصيل

---

## 🔑 الحصول على OpenAI API Key

1. اذهب إلى: https://platform.openai.com/
2. سجل دخول أو أنشئ حساب جديد
3. اذهب إلى **API Keys**: https://platform.openai.com/api-keys
4. اضغط **"Create new secret key"**
5. انسخ المفتاح وأضفه في Streamlit Secrets

> ⚠️ **ملاحظة**: يمكن تشغيل التطبيق بدون OpenAI API Key (سيستخدم AI بسيط بدلاً من GPT-4)

---

## ✅ بعد الـ Deploy

### اختبار التطبيق

1. افتح رابط التطبيق
2. قم بتشغيل Demo Data:
   - افتح **Terminal** في Streamlit Cloud
   - نفذ: `python utils/demo_data.py`
3. اضغط **"Run Pipeline"** في الـ sidebar
4. شاهد البيانات على الـ Dashboard

### مشاركة التطبيق

شارك الرابط مع فريقك:
```
https://your-app-name.streamlit.app
```

---

## 🔧 تحديث التطبيق

عند إضافة تغييرات جديدة:

```bash
git add .
git commit -m "وصف التغيير"
git push origin main
```

سيتم تحديث التطبيق تلقائياً على Streamlit Cloud! 🎉

---

## 🎯 روابط مهمة

- **GitHub Repo**: https://github.com/Madow2026/ksa-projects
- **Streamlit Cloud**: https://share.streamlit.io/
- **OpenAI Platform**: https://platform.openai.com/
- **Documentation**: راجع [README.md](README.md)

---

## ❓ حل المشاكل الشائعة

### المشكلة: التطبيق لا يعمل بعد Deploy

**الحل**:
1. تحقق من Logs في Streamlit Cloud
2. تأكد من أن جميع الملفات موجودة في GitHub
3. تحقق من `requirements.txt`

### المشكلة: Database errors

**الحل**:
```python
# التطبيق يستخدم SQLite - سيتم إنشاء قاعدة البيانات تلقائياً
# لا حاجة لإعدادات إضافية
```

### المشكلة: Scraping لا يعمل

**الحل**:
- بعض المواقع تحجب السكريبرات في البيئة السحابية
- استخدم Demo Data للاختبار
- أو قم بتشغيل Pipeline محلياً ورفع قاعدة البيانات

---

## 🎉 تهانينا!

تطبيقك الآن online ويمكن الوصول إليه من أي مكان! 🚀

**Next Steps**:
1. أضف OpenAI API Key للحصول على أفضل أداء
2. قم بتشغيل Pipeline لجمع البيانات
3. شارك الرابط مع فريقك
4. راقب الأداء وأضف تحسينات

---

**Questions?** راجع [README.md](README.md) أو افتح Issue على GitHub
