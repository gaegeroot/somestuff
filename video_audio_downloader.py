import yt_dlp
import os
from urllib.parse import urlparse
import logging

class VideoAudioDownloader:
    def __init__(self, output_dir="downloads"):
        """Initialize the downloader with an output directory."""
        self.output_dir = output_dir
        self._setup_logging()
        self._create_output_dir()
        
    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _create_output_dir(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.logger.info(f"Created output directory: {self.output_dir}")

    def _get_platform(self, url):
        """Determine the platform (YouTube or Loom) from the URL."""
        domain = urlparse(url).netloc
        if 'youtube.com' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'loom.com' in domain:
            return 'loom'
        else:
            raise ValueError(f"Unsupported platform for URL: {url}")

    def download_audio(self, url):
        """
        Download audio from a video URL (YouTube or Loom).
        
        Args:
            url (str): The URL of the video
            
        Returns:
            str: Path to the downloaded audio file
        """
        platform = self._get_platform(url)
        self.logger.info(f"Downloading audio from {platform} video: {url}")

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                filename = os.path.splitext(filename)[0] + '.mp3'  # Adjust extension for audio
                
                # Download if file doesn't exist
                if not os.path.exists(filename):
                    ydl.download([url])
                    self.logger.info(f"Successfully downloaded audio: {filename}")
                else:
                    self.logger.info(f"Audio file already exists: {filename}")
                
                return filename

        except Exception as e:
            self.logger.error(f"Error downloading audio from {url}: {str(e)}")
            raise

    def batch_download(self, urls):
        """
        Download audio from multiple video URLs.
        
        Args:
            urls (list): List of video URLs
            
        Returns:
            dict: Dictionary mapping URLs to their downloaded file paths
        """
        results = {}
        for url in urls:
            try:
                filepath = self.download_audio(url)
                results[url] = {
                    'status': 'success',
                    'filepath': filepath
                }
            except Exception as e:
                results[url] = {
                    'status': 'error',
                    'error': str(e)
                }
        return results

# Example usage
if __name__ == "__main__":
    # Initialize downloader
    downloader = VideoAudioDownloader(output_dir="video_audio")
    
    # Example URLs
    urls = [
        "https://www.youtube.com/watch?v=example1",
        "https://www.loom.com/share/example2"
    ]
    
    # Single download
    try:
        filepath = downloader.download_audio(urls[0])
        print(f"Downloaded audio to: {filepath}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Batch download
    results = downloader.batch_download(urls)
    for url, result in results.items():
        if result['status'] == 'success':
            print(f"Successfully downloaded {url} to {result['filepath']}")
        else:
            print(f"Failed to download {url}: {result['error']}")