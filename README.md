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
