# Daily Tar Heel + UNC News Sources -- Campus News Radio Research

**Date:** 2026-04-01
**Project:** Signal-Map (hdmap.live) campus radio
**Status:** Research complete, actionable findings

---

## 1. Daily Tar Heel (dailytarheel.com) Technical Analysis

### CMS Platform

DTH runs on **SNworks CEO** (Content Engine Optimized), a headless CMS built by Solutions by SN Media (originated at Michigan State's The State News). This is NOT WordPress. The site relaunched on SNworks in August 2023.

- SNworks CEO is a headless CMS with a REST API (v3)
- Uses JWT authentication (public/private key pair from Settings > Developer Access)
- CEO API docs: https://static.getsnworks.com/ceo/api/
- Content API docs: https://docs.getsnworks.com/ceo2/api/content.html

### CEO Content API Endpoints (Authenticated)

```
GET /v3/content                    -- List articles (paginated)
GET /v3/content/{uuid}             -- Single article by UUID
GET /v3/search?type=content        -- Search articles with filters
```

**Content search parameters:**
- `keywords` -- full-text search
- `tag` -- filter by tag
- `author` -- filter by author
- `filters[content_type]` -- article, post, page, etc.
- `page`, `per_page`, `order`, `dir` -- pagination/sorting

**Response fields per article:** id, uuid, title, slug, type, abstract, content, created_at, modified_at, published_at, state, authors[], tags[], urls[]

**Problem:** API requires JWT auth. We would need DTH developer access credentials. This is not a public API -- it's their internal CMS API.

### RSS Feeds

DTH has a feeds page at https://www.dailytarheel.com/page/feeds but **all direct fetches return 403**. Tested:
- `https://www.dailytarheel.com/feed` -- 403
- `https://www.dailytarheel.com/rss` -- 403
- `https://www.dailytarheel.com/feed/rss` -- 403
- `https://www.dailytarheel.com/rss.xml` -- 403
- `https://www.dailytarheel.com/sitemap.xml` -- 403
- `https://www.dailytarheel.com/robots.txt` -- 403

The entire site aggressively blocks automated/bot requests (403 on all tool-based fetches). This may be Cloudflare or similar WAF protection.

### Google News as Proxy (WORKING)

**This is the viable path.** Google News indexes DTH articles and exposes them via RSS:

```
https://news.google.com/rss/search?q=site:dailytarheel.com&hl=en-US&gl=US&ceid=US:en
```

- Returns ~100 articles
- Includes title, publication date, source, and Google News redirect URL
- Articles span several months of coverage
- Can filter by recency: add `+when:7d` for last 7 days

### URL Structure

DTH articles use two URL patterns:
1. **Slug + date:** `/article/{section}-{topic}-{details}-{YYYYMMDD}` (e.g., `university-bot-meeting-march-2026-20260330`)
2. **UUID:** `/article/{uuid}` (e.g., `ba25e309-07a4-4b17-aad9-29cf9c14fdac`)

### Sections / Categories

From navigation and URL analysis:
- **University** (`/section/campus`) -- UNC administration, faculty, academic news
- **News** (`/section/news`) -- general news
- **Sports** (`/section/sports`) -- UNC athletics
- **City & State** (`/section/city-state`) -- Chapel Hill, Carrboro, NC government
- **Chapel Hill-Carrboro** (`/section/chapel-hill-carrboro`) -- local community
- **Opinion / Editorials** (`/section/editorials`) -- op-eds, letters
- **Topics-based navigation** -- Student Life, Inside UNC, Chapel Hill, plus dozens of subtopics

### Publishing Volume

- **Print:** Wednesday only (10,000 copies to 225+ locations)
- **Online:** Continuous; estimated **8-12 articles/day** during academic year (52-78/week per LinkedIn data)
- **Staff:** ~80 paid students + 150 volunteers + 2 full-time professionals
- **Readership:** ~11,400 unique visitors/day on average school days
- **Letters to editor:** 500 words max; news articles typically 400-800 words

---

## 2. UNC Official News Sources (WORKING RSS Feeds)

### UNC News (uncnews.unc.edu) -- CONFIRMED WORKING

```
Feed URL: https://uncnews.unc.edu/feed/
Format:   RSS 2.0
```

- Official university press releases and announcements
- Categories: Latest News, News, Carolina North, etc.
- Publishing frequency: Low (2-5 articles/month)
- Good for: Major university announcements, milestones, appointments

### UNC The Well (unc.edu) -- CONFIRMED WORKING

```
Feed URL: https://www.unc.edu/feed/
Format:   RSS 2.0
```

- University feature stories, campus life, academics, accolades
- Rich category taxonomy: Campus Life, Academics, Accolades, Faculty and Staff, Health and Medicine, Research, Alumni, Student Stories, Serving N.C., Global, Leadership, etc.
- Publishing frequency: 2-4 articles/day
- Good for: Human interest stories, rankings, achievements, campus culture

### Chapelboro / 97.9 WCHL -- CONFIRMED WORKING

```
Main feed:      https://chapelboro.com/feed
Filtered feed:  https://chapelboro.com/feed?cat=-43
News only:      https://chapelboro.com/category/news/feed
Lifestyle:      https://chapelboro.com/category/lifestyle/feed
WCHL radio:     https://chapelboro.com/category/wchl/feed
Format:         RSS 2.0 (with podcast/iTunes extensions)
```

- Local Chapel Hill/Carrboro news from 97.9 The Hill WCHL
- ~14 articles/day covering local government, sports, community
- Includes columns (Chansky's Notebook), morning/evening news roundups
- Good for: Local news, sports commentary, community events

### Google News UNC Feed -- CONFIRMED WORKING

```
https://news.google.com/rss/search?q=%22UNC+Chapel+Hill%22&hl=en-US&gl=US&ceid=US:en
```

- Aggregates from DTH, local outlets, national press about UNC
- ~100 items per feed
- Good for: Catching DTH articles without direct access

---

## 3. Weather Data -- CONFIRMED WORKING (Free, No Auth)

### National Weather Service API (Chapel Hill)

```
Forecast:        https://api.weather.gov/gridpoints/RAH/59,62/forecast
Hourly forecast: https://api.weather.gov/gridpoints/RAH/59,62/forecast/hourly
Current obs:     https://api.weather.gov/gridpoints/RAH/59,62/stations  (then pick closest station)
Alerts:          https://api.weather.gov/alerts/active?point=35.9132,-79.0558
```

- Grid: RAH (Raleigh office), gridX=59, gridY=62
- Radar station: KRAX
- Forecast zone: NCZ024
- Free, no API key required, rate-limited but generous
- Returns JSON with detailed forecasts, temperature, precipitation, wind

### UNC WeatherSTEM

```
https://orange-nc.weatherstem.com/unc
```

- On-campus weather station data
- Provides hyperlocal campus weather

---

## 4. Campus Radio Context

### WXYC 89.3 FM (Existing UNC Radio)

- UNC's student-run radio station since 1977
- 150 student DJs, 24/7 broadcast
- First radio station to stream on internet (1994)
- Focuses on music (freeform), NOT news
- Not a competitor -- they don't do automated news broadcasts

### Existing News-to-Speech Products

| Product | What | Relevance |
|---------|------|-----------|
| **NewsPod** (UC Berkeley, ACM IUI 2022) | Academic research: auto-generates Q&A-style news podcasts from article clusters | Reference architecture for summarization + TTS pipeline |
| **RadioGPT** (Futuri Media) | Commercial AI radio platform with TopicPulse for local news | Closest commercial product, but targets commercial radio |
| **ReadSpeaker** | Enterprise TTS for news sites (embed audio player on articles) | Widget approach, not broadcast format |
| **ElevenLabs** | News anchor voice library + API | Voice generation tool, not full pipeline |
| **Auphonic** | Podcast post-production automation (leveling, encoding) | Post-processing tool |

**No one does "campus event map + news radio broadcast."** This remains a unique product angle.

---

## 5. TTS Cost Analysis for News Broadcast

Assuming 5 news summaries/day, ~150 words each = 750 words/day = ~4,500 characters/day

| Provider | Model | Cost/day | Cost/month |
|----------|-------|----------|------------|
| DashScope | qwen3-tts-flash | ~$0.001 | ~$0.03 |
| OpenAI | gpt-4o-mini-tts | ~$0.01 | ~$0.30 |
| OpenAI | tts-1 | ~$0.07 | ~$2.10 |
| ElevenLabs | Standard | ~$0.07 | ~$2.10 |

DashScope is essentially free for this volume. OpenAI gpt-4o-mini-tts is the best quality/price balance for English.

---

## 6. Recommended Pipeline Architecture

```
[Cron: every 2 hours during 8am-10pm]
     |
     v
[RSS Fetcher] -- pulls from:
  - Google News (DTH proxy)
  - UNC The Well feed
  - UNC News feed
  - Chapelboro feed
  - NWS Weather API
     |
     v
[Content Deduplicator] -- title similarity + URL matching
     |
     v
[Summarizer (LLM)] -- 3-sentence summary per article
  - Group by category: Campus, Sports, Local, Weather
  - Generate radio script with transitions
     |
     v
[TTS Engine] -- DashScope or OpenAI
  - News anchor voice style
  - Different voices for different segments
     |
     v
[Audio Storage] -- Vercel Blob or R2
     |
     v
[Radio Player] -- plays between music tracks
```

### Key Technical Decisions

1. **DTH access:** Use Google News RSS as proxy (no auth needed, ~100 articles). Fallback: approach DTH for API access or use newspaper3k scraping.
2. **Refresh frequency:** Every 2 hours during waking hours is sufficient for a campus audience.
3. **News script format:** "Good morning, here's your campus update. [weather]. [top 3-5 stories]. That's your update from the Hill."
4. **Audio caching:** Cache generated audio for 2 hours to avoid re-synthesis.

---

## 7. Terms of Service / Legal Considerations

- DTH's 403 responses suggest active bot protection, but Google News indexing means content is publicly available
- Using Google News RSS feeds aggregates headlines + links (fair use for summarization)
- NWS weather data is public domain (US government)
- UNC official feeds are public information
- Chapelboro is a commercial outlet; summarizing (not reproducing) their articles is fair use
- **Best practice:** Link back to original articles, credit sources in broadcast script

---

## Sources

- [Daily Tar Heel](https://www.dailytarheel.com/)
- [Daily Tar Heel Feeds Page](https://www.dailytarheel.com/page/feeds)
- [Daily Tar Heel - Wikipedia](https://en.wikipedia.org/wiki/The_Daily_Tar_Heel)
- [SNworks CEO API Docs](https://static.getsnworks.com/ceo/api/)
- [SNworks CEO Content API](https://docs.getsnworks.com/ceo2/api/content.html)
- [SNworks CEO Search API](https://docs.getsnworks.com/ceo2/api/search.html)
- [SNworks Connector API](https://docs.getsnworks.com/ceo2/front-end/connector-api.html)
- [UNC News RSS](https://uncnews.unc.edu/feed/)
- [UNC The Well RSS](https://www.unc.edu/feed/)
- [Chapelboro RSS Feeds](https://chapelboro.com/rssfeeds)
- [NWS API - Chapel Hill Grid Point](https://api.weather.gov/points/35.9132,-79.0558)
- [Google News RSS Docs (NewsCatcher)](https://www.newscatcherapi.com/blog-posts/google-news-rss-search-parameters-the-missing-documentaiton)
- [NewsPod Paper (ACM IUI 2022)](https://dl.acm.org/doi/10.1145/3490099.3511147)
- [ElevenLabs News Anchor Voices](https://elevenlabs.io/voice-library/news-anchor-voices)
- [OpenAI TTS Pricing](https://costgoat.com/pricing/openai-tts)
- [WXYC About](https://wxyc.org/about)
- [ITU: Broadcast Radio in the Age of AI](https://www.itu.int/hub/2026/02/broadcast-radio-in-the-age-of-ai/)
