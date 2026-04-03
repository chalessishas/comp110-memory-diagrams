# Signal-Map (hdmap.live) Competitive Analysis

Date: 2026-04-01

## Executive Summary

The campus event discovery market is dominated by **institutional B2B platforms** (Anthology Engage, CampusGroups, Modern Campus Involve) that sell to university administrations. There is a near-total absence of **student-first, bottom-up** products that treat the campus map as the primary interface. hdmap.live occupies a unique position: a real-time, map-centric event aggregator built by and for students, with no institutional sales dependency.

---

## 1. Competitive Landscape

### Tier 1: Institutional Engagement Platforms (B2B, sell to universities)

| Product | Focus | Pricing | Strengths | Weaknesses |
|---------|-------|---------|-----------|------------|
| **CampusGroups** (Ready Education) | All-in-one student life | Enterprise SaaS | Facebook-like social layer; 100+ schools migrated from Anthology | Social media aesthetic feels unprofessional; broad focus dilutes individual features |
| **Modern Campus Involve** | Student engagement + retention | Enterprise SaaS | Connects engagement data to retention metrics; admin dashboards | Top-down adoption; students use it because they have to |
| **Anthology Engage** | Co-curricular tracking | Enterprise SaaS | Deep reporting; legacy market share | Schools actively migrating away; dated UX |
| **Localist** | Campus event calendar | Enterprise SaaS | WCAG-compliant; centralized cross-department calendar | Calendar-only, no map, no social layer |
| **Concept3D** | Interactive campus maps + tours + events | Enterprise SaaS | 3D maps; virtual tours; wayfinding; events calendar overlay | Primarily a marketing/admissions tool; not student-facing daily use |
| **Lounge** | Student engagement | Enterprise SaaS | Modern mobile-first UX; event lifecycle management | New entrant; limited institutional adoption data |

### Tier 2: Student-Facing Event Discovery Apps

| Product | Focus | Scale | Strengths | Weaknesses |
|---------|-------|-------|-----------|------------|
| **Corq** (by Anthology) | Event discovery | 250+ campuses, 130K events/year | QR check-in; calendar integration; org discovery | Slow loading; mixed App Store reviews (2.8-3.5 stars); tied to Anthology ecosystem |
| **IRL** (defunct) | Social event discovery | Was 100+ colleges | $170M raised; viral growth | 95% of 20M users were bots; shut down 2023; SEC investigation |

### Tier 3: Informal / Grassroots Solutions

- **Discord/Slack servers**: Student-run, gated by .edu email. High engagement but fragmented, no map, no event aggregation.
- **Instagram/GroupMe**: Event promotion via stories and group chats. No discovery mechanism.
- **University websites**: Static event calendars. Zero student engagement.

### Tier 4: Map-Centric Campus Apps (closest conceptual competitors)

| Product | Status | Notes |
|---------|--------|-------|
| **Marauder's Map (Olin College)** | Archived (2008-2010) | Real-time student location on campus map. Privacy concerns killed it. |
| **Glassmap (Stanford)** | Defunct | Location-sharing iPhone app. Never scaled beyond Stanford. |
| **MIT Media Lab Marauder's Map** | Research project | WiFi-based occupancy visualization. Academic, not productized. |

---

## 2. Why Competitors Succeed or Fail

### Success Factors
1. **Institutional contracts guarantee distribution.** CampusGroups, Involve, and Localist don't need viral growth -- universities mandate adoption.
2. **Corq works because it's bundled.** Schools using Anthology Engage get Corq for free. Captive audience.
3. **Push notifications drive retention.** 60% of students say campus event calendars are the #1 feature they want in a campus app.
4. **Gamification boosts engagement.** Badges, check-in rewards, and CLE credit tracking create habitual use.

