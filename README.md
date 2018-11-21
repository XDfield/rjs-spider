### rjs-spider

> scrapy 的学习

基于 scrapy 的爬虫，爬取"日剧搜"的资源存入 mongodb

#### Requirement

* python 3.6+
* scrapy
* mongodb

#### DateBase

```bash
docker pull mongo
docker run -v $PWD/db:/data/db -p 27017:27017 mongo
```

#### Run

```bash
# 普通抓取，默认从id=1开始递增拉取
scrapy crawl rj
# 指定抓取起始id
scrapy crawl rj -a bPage=233
# 数据库中未完结剧的更新
scrapy crawl rj -a mode=update
# 修复数据库中没有的剧(拉取失败的)
scrapy crawl rj -a mode=fix
```

