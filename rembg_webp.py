from flask import Flask, request, send_file
from rembg import remove
from flasgger import Swagger, swag_from
import io
from PIL import Image
from flask_cors import CORS  # Import Flask-CORS

app = Flask(__name__)
swagger = Swagger(app)

# Enable CORS for all routes
CORS(app)

@app.route('/rmbg/', methods=['POST'])
@swag_from({
    'tags': ['Image Processing'],
    'description': 'Removes background from an image and converts it to WebP format',
    'parameters': [
        {
            'name': 'file',
            'description': 'Image file to process',
            'in': 'formData',
            'type': 'file',
            'required': True
        }
    ],
    'responses': {
        '200': {
            'description': 'Processed image in WebP format',
            'content': {
                'image/webp': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        },
        '400': {
            'description': 'Bad request'
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def remove_bg():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400

    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    try:
        # Read the input image file
        input_image = file.read()

        # Process the image to remove background
        output_image = remove(input_image)

        # Create a BytesIO object to handle image data
        img_bytes_io = io.BytesIO(output_image)
        img = Image.open(img_bytes_io).convert('RGBA')  # Ensure RGBA for transparency

        # Convert image to WebP format
        output_io = io.BytesIO()
        img.save(output_io, format='WEBP', quality=80, lossless=True)  # Save as WebP with transparency and lossless option
        output_io.seek(0)

        # Send the processed image file back as a response
        return send_file(
            output_io,
            mimetype='image/webp',
            as_attachment=True,
            download_name='output.webp'
        )
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
