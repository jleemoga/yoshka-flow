import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import redis
from app.core.config import get_settings
from app.core.celery_app import celery_app

def test_redis_connection():
    """Test direct Redis connection"""
    settings = get_settings()
    print(f"Testing Redis connection to {settings.REDIS_HOST}...")
    
    try:
        # Create Redis client
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        
        # Test connection
        ping_response = r.ping()
        print(f"Redis ping response: {ping_response}")
        
        # Test set/get
        test_key = "test_key"
        test_value = "test_value"
        r.set(test_key, test_value)
        retrieved_value = r.get(test_key)
        print(f"Redis set/get test: {retrieved_value == test_value}")
        
        # Clean up
        r.delete(test_key)
        print("Redis connection test successful!")
        
    except Exception as e:
        print(f"Redis connection test failed: {str(e)}")
        raise e

def test_celery_connection():
    """Test Celery connection to Redis"""
    print("\nTesting Celery connection...")
    try:
        # Test Celery connection
        i = celery_app.control.inspect()
        active_queues = i.active_queues()
        if active_queues:
            print("Celery workers found:")
            for worker, queues in active_queues.items():
                print(f"Worker: {worker}")
                print(f"Queues: {queues}")
        else:
            print("No Celery workers found. Make sure the worker is running.")
    except Exception as e:
        print(f"Celery connection test failed: {str(e)}")

if __name__ == "__main__":
    print("Starting connection tests...")
    test_redis_connection()
    test_celery_connection()
    print("\nAll tests completed.")
