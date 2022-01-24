try:
    from sitecrawl import crawl
except ModuleNotFoundError:
    print('Install sitecrawl first: pip3 install sitecrawl')
    import sys
    sys.exit()

crawl.base_url = 'https://www.github.com'
crawl.no_pound = True  # Trim URLs after #
crawl.no_get = True  # Trim URLs after ?

crawl.deep_crawl(depth=2)

print('Internal URLs:', crawl.get_internal_urls())
print('External URLs:', crawl.get_external_urls())
print('Skipped URLs:', crawl.get_skipped_urls())
