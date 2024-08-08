from flask import Flask, request, jsonify
import redis
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

@app.route('/read', methods=['POST'])
def read_structure():
    data = request.json
    collection = data.get('collection')
    document = data.get('document')
    field = data.get('field')

    if not collection:
        return jsonify({"error": "Collection is required."}), 400

    keys = redis_client.keys(f"{collection}:*")

    if not keys:
        return jsonify({"error": f"Collection '{collection}' does not exist."}), 404

    result = {}

    if document:
        document_key = f"{collection}:{document}"
        if redis_client.type(document_key) != b'hash':
            return jsonify({"error": f"Document '{document}' does not exist."}), 404

        if field:
            field_value = redis_client.hget(document_key, field)
            if field_value is None:
                return jsonify({"error": f"Field '{field}' does not exist."}), 404
            return jsonify({field: field_value.decode('utf-8')}), 200
        
        document_fields = redis_client.hgetall(document_key)
        result[document] = {key.decode('utf-8'): value.decode('utf-8') for key, value in document_fields.items()}
        return jsonify(result), 200

    # If document is not provided, return all documents in the collection
    for key in keys:
        key_str = key.decode('utf-8')
        key_parts = key_str.split(':')
        if len(key_parts) == 2:
            collection_name, doc = key_parts
            if collection_name == collection:
                document_fields = redis_client.hgetall(key)
                if doc not in result:
                    result[doc] = {}
                result[doc] = {field.decode('utf-8'): value.decode('utf-8') for field, value in document_fields.items()}

    return jsonify(result), 200

if __name__ == '__main__':
    app.run(port=5001, host="0.0.0.0", debug=True)
