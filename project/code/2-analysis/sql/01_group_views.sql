-- View metrik per grup dan per hari dalam seminggu. Semua ORDER BY punya tie-breaker.
CREATE OR REPLACE VIEW v_group_summary AS
SELECT grp,
       COUNT(*) AS n,
       SUM(converted) AS konversi,
       SUM(converted) * 1.0 / COUNT(*) AS conv_rate,
       MEDIAN(total_ads) AS median_total_ads,
       AVG(total_ads) AS mean_total_ads
FROM users
GROUP BY grp
ORDER BY grp;

CREATE OR REPLACE VIEW v_day_summary AS
SELECT most_ads_day AS segmen,
       SUM(CASE WHEN grp = 'ad' THEN 1 ELSE 0 END) AS n_ad,
       SUM(CASE WHEN grp = 'psa' THEN 1 ELSE 0 END) AS n_psa,
       SUM(CASE WHEN grp = 'ad' THEN converted ELSE 0 END) * 1.0
         / NULLIF(SUM(CASE WHEN grp = 'ad' THEN 1 ELSE 0 END), 0) AS cr_ad,
       SUM(CASE WHEN grp = 'psa' THEN converted ELSE 0 END) * 1.0
         / NULLIF(SUM(CASE WHEN grp = 'psa' THEN 1 ELSE 0 END), 0) AS cr_psa
FROM users
GROUP BY most_ads_day
ORDER BY segmen;
