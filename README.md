# Fast and lightweight youtube scraper for python 

> This project still in development, not fully usable

## Usage

```python
from youtube import Youtube
yt = Youtube()
yt.auto_complete('Python')

metadata = yt.info('dQw4w9WgXcQ')
print(metadata)
```


## How to Contribute

1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add feature'`)
5. Push to the branch (`git push origin feature-name`)
6. Open a Pull Request