### Failure Factors
1. **IRL's bot catastrophe ($170M burned).** Vanity metrics without real users. Lesson: authentic engagement > growth hacking.
2. **Top-down platforms feel mandatory, not delightful.** Students use CampusGroups because their university chose it, not because they love it.
3. **No map = no spatial context.** Localist and most event calendars are just lists. Students can't answer "what's happening near me right now?"
4. **Poor mobile UX kills adoption.** Corq's App Store reviews consistently cite slow loading and clunky navigation.
5. **Privacy concerns killed location-sharing apps.** Marauder's Map concepts repeatedly fail because students won't share real-time location.

---

## 3. hdmap.live Differentiation

### What hdmap.live has that competitors don't:

| Differentiator | hdmap.live | Competitors |
|----------------|-----------|-------------|
| **Map-first interface** | Building-level heat map with T0-T4 activity levels | Calendar lists, maybe a pin on a map |
| **Multi-source aggregation** | 5 data sources, automatic hourly ingest | Single institutional data feed |
| **No institutional dependency** | Bottom-up, student-built | B2B enterprise sales required |
| **Real-time activity signal** | Heat levels show "what's hot right now" | Static event listings |
| **Campus radio** | AI-generated broadcasts with TTS | Nothing comparable |
| **CLE credit tracking** | Visual indicators for credit-bearing events | Some platforms track but don't visualize |
| **GeoJSON building polygons** | 1,236 polygon-accurate building outlines | Pin drops or simple markers |
| **Free, no login required** | Browse without account | Most require .edu authentication |

### What competitors have that hdmap.live doesn't (gaps to address):

| Gap | Impact | Priority |
|-----|--------|----------|
| **Mobile app (native)** | 90%+ of student usage is mobile | HIGH |
| **Push notifications** | #1 retention driver for event apps | HIGH |
| **Org/club directory** | Students discover groups, not just events | MEDIUM |
| **Social features** | RSVP, friend activity, shared calendars | MEDIUM |
| **Institutional partnerships** | Guaranteed distribution to entire campus | LOW (strategic choice) |
| **Analytics dashboard for orgs** | Event organizers want attendance data | MEDIUM |

---

## 4. Market Size

- **Global student engagement platform market:** $987.6M (2025) -> $2.5B by 2033 (CAGR 11.8%)
- **North America share:** ~40% ($395M in 2025)
- **US higher education enrollment:** ~20M students across 4,000+ institutions
- **TAM for a free, student-facing campus event app:** Hard to monetize directly. Revenue models include:
  - Sponsored event promotion (student orgs pay to boost visibility)
  - University licensing (flip to B2B after proving student adoption)
  - Local business advertising (restaurants, study spots near campus)
  - Premium features (personal schedule optimization, study group matching)

---

## 5. User Acquisition Strategies (What Works for Campus Apps)

### Proven Tactics
1. **Orientation week launch.** 60%+ of successful campus apps launch during orientation when students actively seek campus info.
2. **Student org partnerships.** Give org admins dashboards to manage their events. They become evangelists.
3. **QR codes at physical events.** Bridge offline-to-online. "Scan to see what else is happening tonight."
4. **Campus ambassador program.** 5-10 student ambassadors per campus, compensated with swag or small stipends.
5. **Incentivized check-ins.** Badge systems, streaks, or small rewards for attending events discovered through the app.

### What Doesn't Work
- **Paid ads to students.** CAC too high, students are ad-blind.
- **Mass email blasts.** Low open rates, seen as spam.
- **Trying to go multi-campus too early.** Nail one campus first (UNC), then expand.
- **Bot-driven growth (IRL lesson).** Fake engagement destroys trust and invites SEC scrutiny.

---

## 6. Technical Architecture Insights

### Real-Time Map Apps: Best Practices

