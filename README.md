```markdown
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
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the environment:**  
   Edit the config section in your main script or provide a configuration file:
   ```python
   config = {
       'neo4j_uri': 'bolt://localhost:7687',
       'neo4j_user': 'neo4j',
       'neo4j_password': 'password',
       'elasticsearch_host': 'localhost:9200',
       'spiderfoot_host': 'http://localhost:5001',
       'shodan_api_key': '<your_shodan_api_key>'
   }
   ```

4. **Start Neo4j and Elasticsearch:**  
   Make sure Neo4j and Elasticsearch are running locally or update the config for remote instances.

5. **(Optional) Run SpiderFoot, Recon-ng, and TheHarvester as services or ensure they are accessible.**

## Usage

You can use the framework in your own scripts or run the included example:

```python
from osint_framework import OSINTFramework, OSINTTarget
import asyncio

async def run():
    config = {...}  # see above
    framework = OSINTFramework(config)
    target = OSINTTarget(target_type='domain', target_value='example.com', collection_modules=['spiderfoot', 'shodan', 'harvester'])
    results = await framework.collect_intelligence(target)
    framework.store_results(results)
    print(framework.visualize_results('example.com'))

asyncio.run(run())
```

## Output

- **Graph Visualization:**  
  Entity relationships are visualized and can be exported or served via a web frontend.
- **Searchable Archive:**  
  All findings are indexed for search via Elasticsearch.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions, issues, and feature requests are welcome! Please open an issue or submit a pull request.

## Disclaimer

This tool is for educational and lawful use only. Use responsibly and ensure compliance with all applicable laws.
```
