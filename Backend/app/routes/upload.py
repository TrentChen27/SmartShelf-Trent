from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.utils.r2_storage import r2_storage

bp = Blueprint('upload', __name__, url_prefix='/api/upload')


@bp.route('/image', methods=['POST'])
@jwt_required()
def upload_image():
    """Upload an image to R2 storage"""
    print("=" * 80)
    print("IMAGE UPLOAD REQUEST RECEIVED")
    print("=" * 80)

    claims = get_jwt()
    role = claims.get('role')
    print(f"[LOG] User role: {role}")

    # Only manager and region can upload images
    if role not in ['manager', 'region']:
        print(f"[LOG] Unauthorized role: {role}")
        return jsonify({'error': 'Unauthorized'}), 403

    # Check if file is in request
    print(f"[LOG] Request files: {list(request.files.keys())}")
    if 'file' not in request.files:
        print("[LOG] ERROR: No file in request")
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    print(f"[LOG] File received: {file.filename}")
    print(f"[LOG] File content type: {file.content_type}")
    print(f"[LOG] File size: {file.content_length} bytes")

    if file.filename == '':
        print("[LOG] ERROR: Empty filename")
        return jsonify({'error': 'No file selected'}), 400

    # Validate file type (only images)
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    print(f"[LOG] File extension: {file_ext}")

    if file_ext not in allowed_extensions:
        print(f"[LOG] ERROR: Invalid extension: {file_ext}")
        return jsonify({'error': 'Invalid file type. Only images are allowed.'}), 400

    try:
        print("[LOG] Starting R2 upload...")
        # Upload to R2
        url = r2_storage.upload_file(file, folder='products')
        print(f"[LOG] Upload completed. URL: {url}")

        if not url:
            print("[LOG] ERROR: Upload returned None")
            return jsonify({'error': 'Failed to upload file'}), 500

        print("[LOG] SUCCESS: File uploaded successfully")
        print("=" * 80)
        return jsonify({
            'message': 'File uploaded successfully',
            'url': url
        }), 200

    except Exception as e:
        print(f"[LOG] EXCEPTION during upload: {type(e).__name__}")
        print(f"[LOG] Exception message: {str(e)}")
        import traceback
        print(f"[LOG] Traceback:\n{traceback.format_exc()}")
        print("=" * 80)
        return jsonify({'error': str(e)}), 500
