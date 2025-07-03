# 📊 2-1-1 Call Data Analysis — United Way of San Antonio & Bexar County

## 📘 Project Overview  
This repository contains all scripts, cleaned datasets, spatial analyses, and visualizations created for the United Way of San Antonio & Bexar County 2-1-1 Call Data Project, as part of the **UTSA Community Innovation Scholars Program**.

The goal of this project is to analyze ZIP-level patterns of 2-1-1 caller volume and economic instability across Bexar County using spatial and statistical techniques. Key tasks include:

- Cleaning and processing 2-1-1 client and interaction call data  
- Creating ZIP-level bivariate spatial visualizations using LISA and Moran’s I  
- Analyzing the relationship between caller rates and economic instability indicators (poverty, ALICE, and combined)  
- Generating clear and digestible visuals for both technical analysis and nonprofit partner use  

This project was completed as part of a **three-person research team**. Each member was assigned a specific demographic focus.  
💼 **My assigned demographic was economic instability**, and **100% of the content in this repository directly answers the project’s research question through that lens**.  
All code, visualizations, and analysis in this repository are tied to understanding how economic instability impacts 2-1-1 caller patterns.

The repository is organized into folders by function (e.g. data cleaning scripts, LISA outputs, graphs by category) and includes both raw and filtered datasets, in addition to all exploratory and final visualizations.

## 🔍 Primary Research Question

> To what extent are 2-1-1 call patterns aligned with geographic and sociodemographic inequities in Bexar County?

We answer this through analysis of:
- Call frequency by ZIP code
- Normalized call volume (calls per 1,000 residents)
- Demographic trends of clients using 2-1-1

## 🛠️ Tools Used
- Python (pandas, matplotlib, sklearn, ast, plotly, scipy, etc.)
- Excel
- SPSS (for statistical analysis, not shown in this repo)
- Tableau (for final dashboard visualization)

> ⚠️ **Data files are not included in this repository due to an NDA (Non-Disclosure Agreement). Only the code is available.**

## 📁 Folder Glossary

- `bexar_specific/` — Analysis and outputs restricted to Bexar County ZIP codes
- `bivariate_data/` — Bivariate LISA output files across all ZIPs
- `graphs/` — Final visualizations by theme (heat maps, LISA, Spearman, etc.)
- `starter/` — Legacy or early versions of cleaned ZIP datasets

## 🗂️ Project Repository Structure
> **Note: This is the true, full project directory used for analysis and visualization during the UTSA Community Innovation Scholars Program.
While raw .csv files and generated graphs are not publicly visible in this repository due to an NDA with United Way of San Antonio & Bexar County, the structure below reflects all scripts, file paths, and outputs used internally.**

UNITED-WAY-BEXAR-COUNTY/
├── README.md
├── .gitignore
├── venv/
│
├── bexar_specific/
│   ├── Bexar County ZIPs Tests.py
│   ├── Bexar_Bivariate_ALICE_LISA.csv
│   ├── Bexar_Bivariate_Poverty_LISA.csv
│   ├── Bexar_Bivariate_Sum_LISA.csv
│   ├── Bexar_County_Cleaned_ZIP_Data.csv
│   ├── Bexar_County_ZIP_Eco_Indicator_Data.csv
│
├── bivariate_data/
│   ├── Bivariate_ALICE_vs_CallerRate_LISA.csv
│   ├── Bivariate_Poverty_vs_CallerRate_LISA.csv
│   ├── Bivariate_PovertyALICE_vs_CallerRate_LISA.csv
│
├── graphs/
│   ├── bexar LISA economic instability/
│   ├── LISA economic instability/
│   │   ├── LISA_ALICE_rate.png
│   │   ├── LISA_callers_rate.png
│   │   ├── LISA_instability.png
│   │   ├── LISA_poverty_rate.png
│   ├── nonprofit requested graphs/
│   │   ├── heat map quartiles/
│   │   │   ├── heat_map_caller_ALICE_rate.png
│   │   │   ├── heat_map_caller_poverty_rate.png
│   │   │   ├── heat_map_caller_rate_sum.png
│   │   ├── heat map quartiles (new)/
│   │   ├── spearmen zoomed in/
│   │   │   ├── spearmen_caller_rate_ALICE_zoom.png
│   │   │   ├── spearmen_caller_rate_poverty_zoom.png
│   │   │   ├── spearmen_caller_rate_sum_zoom.png
│   │   ├── spearmen outlier included/
│   │   │   ├── spearmen_callers_rate_ALICE_rate.png
│   │   │   ├── spearmen_callers_rate_poverty_rate.png
│   │   │   ├── spearmen_callers_rate_sum.png
│   │   │   ├── instability_ALICE_rate_by_ZIP.png
│   │   │   ├── instability_poverty_ALICE_rate_by_ZIP.png
│   │   │   ├── instability_poverty_rate_by_ZIP.png
│   │   │   ├── total_callers_by_ZIP_map_quartile.png
│   ├── strictly bexar county visuals/
│       ├── bivariate_ALICE_caller_rate.png
│       ├── bivariate_poverty_caller_rate.png
│       ├── bivariate_sum_caller_rate.png
│       ├── caller_rate_by_ZIP_map_quartile.png
│       ├── spearmen_caller_rate_ALICE.png
│
├── starter/
│   ├── Old Client ZIP Code Cleanup.py
│   ├── Old_211_Client_Cleaned.csv
│   ├── Old_Callers_By_Zip.csv
│   ├── Old_Callers_Per_1000.csv
│
├── 211 Area Indicators_ZipZCTA.csv
├── 211 Call Data_Client Tab_All Years.csv
├── 211 Call Data_Interaction Tab_All Years.csv
├── 211 Call Data_Referral Tab_All Years.csv
├── 211 Caller Poverty Rate Heat Map.py
├── 211 ZIP Morans I Analysis.py
├── 211 ZIP Spearman Analysis.py
├── 211_Demographic_Data_Cleaned.csv
├── 211_Merged_ZIP_Economic_Instability.csv
├── 211_Spearman_Correlation_Results.csv
├── Community Indicator Metadata.csv
├── Filter Clients Calls ZIP.py
├── New_211_Client_Cleaned.csv
├── Poverty Cleanup.py
├── Top_ZIPs_Economic_Instability.csv


## 🚫 Data Access & NDA Note

This project was completed in partnership with United Way of San Antonio & Bexar County. Due to the confidentiality terms of the Non-Disclosure Agreement (NDA), no CSV or Excel data files from this project are uploaded to this repository. Only scripts and documentation are provided.

If you're interested in collaborating or learning more about the methodology, feel free to reach out!
