from flask import Flask, request, send_file, jsonify
from video_audio_downloader import VideoAudioDownloader
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
downloader = VideoAudioDownloader(output_dir="downloads")

@app.route('/download', methods=['POST'])
def download_audio():
    """
    Endpoint to download audio from a video URL
    Expects JSON: {"url": "video_url"}
    Returns: Audio file or error message
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400

        url = data['url']
        filepath = downloader.download_audio(url)
        
        # Send the file and then delete it (optional)
        response = send_file(
            filepath,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=os.path.basename(filepath)
        )
        
        # Optional: Delete file after sending
        # @response.call_on_close
        # def cleanup():
        #     os.remove(filepath)
        
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch-download', methods=['POST'])
def batch_download_audio():
    """
    Endpoint to download audio from multiple video URLs
    Expects JSON: {"urls": ["url1", "url2", ...]}
    Returns: JSON with download results
    """
    try:
        data = request.get_json()
        if not data or 'urls' not in data:
            return jsonify({'error': 'No URLs provided'}), 400

        urls = data['urls']
        results = downloader.batch_download(urls)
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # For local testing only
    app.run(host='0.0.0.0', port=8080)