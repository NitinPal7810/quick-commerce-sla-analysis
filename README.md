# Quick Commerce SLA Breach Analytics & Operational Risk Analysis

## 📌 Project Overview

This project analyzes Service Level Agreement (SLA) breaches in a simulated quick-commerce operation to identify operational bottlenecks, quantify revenue at risk, and evaluate staffing scenarios for reducing delivery delays.

The analysis covers **200,000 simulated delivery orders** across **20 zones and 40 stores** from January to March 2026.

The project combines SQL analytics, Python-based exploratory analysis, XGBoost machine learning, SHAP explainability, scenario simulation, and Power BI dashboarding to understand the operational factors associated with SLA breaches.

> **Note:** The dataset is simulated for portfolio and analytical demonstration purposes. Revenue-at-risk and staffing scenario results are modeled estimates, not actual company financial losses or causal experimental results.

---

## 🎯 Business Problem

Quick-commerce businesses operate under strict delivery-time commitments. When deliveries exceed the promised SLA, customer experience and repeat-purchase probability may be affected.

This project addresses the following questions:

- What percentage of orders breach the SLA?
- Which time periods experience the highest breach rates?
- Which zones and stores show greater operational pressure?
- How do queue pressure, rider availability, distance, and utilization relate to breaches?
- Which operational variables are most important for predicting SLA breaches?
- What is the modeled revenue at risk associated with SLA breaches?
- How could staffing changes affect breach rates under predefined scenario assumptions?

---

## 📊 Dataset

The dataset contains **200,000 simulated delivery-level records**.

### Key Dataset Statistics

| Metric | Value |
|---|---:|
| Total Orders | 200,000 |
| Zones | 20 |
| Stores | 40 |
| SLA Breach Orders | 20,000 |
| Overall Breach Rate | 10.00% |
| Average Order Value | ₹804.81 |
| Average Delivery Time | 7.98 min |
| Average Dispatch Delay | 3.24 min |
| Modeled Revenue at Risk | ₹32.2L |
| SLA Target | 10 minutes |

### Important Variables

- Order placement time
- Zone
- Store
- Zone type
- Distance
- Weather
- Riders active
- Orders in queue
- Store utilization
- Utilization rate
- Queue pressure
- Load ratio
- Rider idle time
- Delivery time
- Dispatch delay
- Order value
- SLA breach flag
- Reorder probability

---

## 🔍 Key Findings

### 1. SLA Breach by Time of Day

The highest breach rate occurs during the **Evening Peak** period.

| Time Bucket | Breach Rate |
|---|---:|
| Morning | 4.50% |
| Late Morning | 10.83% |
| Afternoon | 14.04% |
| Evening Peak | 19.30% |
| Night | 4.59% |

The analysis indicates that peak operating periods are associated with substantially higher SLA breach rates in the simulated dataset.

---

### 2. Operational Pressure

SQL and Python analysis were used to investigate the relationship between operational pressure and SLA performance.

Variables analyzed include:

- Queue pressure
- Orders in queue
- Store utilization
- Rider availability
- Load ratio
- Rider idle time
- Dispatch delay
- Distance

Higher operational pressure was associated with higher observed breach rates in the simulated dataset.

---

### 3. Zone-Level Risk

Zone × time analysis was used to identify combinations where breach rates and operational pressure were simultaneously elevated.

The compound-impact analysis highlighted **Evening Peak** as an important operating window for several zones.

---

## 💰 Revenue-at-Risk Analysis

A modeled customer retention assumption was used to estimate potential revenue exposure.

For breached orders, the project applies a modeled **0.20 reorder-probability penalty**.

The calculation is:

