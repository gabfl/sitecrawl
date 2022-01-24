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
sitecrawl --url http://www.gab.lc --depth 3

# Add --verbose for verbose mode
```

->

```
* Found 4 internal URLs
  http://www.gab.lc
  http://www.gab.lc/articles
  http://www.gab.lc/contact
  http://www.gab.lc/about

* Found 8 external URLs
  https://gpgtools.org/
  http://en.wikipedia.org/wiki/GNU_General_Public_License
  http://en.wikipedia.org/wiki/Pretty_Good_Privacy
  http://en.wikipedia.org/wiki/GNU_Privacy_Guard
  https://www.gpgtools.org
  https://www.google.com/#hl=en&q=install+gpg+windows
  http://www.gnupg.org/gph/en/manual/x135.html
  http://keys.gnupg.net

* Skipped 0 URLs
```

### As a module

Basic example:

```py
from sitecrawl import crawl

crawl.base_url = 'https://www.github.com'
crawl.deep_crawl(depth=2)

print('Internal URLs:', crawl.get_internal_urls())
print('External URLs:', crawl.get_external_urls())
print('Skipped URLs:', crawl.get_skipped_urls())
```

A more detailed example is available in [example.py](https://github.com/gabfl/sitecrawl/blob/main/example.py).
