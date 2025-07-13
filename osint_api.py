#!/usr/bin/env python3
"""
Flask API for OSINT Framework
Provides REST endpoints for the dashboard
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
from osint_framework import OSINTFramework, OSINTTarget

app = Flask(__name__)
CORS(app)

# Initialize framework
config = {
    'neo4j_uri': 'bolt://localhost:7687',
    'neo4j_user': 'neo4j',
    'neo4j_password': 'password',
    'elasticsearch_host': 'localhost:9200',
    'spiderfoot_host': 'http://localhost:5001',
    'shodan_api_key': 'your_shodan_api_key'
}

framework = OSINTFramework(config)

@app.route('/api/collect', methods=['POST'])
def collect_intelligence():
    """Start intelligence collection"""
    data = request.get_json()
    
    target = OSINTTarget(
        target_type=data['target_type'],
        target_value=data['target_value'],
        collection_modules=data['collection_modules']
    )
    
    # Run collection
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        results = loop.run_until_complete(framework.collect_intelligence(target))
        framework.store_results(results)
        
        # Add visualization data
        viz_data = framework.visualize_results(target.target_value)
        results['visualization_data'] = viz_data
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/visualize/<target_value>', methods=['GET'])
def get_visualization(target_value):
    """Get visualization data for a target"""
    try:
        viz_data = framework.visualize_results(target_value)
        return jsonify(json.loads(viz_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_results():
    """Search historical results"""
    query = request.args.get('q', '')
    
    search_body = {
        'query': {
            'multi_match': {
                'query': query,
                'fields': ['target.target_value', 'sources.*']
            }
        }
    }
    
    try:
        results = framework.es_client.search(
            index='osint-results',
            body=search_body
        )
        
        return jsonify({
            'total': results['hits']['total']['value'],
            'results': [hit['_source'] for hit in results['hits']['hits']]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)