```text
Revenue at Risk
= Breached Orders
  × Reorder Probability Penalty
  × Average Order Value

  The modeled revenue-at-risk estimate is approximately **₹32.2 lakh** for the simulated dataset.

> **Important:** The 0.20 reorder-probability penalty is a modeling assumption used for scenario analysis. It should not be interpreted as an observed causal effect.

---

## 🤖 Machine Learning

An **XGBoost binary classification model** was developed to predict whether an order would breach the 10-minute SLA.

### Model Performance

| Metric | Value |
|---|---:|
| Accuracy | 84.76% |
| Precision | 38.51% |
| Recall | 87.92% |
| F1 Score | 53.56% |
| ROC-AUC | 93.87% |

The model was trained using operational features available around order placement while avoiding post-delivery leakage.

### Key Predictive Features

The model identified several important variables associated with SLA breach risk:

- Peak-hour indicator
- Distance
- Weather conditions
- Queue pressure
- Store utilization
- Orders in queue
- Load ratio
- Rider availability

---

## 🔎 SHAP Explainability

SHAP-based analysis was used to explain the model's predictions and understand which variables contributed most strongly to SLA breach risk.

The most influential features included:

1. Distance
2. Rain conditions
3. Peak-hour indicator
4. Queue pressure
5. Store utilization
6. Orders in queue
7. Load ratio

This provides an interpretable layer beyond the XGBoost feature-importance output.

---

## 📈 Staffing Scenario Simulation

A scenario analysis was created to estimate how additional staffing could affect SLA breach rates.

The scenarios use a predefined modeling assumption:

> Every **10% increase in staffing** is assumed to produce a **5% relative reduction in breach probability**.

### Scenario Results

| Scenario | Modeled Breach Rate | Estimated Breaches | Estimated Breaches Avoided |
|---|---:|---:|---:|
| Baseline | 10.00% | 20,000 | — |
| Staffing +10% | 9.50% | 19,000 | 1,000 |
| Staffing +20% | 9.00% | 18,000 | 2,000 |
| Staffing +30% | 8.50% | 17,000 | 3,000 |

> **Important:** These are modeled scenario estimates based on predefined assumptions, not causal evidence from an A/B test or real operational deployment.

---

## 📊 Power BI Dashboard

The project includes an executive Power BI dashboard designed to communicate operational performance and potential risk to business stakeholders.

The dashboard will include:

### Executive KPI View

- Total Orders
- SLA Breach Rate
- Breach Orders
- Average Delivery Time
- Average Dispatch Delay
- Average Order Value
- Modeled Revenue at Risk

### Operational Analysis

- SLA Breach Rate by Time Bucket
- Zone-level Breach Analysis
- Store Performance
- Queue Pressure Analysis
- Rider Utilization
- Dispatch Delay Analysis

### Scenario Analysis

A staffing scenario section will allow users to compare:

- Baseline breach rate
- Staffing +10%
- Staffing +20%
- Staffing +30%
- Estimated breaches avoided

The dashboard is intended to provide an executive-level view of operational risk and support scenario-based decision making.

---

## 🛠️ Tech Stack

- **Python** — Data generation, cleaning, EDA, feature engineering, machine learning, SHAP, scenario simulation
- **SQL / MySQL** — Data loading and operational analytics
- **XGBoost** — SLA breach prediction
- **SHAP** — Model explainability
- **Power BI** — Executive dashboard and scenario visualization
- **Git / GitHub** — Version control and project documentation

---

## 📁 Project Structure

```text
quick-commerce-sla-analysis/
│
├── data/
│   └── deliveries.csv
│
├── sql/
│   ├── 01_breach_audit.sql
│   ├── 02_time_bucket_analysis.sql
│   ├── 03_store_overload_analysis.sql
│   ├── 04_window_functions.sql
│   ├── 05_rider_idle_analysis.sql
│   ├── 06_compound_impact_score.sql
│   └── 07_retention_revenue_impact.sql
│
├── python/
│   ├── generate_dataset.py
│   ├── 01_data_cleaning.py
│   ├── 02_eda.py
│   ├── 03_feature_engineering.py
│   ├── 04_xgboost_model.py
│   ├── 05_shap_analysis.py
│   └── 06_scenario_simulation.py
│
├── outputs/
│   ├── charts/
│   └── models/
│
├── notebooks/
│
├── powerbi/
│   ├── python/
│   └── sql/
│
├── README.md
├── .gitignore
└── requirements.txt

