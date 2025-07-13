# Osint-Multi-Tool

Osint-Multi-Tool is an advanced framework for integrated Open Source Intelligence (OSINT) collection, analysis, and visualization. It automates the orchestration of multiple OSINT tools and enables unified intelligence gathering with graph-based visualization and storage.

## Features

- **Automated Multi-Source Collection:**  
  Orchestrates intelligence gathering from tools like SpiderFoot, Recon-ng, Shodan, and TheHarvester.
- **Entity Extraction:**  
  Extracts and correlates entities (IPs, domains, emails, etc.) across sources.
- **Graph Database Storage:**  
  Stores results in Neo4j for relationship mapping and analysis.
- **Searchable Results Archive:**  
  Indexes intelligence findings in Elasticsearch for fast search and retrieval.
- **Visualization:**  
  Generates relationship graphs for intuitive OSINT data exploration.
- **Modular & Extensible:**  
  Easily add collection modules or integrate new OSINT tools.
- **Logging & Error Handling:**  
  Robust logging for process tracking and troubleshooting.

## Supported OSINT Tools

- SpiderFoot
- Recon-ng
- Shodan
- TheHarvester

## Requirements

- Python 3.8+
- Neo4j (Graph database)
- Elasticsearch
- SpiderFoot (OSINT automation tool)
- Shodan Python SDK
- Recon-ng
- TheHarvester
- Additional Python dependencies as listed in `requirements.txt`

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ROBOTdingDONG/Osint-Multi-Tool.git
   cd Osint-Multi-Tool
