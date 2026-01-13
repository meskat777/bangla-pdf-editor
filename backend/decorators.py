"""
Decorators for Flask routes
"""

from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)


def require_session(session_manager):
    """
    Decorator to validate session exists before processing request.
    
    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @require_session(session_manager)
        def my_endpoint(session_id, session):
            # session_id and session are automatically validated and injected
            return jsonify({'success': True})
    
    Args:
        session_manager: SessionManager instance
        
    Returns:
        Decorated function that validates and loads session
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get session_id from request
            if request.method == 'GET':
                session_id = request.args.get('session_id')
            else:
                data = request.json or {}
                session_id = data.get('session_id')
            
            # Validate session exists
            if not session_id:
                logger.warning("Request missing session_id")
                return jsonify({'error': 'Session ID required'}), 400
            
            if not session_manager.exists(session_id):
                logger.warning(f"Invalid session requested: {session_id}")
                return jsonify({'error': 'Invalid session'}), 404
            
            # Load session
            session = session_manager.load(session_id)
            
            if session is None:
                logger.error(f"Failed to load session: {session_id}")
                return jsonify({'error': 'Failed to load session'}), 500
            
            # Inject session_id and session into the route function
            return f(session_id=session_id, session=session, *args, **kwargs)
        
        return decorated_function
    return decorator


def log_request(logger=None):
    """
    Decorator to log all requests to an endpoint.
    
    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @log_request()
        def my_endpoint():
            return jsonify({'success': True})
    
    Args:
        logger: Logger instance (optional)
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Log request
            logger.info(f"{request.method} {request.path} from {request.remote_addr}")
            
            # Execute function
            result = f(*args, **kwargs)
            
            # Log response status
            if hasattr(result, 'status_code'):
                logger.info(f"Response: {result.status_code}")
            
            return result
        
        return decorated_function
    return decorator
