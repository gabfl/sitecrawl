# sitecrawl

[![Pypi](https://img.shields.io/pypi/v/sitecrawl.svg)](https://pypi.org/project/sitecrawl)
[![Build Status](https://github.com/gabfl/sitecrawl/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/gabfl/sitecrawl/actions)
[![codecov](https://codecov.io/gh/gabfl/sitecrawl/branch/main/graph/badge.svg)](https://codecov.io/gh/gabfl/sitecrawl)
[![MIT licensed](https://img.shields.io/badge/license-MIT-green.svg)](https://raw.githubusercontent.com/gabfl/sitecrawl/main/LICENSE)

Simple Python module to crawl a website and extract URLs.

## Installation

Using pip:

```bash
pip3 install sitecrawl

sitecrawl --help
```

Or build from sources:

```bash
# Clone project
git clone https://github.com/gabfl/sitecrawl && cd sitecrawl

# Installation
pip3 install .
```

## Usage

### CLI

```bash
sitecrawl --url https://www.yahoo.com/ --depth 2 --max 4 --verbose
```

->

```
* Found 4 internal URLs
  https://www.yahoo.com
  https://www.yahoo.com/entertainment
  https://www.yahoo.com/lifestyle
  https://www.yahoo.com/plus

* Found 5 external URLs
  https://mail.yahoo.com/
  https://news.yahoo.com/
  https://finance.yahoo.com/
  https://sports.yahoo.com/
  https://shopping.yahoo.com/

* Skipped 0 URLs
```

### As a module

Basic example:

```py
from sitecrawl import crawl

crawl.base_url = 'https://www.yahoo.com'
crawl.deep_crawl(depth=2)

print('Internal URLs:', crawl.get_internal_urls())
print('External URLs:', crawl.get_external_urls())
print('Skipped URLs:', crawl.get_skipped_urls())
```

A more detailed example is available in [example.py](https://github.com/gabfl/sitecrawl/blob/main/example.py).
