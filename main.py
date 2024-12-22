from flask import Flask, request, send_file
from rembg import remove
from flasgger import Swagger, swag_from
import io
from PIL import Image

app = Flask(__name__)
swagger = Swagger(app)

# @njit("void(f4[:, :, :], f4[:, :, :])", cache=False, nogil=True, parallel=True)
@app.route('/rmbg/', methods=['POST'])
@swag_from({
    'tags': ['Image Processing'],
    'description': 'Removes background from an image',
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
            'description': 'Processed image',
            'content': {
                'image/png': {
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
        
        # Create a BytesIO object to return the image as a response
        img_bytes_io = io.BytesIO(output_image)
        img = Image.open(img_bytes_io)
        
        # Save image to BytesIO object in PNG format
        output_io = io.BytesIO()
        img.save(output_io, format='PNG')
        output_io.seek(0)
        
        # Send the processed image file back as a response
        return send_file(
            output_io,
            mimetype='image/png',
            as_attachment=True,
            download_name='output.png'
        )
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
