# SEO for public web content

## Applicability and scope

Before implementing a web feature, identify which routes are intended for public search discovery. Apply this policy to those routes and to changes affecting their URLs, rendering or indexing. For an internal app, authenticated dashboard, API-only service or non-web project, record SEO as not applicable with a brief reason. Keep authentication and access control for private content; robots directives are not security controls.

Use the existing framework's metadata/routing facilities. Do not add an SEO service, plugin, rendering migration or crawler infrastructure without a demonstrated need. Search-engine guidance changes: verify relevant official documentation when implementing. No checklist, score or structured data guarantees indexing, rich results or ranking.

## Baseline for applicable pages

- Provide useful, accurate content for people, descriptive page titles, useful page-specific descriptions, semantic headings, descriptive links and appropriate image alternative text. Avoid keyword stuffing, hidden text and fabricated content. Google may choose different titles/snippets; meta keywords are not a Google ranking mechanism.
- Make intended content and navigation discoverable through crawlable links with real href URLs. Verify the rendered content and essential resources are accessible to the intended crawler. Choose static, server or client rendering based on actual needs and verified crawler support; do not mandate a framework rewrite merely for SEO.
- Return appropriate HTTP status codes: successful content, permanent redirects for permanent moves, and genuine 404/410 responses for removed content where appropriate. Avoid returning a success page for every missing URL. Check redirect loops and chains.
- Define preferred URLs and consistent canonical signals for duplicate variants. Align internal links and sitemap entries with that choice; avoid conflicting canonical declarations and accidental canonicals to staging. Treat canonicalization as a signal, not access control or a guaranteed directive.
- Check robots.txt and meta/X-Robots-Tag directives together. robots.txt controls crawling, not reliable exclusion from search. A crawler must be allowed to fetch a page to see noindex. Protect private/staging content with access controls; do not expose it merely to let a crawler see a directive. Verify intended public production pages do not inherit staging noindex settings.
- When discovery warrants a sitemap, include intended canonical, indexable URLs, accurate lastmod values where supplied and no private/redirect/error URLs. A small well-linked site need not gain a sitemap generator solely to satisfy a checklist.
- Add structured data only for supported, relevant types matching visible truthful content; validate required properties and eligibility against the current feature documentation. Use reciprocal hreflang annotations only for genuine language/region alternatives, with consistent canonical handling.
- Maintain a usable mobile layout, accessibility and efficient loading. Set performance budgets appropriate to users; inspect Core Web Vitals with field data where available. Distinguish lab diagnostics from real-user measurements and disclose missing field data. Social sharing metadata may improve previews but is not proof of search ranking.

## Verification and release review

For affected page types, include representative URLs and expected indexability in existing feature verification notes. Check responses/redirects, rendered content, title/description, canonical, robots directives and links. Validate sitemap entries, structured data and language alternates only when used. Automate stable assertions using existing tooling; do not require a paid SEO product or universal perfect score.

Before release, inspect production configuration for domain/canonical/robots mistakes without publishing or changing access as part of the check. Record command/tool, environment, date and actual results. After authorized deployment, use Search Console URL Inspection/indexing reports and Rich Results Test when relevant and accessible. Mark unavailable live checks as NOT RUN with the reason and follow-up owner; never substitute a local audit for proof of indexing. For URL migrations, review redirects and monitor indexing/traffic after release.

## Official references

Reviewed 2026-11-12. These are search-engine recommendations, not a universal certification; check other target engines when relevant.

- [Google SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
- [Technical search guidance](https://developers.google.com/search/docs/fundamentals/get-started)
- [Blocking indexing with noindex](https://developers.google.com/search/docs/crawling-indexing/block-indexing)
- [Core Web Vitals and Search](https://developers.google.com/search/docs/appearance/core-web-vitals)
- [Structured data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
- [Localized versions and hreflang](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Canonical URL guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
