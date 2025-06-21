# Fast and lightweight youtube scraper for python
>Warning: The user/developer is solely responsible for the use of this code, I am not responsible for copyrights and YouTube restrictions. It is for educational purposes only, do not misuse it.

## Installing
```
pip install yt-api-wrapper
```

## How to use?
It is very simple to use and only one line. Below are some examples:

```python
>>> from yt_api_wrapper import YouTubeAPIWrapper # Import the library
>>> yt = YouTubeAPIWrapper() # Create API wrapper
>>> yt.auto_complete('pytho') # Auto Complete example
INFO:yt_api_wrapper.yt_api_wrapper:Fetching autocomplete for query: 'pyth'
INFO:yt_api_wrapper.yt_api_wrapper:Found 14 suggestions
['python', 'pythagorean theorem', 'python download', 'python programming', 'pythagorean theorem calculator', 'python compiler', 'python online', 'python dictionary', 'pythagoras', 'python snake', 'pythagorean identities', 'python online compiler', 'pythagorean triples', 'python for loop']

>>> video = yt.get_video_info('dQw4w9WgXcQ') # Get video info with one line
INFO:yt_api_wrapper.yt_api_wrapper:Fetching video info for ID: dQw4w9WgXcQ
INFO:yt_api_wrapper.yt_api_wrapper:Successfully extracted info for video: Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)

>>> results = yt.search_videos('python course') # Search videos
INFO:yt_api_wrapper.yt_api_wrapper:Searching YouTube for videos: 'python course'
```

## How to Contribute

1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add feature'`)
5. Push to the branch (`git push origin feature-name`)
6. Open a Pull Request
