# 🛒 PrestaShop Project

Welcome to the **PrestaShop Project** repository! This project provides a fully Dockerized environment for running a **PrestaShop** e-commerce platform, integrated with **MariaDB** for database management and **phpMyAdmin** for easy database interaction. Secure communication is ensured with SSL via a self-signed certificate.

---

## ✨ Features

- **PrestaShop 1.7.8**: Dockerized PrestaShop installation for streamlined deployment.
- **MariaDB**: Reliable, MySQL-compatible database for e-commerce data.
- **phpMyAdmin**: Simplified database management via an intuitive web interface.
- **SSL Integration**: Secure HTTPS connections using self-signed certificates.
- **Persistent Storage**: Ensures data consistency across container restarts.
- **Customizable Environment**: Easily configure via environment variables.
- **Python Tools**: Scraping and testing utilities built with Scrapy and Selenium.

---

## 🛠️ Software Stack

1. **PrestaShop** v1.7.8
2. **MariaDB**
3. **Docker**
4. **Python** (for scraping and testing)
5. **Scrapy**
6. **Selenium**

---

## 🚀 Getting Started

### Prerequisites
Ensure you have the following installed:
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

### 🐾 Step-by-Step Guide

#### 1️⃣ Clone the Repository
```bash
git clone https://github.com/hannayuzefavich/prestashop-project.git
cd prestashop-project
```

#### 2️⃣ Launch the Containers
```bash
docker-compose up --build
```

#### 3️⃣ Access the Services
- **PrestaShop**: [https://localhost:8090](https://localhost:8090)
- **phpMyAdmin**: [http://localhost:8081](http://localhost:8081)

#### 4️⃣ Login Credentials
##### MariaDB Admin:
- **Username**: `prestashop`
- **Password**: `prestashop`

##### PrestaShop Admin:
- **Username**: `juzeffch@gmail.com`
- **Password**: `prestashop`

---

## 🧩 Additional Features

### 🕷️ Run Scraper
To execute the web scraper, run:
```bash
python scraper.py
```

### 🧪 Run Tests
For automated tests:
```bash
python -m unittest discover
```

### 🌐 Run API
To start the API server:
```bash
python api_server.py
```

---

## 🖋️ Authors

- [Maxym Besarab](https://www.github.com/MaxBesarab)
- [Hanna Yuzefavich](https://www.github.com/hannayuzefavich)
- [Karyna Lukashova](https://www.github.com/lkarii)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 📬 Feedback

Feel free to open an issue or contact the authors for suggestions and improvements!
