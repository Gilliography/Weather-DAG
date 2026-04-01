# Weather-DAG
Beginner weather app practicing on APIs
# 🌦️ Weather ETL Pipeline with Apache Airflow

## 📌 Overview

This project is a beginner-friendly yet production-inspired **ETL (Extract, Transform, Load) pipeline** built using **Apache Airflow** and **Docker**.

It fetches weather data from the Open-Meteo API, processes it, and loads it into a storage system (CSV or PostgreSQL).

---

## 🏗️ Architecture

```
        ┌──────────────┐
        │ Open-Meteo API │
        └──────┬───────┘
               │ (Extract)
               ▼
        ┌──────────────┐
        │  Extract Task │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ Transform Task│
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │   Load Task   │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ Storage (CSV / Postgres) │
        └──────────────┘
```

---

## ⚙️ Tech Stack

* Apache Airflow (workflow orchestration)
* Docker & Docker Compose
* Python (Pandas, Requests)
* PostgreSQL (optional storage)
* Open-Meteo API (data source)

---

## 📁 Project Structure

```
Weather-DAG/
│
├── dags/
│   └── weather_etl_dag.py
│
├── scripts/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
│
├── docker-compose.yaml
├── requirements.txt
└── README.md
```

---

## 🔄 ETL Pipeline Explanation

### 1. Extract

* Calls Open-Meteo API
* Retrieves hourly temperature data
* Returns raw JSON

### 2. Transform

* Converts JSON → Pandas DataFrame
* Cleans and formats columns
* Prepares structured dataset

### 3. Load

* Option 1: Save as CSV
* Option 2: Load into PostgreSQL table

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Weather-DAG
```

---

### 2. Start the Services

```bash
docker-compose down -v
docker-compose up --build
```

---

### 3. Access Airflow UI

#### Local Machine:

```
http://localhost:8080
```

#### GitHub Codespaces:

* Open **PORTS tab**
* Click port **8080**
* Use forwarded URL:

```
https://<codespace>-8080.app.github.dev
```

---

### 4. Login Credentials

```
Username: airflow
Password: airflow
```

---

## ▶️ Running the Pipeline

1. Open Airflow UI
2. Enable DAG: `modular_weather_etl`
3. Click **Trigger DAG**
4. Monitor execution in:

   * Graph View
   * Task Logs

---

## 🧪 Example API Used

```
https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m
```

---

## 📊 Enhancements (Next Steps)

* Store data in PostgreSQL instead of CSV
* Add retry logic for API failures
* Parameterize latitude/longitude
* Schedule DAG (e.g., hourly)
* Add logging and monitoring

---

## 🐳 Docker Services

* airflow-webserver
* airflow-scheduler
* airflow-init
* postgres

---

## 🧠 Key Learnings

* Building modular ETL pipelines
* Orchestrating workflows with Airflow
* Using Docker for reproducible environments
* Debugging real-world Airflow issues (auth, imports, containers)

---

## ⚠️ Troubleshooting

### Airflow UI not accessible

* Check port 8080 is running
* Use correct Codespaces URL

### Invalid login

* Ensure user exists:

```bash
airflow users list
```

### DAG import errors

* Add path fix:

```python
import sys
sys.path.append('/opt/airflow')
```

---

## 🌟 Conclusion

This project demonstrates how to build a complete ETL pipeline using modern data engineering tools. It serves as a strong foundation for more advanced systems involving streaming, cloud deployment, and data warehousing.

---

## 📌 Author

**Gilbert Kiprotich**

---

## ⭐ If you found this helpful

Give the repo a star and share 🚀
