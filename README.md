# Fast and Lightweight YouTube Scraper for Python

> **Warning:** The user/developer is solely responsible for the use of this code. I am not responsible for copyrights and YouTube restrictions.  
> It is for educational purposes only—do not misuse it.

## Installing

```bash
pip install yt-api-wrapper
```

Or, for faster JSON parsing with [orjson](https://github.com/ijl/orjson):

```bash
pip install yt-api-wrapper[orjson]
```

## How to Use?

This library is simple to use and often requires just a single line of code.  
Here are some quick examples:

```python
from yt_api_wrapper import YouTubeAPIWrapper  # Import the library
yt = YouTubeAPIWrapper()                      # Create API wrapper

yt.auto_complete('pytho')                     # Auto Complete example

video = yt.get_video_info('dQw4w9WgXcQ')      # Get video info

results = yt.search_videos('python course')   # Search videos

channel = yt.get_channel_info('UCuAXFkgsw1L7xaCfnd5JJOw')  # Get channel info
```

### Asynchronous Usage

```python
import asyncio
from yt_api_wrapper import AsyncYouTubeAPIWrapper

yt_async = AsyncYouTubeAPIWrapper()

async def main():
    suggestions = await yt_async.auto_complete('pytho')
    print(suggestions)

    video_info = await yt_async.get_video_info('dQw4w9WgXcQ')
    print(video_info)

    search_results = await yt_async.search_videos('python course')
    print(search_results)

    channel_info = await yt_async.get_channel_info('UCuAXFkgsw1L7xaCfnd5JJOw')
    print(channel_info)

asyncio.run(main())
```

---

## Contribution

Contributions are welcome!  
To contribute, please follow these rules to ensure quality and consistency:

### General Guidelines

- Be respectful and constructive in all communications.
- Make sure your code follows PEP8 style guidelines.
- Write clear commit messages and describe the reason for your change.
- Keep pull requests focused—avoid combining unrelated changes.

### Contributing Process

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes.
4. Add or update tests to cover your changes if necessary.
5. Ensure all tests pass (`pytest` or your preferred runner).
6. Commit your changes (`git commit -m 'Add feature: your feature name'`).
7. Push to your branch (`git push origin feature/your-feature-name`).
8. Open a Pull Request and describe your changes clearly.
9. Respond to any code review feedback.

### Code of Conduct

- Harassment, discrimination, or abusive behavior will not be tolerated.
- Respect all contributors and maintainers.

### Reporting Issues

- Search [existing issues](https://github.com/isa-programmer/yt_api_wrapper/issues) before opening a new one.
- Provide clear and concise information when reporting bugs or requesting features.

---

*This project is not affiliated with or endorsed by YouTube or Google. For educational purposes only.*
