"""
Search routes blueprint for keyword and semantic search.
"""
from flask import Blueprint, render_template, request, jsonify, current_app, session
import logging
from app.services.json_storage_service import JSONStorageService
from app.services.rag_service import RAGService
from app.utils.validators import validate_query
from app.utils.helpers import extract_excerpt, highlight_keywords
from app.utils.decorators import handle_errors

logger = logging.getLogger(__name__)

search_bp = Blueprint('search', __name__)


@search_bp.route('/')
def search_page():
    """Render search page."""
    return render_template('search.html')


@search_bp.route('/keyword', methods=['POST'])
@handle_errors
def keyword_search():
    """
    Perform keyword-based search across journal entries.
    
    Returns:
        JSON response with search results
    """
    # Get current user from session
    current_user = session.get('current_user', 'harshit')
    storage = JSONStorageService(username=current_user)
    
    data = request.get_json()
    query = data.get('query', '').strip()
    page = data.get('page', 1)
    per_page = data.get('per_page', 10)
    
    if not validate_query(query):
        return jsonify({
            'status': 'error',
            'message': 'Invalid search query'
        }), 400
    
    # Split query into keywords
    keywords = query.lower().split()
    results = []
    
    # Load all entries
    all_entries = storage.load_all_entries()
    
    for date, entries_list in all_entries.items():
        for entry in entries_list:
            content_lower = entry['content'].lower()
            
            # Check if all keywords match (AND logic)
            if all(kw in content_lower for kw in keywords):
                excerpt = extract_excerpt(entry['content'], max_length=150)
                highlighted_excerpt = highlight_keywords(excerpt, keywords)
                
                results.append({
                    "date": date,
                    "entry_id": entry['id'],
                    "excerpt": highlighted_excerpt,
                    "full_text": entry['content'],
                    "highlights": keywords
                })
    
    # Sort by date (most recent first)
    results.sort(key=lambda x: x['date'], reverse=True)
    
    # Pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_results = results[start_idx:end_idx]
    
    return jsonify({
        'status': 'success',
        'search_type': 'keyword',
        'query': query,
        'results': paginated_results,
        'count': len(results),
        'page': page,
        'total_pages': (len(results) + per_page - 1) // per_page
    }), 200


@search_bp.route('/semantic', methods=['POST'])
@handle_errors
def semantic_search():
    """
    Perform semantic search using RAG and LLM.
    
    Returns:
        JSON response with search results and AI summary
    """
    # Get current user from session
    current_user = session.get('current_user', 'harshit')
    
    data = request.get_json()
    query = data.get('query', '').strip()
    top_k = data.get('top_k', 5)
    date_range = data.get('date_range')
    
    if not validate_query(query):
        return jsonify({
            'status': 'error',
            'message': 'Invalid search query'
        }), 400
    
    # Perform semantic search
    rag_service = RAGService(current_app.config['OPENAI_API_KEY'], username=current_user)
    search_results = rag_service.semantic_search(query, top_k, date_range)
    
    # Format results
    formatted_results = []
    for result in search_results['results']:
        formatted_results.append({
            "date": result['date'],
            "entry_id": result['entry_id'],
            "excerpt": result['text'],
            "relevance_score": result['relevance_score'],
            "embedding_similarity": result['similarity']
        })
    
    return jsonify({
        'status': 'success',
        'search_type': 'semantic',
        'query': query,
        'results': formatted_results,
        'count': len(formatted_results),
        'ai_summary': search_results.get('ai_summary', '')
    }), 200
