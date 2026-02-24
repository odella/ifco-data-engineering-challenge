# IFCO Data Engineering Challenge - Solution Delivery

This folder contains the complete deliverables for the technical challenge, structured to provide both the data engineering pipeline and a standalone, containerized visualization dashboard.

## 📂 Deliverables Structure

### 1. Data Processing & Aggregation (Tests 1-5)
The complete data engineering pipeline, including data cleaning (Silver layer), aggregations (Gold layer), and comprehensive **unit tests** for all the logic, is contained within a single Databricks Notebook:
* `IFCO Data Engineering Challenge.ipynb`
* **Data Sources Included:** I have also included the raw `orders.csv` and `invoicing_data.json` files in this `Respuesta` folder for your convenience.

### 2. Executive Sales Dashboard (Test 6)
To satisfy the requirement of providing a complete execution environment, the interactive visualization dashboard has been fully decoupled from Databricks and containerized using Docker. 

All files required to run the dashboard are located in the `docker/` directory.

---

## 🚀 How to Run the Databricks Notebook (Tests 1-5)

The data engineering pipeline and unit tests are designed to run in a Databricks environment (including the Free Community Edition).

**Execution Steps:**
1. Log in to your Databricks Workspace.
2. Navigate to **Workspace** -> **Users** -> *[Your Username]* and create a new folder (e.g., `IFCO_Challenge`).
3. **Import Files:** Inside that folder, select **Import** and upload:
   - `IFCO Data Engineering Challenge.ipynb`
   - `orders.csv`
   - `invoicing_data.json`
4. Open the imported notebook, attach it to an active compute cluster, and run all cells (`Run All`).

> [!NOTE]
> The notebook is configured to look for the data files in its local workspace directory (using the `/Workspace/...` path syntax), ensuring a seamless setup experience.

---

## 📈 How to Run the Dashboard (Test 6)

The dashboard is built with Streamlit and Plotly, and uses a pre-processed snapshot of the Gold/Silver data to ensure it runs instantly on any machine without requiring a Databricks cluster connection.

**Prerequisites:** 
- [Docker](https://docs.docker.com/get-docker/) installed and running.

**Execution Steps:**
1. Open your terminal and navigate to the `docker` directory within this folder:
   ```bash
   cd Respuesta/docker
   ```
2. Build and launch the containerized application:
   ```bash
   docker-compose up --build -d
   ```
3. Open your web browser and navigate to the dashboard at:
   👉 **[http://localhost:8502](http://localhost:8502)**

*(To stop the dashboard later, simply run `docker-compose down` from the same directory).*

---

## 🗺️ Roadmap — What I Would Build Next (1-Month Vision)

> If this were a real project within a multidisciplinary team (Data Engineering, Analytics, Product, and Sales), here is how I would evolve the solution over the next 4 weeks:

### Week 1 — Productionise the Data Pipeline
- **Replace the notebook with a modular dbt project:** each Test (1–5) becomes a dbt model with its own schema tests and documentation. This enables version-controlled, incremental transformations and a data lineage graph out of the box.
- **Automate ingestion with a Databricks Workflow (or Apache Airflow DAG):** schedule Bronze → Silver → Gold refreshes so the dashboard always reflects live data instead of a static snapshot.
- **Implement data quality alerts:** use Great Expectations (or dbt tests) to catch anomalies (e.g. negative commissions, unknown crate types) before they reach the dashboard.

### Week 2 — Harden the Dashboard & Infrastructure
- **CI/CD pipeline (GitHub Actions):** on every push, run linting (`ruff`), unit tests (`pytest`), and rebuild the Docker image — so no broken code reaches `main`.
- **Environment variables & secrets management:** move any hard-coded paths or credentials to `.env` files (excluded from git) and a secrets manager for production.
- **Automated dashboard tests:** add Streamlit's `AppTest` framework to validate that all sections render correctly after a data refresh, preventing silent regressions.

### Week 3 — Deepen the Analytics
- **Extend the commission model:** support configurable commission tiers (instead of hard-coded 6% / 2.5% / 0.95%) so the Sales team can self-serve rule changes without touching code.
- **Cohort & retention analysis:** group companies by their first order date and track whether they expand, reduce, or churn their crate type mix — a direct leading indicator for the sales team.
- **Predictive training prioritisation:** use a simple logistic regression (scikit-learn) to score each sales owner's probability of closing a Plastic order in the next quarter, making the "Training Priority" view truly data-driven instead of rule-based.

### Week 4 — Embed in the Business
- **Role-based dashboard views:** managers see aggregated team KPIs; individual sales owners see only their own performance — implemented via Streamlit's authentication options or an identity-aware proxy.
- **Alerting & subscriptions:** email or Slack digest (weekly) with the top/bottom performers and any significant trend changes, so insights reach people who don't visit the dashboard.
- **Stakeholder feedback loop:** run a short demo session with the Sales team and collect structured feedback (What's missing? What's confusing?) to prioritise the next iteration — treating the dashboard as a product, not a one-off report.

### Key Technical Decisions I Would Propose
| Decision | Rationale |
|---|---|
| **dbt over raw SQL notebooks** | Version control, automated testing, lineage, and self-documenting models |
| **Delta Lake / Lakehouse pattern** | Time travel + ACID transactions for reliable incremental loads without full recomputes |
| **Streamlit → Superset/Metabase** (long-term) | Self-service analytics for non-technical stakeholders without requiring Python deployments |
| **Feature Store for ML features** | Reuse commission/performance features across models to avoid duplication |

