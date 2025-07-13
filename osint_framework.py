#!/usr/bin/env python3
"""
OSINT Integration Framework
Combines multiple OSINT tools for comprehensive intelligence gathering
"""

import json
import asyncio
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# Core integrations
from spiderfoot import SpiderFootApi
from recon_ng import ReconNgApi
from shodan import Shodan
from neo4j import GraphDatabase
from elasticsearch import Elasticsearch

@dataclass
class OSINTTarget:
    """Target definition for OSINT collection"""
    target_type: str  # domain, ip, email, etc.
    target_value: str
    collection_modules: List[str]
    priority: int = 1

class OSINTFramework:
    """Main OSINT integration framework"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {}
        self.graph_db = GraphDatabase.driver(
            config['neo4j_uri'], 
            auth=(config['neo4j_user'], config['neo4j_password'])
        )
        self.es_client = Elasticsearch([config['elasticsearch_host']])
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Configure logging for the framework"""
        logger = logging.getLogger('osint_framework')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def collect_intelligence(self, target: OSINTTarget) -> Dict[str, Any]:
        """Orchestrate intelligence collection from multiple sources"""
        results = {
            'target': target,
            'timestamp': datetime.utcnow().isoformat(),
            'sources': {}
        }
        
        # SpiderFoot collection
        if 'spiderfoot' in target.collection_modules:
            results['sources']['spiderfoot'] = await self._collect_spiderfoot(target)
        
        # Recon-ng collection
        if 'recon_ng' in target.collection_modules:
            results['sources']['recon_ng'] = await self._collect_recon_ng(target)
        
        # Shodan collection
        if 'shodan' in target.collection_modules:
            results['sources']['shodan'] = await self._collect_shodan(target)
        
        # TheHarvester collection
        if 'harvester' in target.collection_modules:
            results['sources']['harvester'] = await self._collect_harvester(target)
        
        return results
    
    async def _collect_spiderfoot(self, target: OSINTTarget) -> Dict[str, Any]:
        """Collect data using SpiderFoot"""
        self.logger.info(f"Starting SpiderFoot collection for {target.target_value}")
        
        # SpiderFoot API integration
        sf_api = SpiderFootApi(self.config['spiderfoot_host'])
        
        # Start scan
        scan_id = sf_api.start_scan(
            target.target_value,
            modules=['dns', 'whois', 'social', 'leaks']
        )
        
        # Wait for completion and get results
        results = sf_api.get_scan_results(scan_id)
        
        return {
            'scan_id': scan_id,
            'results': results,
            'entities': self._extract_entities(results)
        }
    
    async def _collect_recon_ng(self, target: OSINTTarget) -> Dict[str, Any]:
        """Collect data using Recon-ng"""
        self.logger.info(f"Starting Recon-ng collection for {target.target_value}")
        
        # Recon-ng integration
        recon_api = ReconNgApi()
        
        # Run modules
        results = {}
        modules = ['recon/domains-hosts/hackertarget', 'recon/hosts-ports/shodan_ip']
        
        for module in modules:
            results[module] = recon_api.run_module(module, target.target_value)
        
        return results
    
    async def _collect_shodan(self, target: OSINTTarget) -> Dict[str, Any]:
        """Collect data using Shodan"""
        self.logger.info(f"Starting Shodan collection for {target.target_value}")
        
        api = Shodan(self.config['shodan_api_key'])
        
        try:
            # Host information
            if target.target_type == 'ip':
                host_info = api.host(target.target_value)
                return {
                    'host_info': host_info,
                    'services': host_info.get('data', []),
                    'location': {
                        'country': host_info.get('country_name'),
                        'city': host_info.get('city'),
                        'coords': [host_info.get('latitude'), host_info.get('longitude')]
                    }
                }
            
            # Domain search
            elif target.target_type == 'domain':
                search_results = api.search(f'hostname:{target.target_value}')
                return {
                    'total': search_results['total'],
                    'matches': search_results['matches']
                }
                
        except Exception as e:
            self.logger.error(f"Shodan collection error: {str(e)}")
            return {'error': str(e)}
    
    async def _collect_harvester(self, target: OSINTTarget) -> Dict[str, Any]:
        """Collect data using TheHarvester"""
        self.logger.info(f"Starting TheHarvester collection for {target.target_value}")
        
        # TheHarvester integration
        import subprocess
        import json
        
        cmd = [
            'theHarvester',
            '-d', target.target_value,
            '-b', 'google,bing,yahoo,duckduckgo',
            '-f', 'json'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {'error': result.stderr}
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_entities(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entities from collection results"""
        entities = []
        
        # Process different result types
        for source, data in results.items():
            if isinstance(data, dict):
                # Extract IPs, domains, emails, etc.
                for key, value in data.items():
                    if self._is_entity(key, value):
                        entities.append({
                            'type': self._get_entity_type(key, value),
                            'value': value,
                            'source': source,
                            'confidence': self._calculate_confidence(source, key)
                        })
        
        return entities
    
    def store_results(self, results: Dict[str, Any]) -> None:
        """Store results in graph database and search index"""
        
        # Store in Neo4j
        with self.graph_db.session() as session:
            session.write_transaction(self._create_graph_nodes, results)
        
        # Store in Elasticsearch
        doc = {
            'timestamp': results['timestamp'],
            'target': results['target'].__dict__,
            'sources': results['sources']
        }
        
        self.es_client.index(
            index='osint-results',
            doc_type='_doc',
            body=doc
        )
    
    def _create_graph_nodes(self, tx, results: Dict[str, Any]) -> None:
        """Create nodes and relationships in Neo4j"""
        target = results['target']
        
        # Create target node
        tx.run(
            "MERGE (t:Target {value: $value, type: $type}) "
            "SET t.last_updated = $timestamp",
            value=target.target_value,
            type=target.target_type,
            timestamp=results['timestamp']
        )
        
        # Create entity nodes and relationships
        for source, data in results['sources'].items():
            if 'entities' in data:
                for entity in data['entities']:
                    tx.run(
                        "MERGE (e:Entity {value: $value, type: $type}) "
                        "SET e.source = $source, e.confidence = $confidence "
                        "WITH e "
                        "MATCH (t:Target {value: $target_value}) "
                        "MERGE (t)-[:FOUND_IN]->(e)",
                        value=entity['value'],
                        type=entity['type'],
                        source=entity['source'],
                        confidence=entity['confidence'],
                        target_value=target.target_value
                    )
    
    def visualize_results(self, target_value: str) -> str:
        """Generate visualization data for frontend"""
        with self.graph_db.session() as session:
            result = session.read_transaction(
                self._get_graph_data, target_value
            )
            
            return json.dumps({
                'nodes': result['nodes'],
                'edges': result['edges'],
                'metadata': result['metadata']
            })
    
    def _get_graph_data(self, tx, target_value: str) -> Dict[str, Any]:
        """Retrieve graph data for visualization"""
        query = """
        MATCH (t:Target {value: $target_value})-[:FOUND_IN]->(e:Entity)
        RETURN t, e, collect(e) as entities
        """
        
        result = tx.run(query, target_value=target_value)
        
        nodes = []
        edges = []
        
        for record in result:
            target = record['t']
            entities = record['entities']
            
            # Add target node
            nodes.append({
                'id': target['value'],
                'label': target['value'],
                'type': 'target',
                'size': 20
            })
            
            # Add entity nodes and edges
            for entity in entities:
                nodes.append({
                    'id': entity['value'],
                    'label': entity['value'],
                    'type': entity['type'],
                    'size': 10,
                    'source': entity['source'],
                    'confidence': entity['confidence']
                })
                
                edges.append({
                    'from': target['value'],
                    'to': entity['value'],
                    'label': 'found_in'
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_entities': len(nodes) - 1,
                'sources': list(set([n.get('source') for n in nodes if n.get('source')]))
            }
        }

# Usage example
async def main():
    """Example usage of the OSINT framework"""
    
    config = {
        'neo4j_uri': 'bolt://localhost:7687',
        'neo4j_user': 'neo4j',
        'neo4j_password': 'password',
        'elasticsearch_host': 'localhost:9200',
        'spiderfoot_host': 'http://localhost:5001',
        'shodan_api_key': 'your_shodan_api_key'
    }
    
    framework = OSINTFramework(config)
    
    # Define target
    target = OSINTTarget(
        target_type='domain',
        target_value='example.com',
        collection_modules=['spiderfoot', 'shodan', 'harvester']
    )
    
    # Collect intelligence
    results = await framework.collect_intelligence(target)
    
    # Store results
    framework.store_results(results)
    
    # Generate visualization
    viz_data = framework.visualize_results('example.com')
    print(viz_data)

if __name__ == "__main__":
    asyncio.run(main())