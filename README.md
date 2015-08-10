To run:

```
git clone https://github.com/jgors/data_crawlers
cd data_crawlers
scrapy crawl crcns
```

The first time it is run, it generates a cookie from just crawling a single
dataset.  Then the next time it is run, it uses that cookie to crawl the 
whole site.
