# 🩺 TipMYS Light

**TipMYS Light** is a simplified, open-source version of the Medical Faculty Curriculum Management System.  
It’s built with **Django 5**, designed to manage academic programs, courses, committees, and exam workflows in a lightweight and educational way.

---

## 🚀 Features

- 🏫 Faculty, Program, Committee, and Course Management  
- 📚 Course Events, Academic Calendar, and Lecture Tracking  
- 🧠 Question Bank (QBank) with Exam Question Selection  
- 🧾 Exam Setup & Performance Statistics  
- 🧍‍♂️ Role-based permissions for lecturers, chairs, and secretaries  
- 🌐 Multilingual interface (Turkish / English)  
- ⚙️ Compatible with MySQL or MariaDB  
- 🧩 Modular architecture for easy customization and demo use

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| **Framework** | Django 5.2 |
| **Frontend** | Bootstrap 5 + jQuery + Select2 |
| **Database** | MySQL / MariaDB |
| **Forms** | Crispy Forms (Bootstrap 5) |
| **Extras** | Import-Export, Django-Select2, DataTables |

---

## 🧑‍💻 Installation (Development)

```bash
# 1️⃣ Clone the repo
git clone https://github.com/onanarif/tipmys_light.git
cd tipmys_light

# 2️⃣ Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate   # macOS / Linux

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Create a .env file
cp .env.example .env
# Then edit .env to include your DB credentials and secret key

# 5️⃣ Apply migrations
python manage.py migrate

# 6️⃣ Run the development server
python manage.py runserver
