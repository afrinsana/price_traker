-- 1. Price Volatility (Standard Deviation)
SELECT 
    product_id,
    STDDEV(price) AS price_volatility
FROM price_history
GROUP BY product_id;

-- 2. Weekly Price Trends
SELECT 
    product_id,
    strftime('%Y-%W', date) AS week,
    AVG(price) AS avg_price
FROM price_history
GROUP BY product_id, week;

-- 3. Optimal Buy Windows (Prices below avg)
SELECT 
    product_id,
    date,
    price
FROM price_history
WHERE price < (SELECT AVG(price) FROM price_history AS ph2 
               WHERE ph2.product_id = price_history.product_id);