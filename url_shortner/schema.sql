DROP TABLE IF EXISTS short_urls;

CREATE TABLE short_urls (
  url TEXT NOT NULL,
  shortcode TEXT NOT NULL UNIQUE,
  created TIMESTAMP NOT NULL DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')),
  last_redirect TIMESTAMP,
  redirect_count INTEGER DEFAULT 0
);