| Component | Recommended Approach | hdmap.live Current |
|-----------|---------------------|-------------------|
| **Real-time updates** | Supabase Realtime (Postgres Changes) or WebSocket | SSR + 60s revalidate (not true real-time) |
| **Geospatial queries** | PostGIS `ST_Within` for bounding box queries | Prisma + manual coordinate matching |
| **Map rendering** | MapLibre GL JS (vector tiles, better perf) | Leaflet (raster tiles, adequate) |
| **Push notifications** | Web Push API + service worker, or native app | None |
| **Offline support** | PWA with service worker caching | None |
| **Scaling** | Supabase Realtime cluster handles millions of connections | N/A at current scale |

### Architecture Recommendation
The current Leaflet + SSR + Prisma stack is adequate for single-campus MVP. For scaling:
1. Add Supabase Realtime for live event updates (low effort, high impact)
2. Convert to PWA for offline building data + push notifications
3. Migrate to MapLibre GL JS only if performance becomes an issue with many simultaneous users
4. PostGIS for geospatial queries would improve building matching rate beyond current 74%

---

## 7. Strategic Recommendations

### Short-term (next 4 weeks)
1. **Mobile-responsive redesign.** This is blocking >50% of potential users.
2. **PWA + push notifications.** Web push for event reminders without a native app.
3. **Supabase Realtime integration.** Live heat level updates without page refresh.

### Medium-term (2-3 months)
1. **Student org self-service portal.** Let club leaders post events directly. This creates supply-side network effects.
2. **Event RSVP + attendance tracking.** Students want to know "who else is going." Orgs want attendance data.
3. **Expand data sources.** Add dining events, sports watch parties, study group sessions.

### Long-term (6+ months)
1. **Multi-campus expansion.** Package the data ingestion pipeline so it's configurable per university. Start with peer UNC-system schools.
2. **Revenue model.** Sponsored event promotion for student orgs ($5-20/boost). Local business ads in the map sidebar.
3. **Institutional pitch.** Once organic adoption is proven at UNC, approach Student Affairs for official partnership.

---

## 8. Key Insight

The entire campus event platform market is built on **top-down, B2B sales to university administrations**. No one has successfully built a **bottom-up, student-viral, map-first** campus event product. This is both hdmap.live's greatest opportunity and greatest risk:

- **Opportunity:** If students genuinely prefer a map-first interface over calendar lists, hdmap.live can achieve organic adoption that institutional platforms can't match.
- **Risk:** Without institutional backing, growth depends entirely on word-of-mouth. If the product doesn't reach critical mass at UNC within the first semester, it may stall.

The IRL cautionary tale ($170M burned on fake users) proves that authentic, organic campus engagement is extremely hard to manufacture. hdmap.live's advantage is that it's solving a real, visible problem (what's happening on campus right now?) with a genuinely novel interface (the heat map). The question is whether that's enough to overcome the cold-start problem.

---

Sources:
- [Corq App](https://corq.app/)
- [Concept3D Campus Maps](https://concept3d.com/use-cases/higher-education/)
- [CampusGroups / Ready Education](https://www.readyeducation.com/campusgroups)
- [Lounge Student Engagement](https://about.lounge.live/)
- [Modern Campus Involve](https://moderncampus.com/products/involve/engage-more-students.html)
- [IRL Failure Analysis](https://ideaproof.io/failure/irl)
- [IRL Shutdown - TechCrunch](https://techcrunch.com/2023/06/26/irl-shut-down-fake-users/)
- [Student Engagement Market Size](https://www.marketreportanalytics.com/reports/student-engagement-platform-software-52361)
- [Supabase Realtime Location Sharing](https://supabase.com/blog/postgres-realtime-location-sharing-with-maplibre)
- [Marauder's Map - Olin College](https://github.com/olin/maraudersmap-client)
- [CampusGroups Adoption](https://www.readyeducation.com/en/articles/replacing-anthology-engage-100-institutions-and-counting)
- [Campus App Adoption Strategies](https://blog.campusgroups.com/campusgroups/2021/10/12/how-to-fast-track-adoption-of-your-campus-mobile-app)
- [Student Engagement Trends](https://www.insidehighered.com/news/student-success/college-experience/2024/11/27/using-tech-tools-college-student-campus)
