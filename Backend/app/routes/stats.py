from flask import Blueprint, jsonify, request
from sqlalchemy import text
from app import db

stats_bp = Blueprint('stats', __name__)

def result_to_dict(result):
    return [dict(row._mapping) for row in result]

@stats_bp.route('/api/manager/stats', methods=['GET'])
def get_manager_stats():
    try:
        # 1. Get the range (Safety check: ensure it is an int)
        try:
            range_days = int(request.args.get('range', '30'))
        except ValueError:
            range_days = 30

        # Common date filter string to reuse
        date_filter = f"AND o.order_date >= CURRENT_DATE - INTERVAL '{range_days} days'"

        # --- 1. Sales Trend ---
        trend_sql = text(f"""
            SELECT 
                DATE(order_date) as date, 
                ROUND(SUM(total_amount) / 100.0, 2) as total
            FROM orders o
            WHERE payment_status = true 
            {date_filter}
            GROUP BY DATE(order_date) 
            ORDER BY DATE(order_date) ASC
        """)
        trend_result = db.session.execute(trend_sql).fetchall()

        trend_data = {
            "dates": [str(row.date) for row in trend_result],
            "values": [row.total for row in trend_result]
        }

        # --- 2. Top 5 Products by Revenue ---
        top_products_sql = text(f"""
            SELECT 
                p.product_name, 
                ROUND(SUM(oi.sub_price) / 100.0, 2) as revenue
            FROM orderitem oi
            JOIN product p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.payment_status = true
            {date_filter}
            GROUP BY p.product_name
            ORDER BY revenue DESC
            LIMIT 5
        """)
        prod_result = db.session.execute(top_products_sql).fetchall()

        top_products_data = {
            "names": [row.product_name for row in prod_result],
            "values": [row.revenue for row in prod_result]
        }

        # --- 3. B2B vs B2C Segments ---
        customer_seg_sql = text(f"""
            SELECT 
                CASE 
                    WHEN c.kind = 0 THEN 'Home (B2C)' 
                    WHEN c.kind = 1 THEN 'Business (B2B)' 
                END as segment,
                ROUND(SUM(o.total_amount) / 100.0, 2) as total
            FROM orders o
            JOIN customer c ON o.customer_id = c.id
            WHERE o.payment_status = true
            {date_filter}
            GROUP BY c.kind
        """)
        seg_result = db.session.execute(customer_seg_sql).fetchall()

        segment_data = [
            {"name": row.segment, "value": row.total} for row in seg_result
        ]

        # --- 4. Sales by Category ---
        category_sql = text(f"""
            SELECT 
                p.kind, 
                ROUND(SUM(oi.sub_price) / 100.0, 2) as revenue
            FROM orderitem oi
            JOIN product p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.payment_status = true
            {date_filter}
            GROUP BY p.kind
        """)
        cat_result = db.session.execute(category_sql).fetchall()

        category_data = [
            {"name": row.kind if row.kind else "Uncategorized", "value": row.revenue}
            for row in cat_result
        ]

        # --- 5. Demographics (Age) ---
        age_sql = text(f"""
            SELECT 
                CASE 
                    WHEN h.age < 25 THEN 'Under 25'
                    WHEN h.age BETWEEN 25 AND 35 THEN '25 - 35'
                    WHEN h.age BETWEEN 36 AND 50 THEN '36 - 50'
                    WHEN h.age > 50 THEN 'Over 50'
                    ELSE 'Unknown'
                END as age_range,
                ROUND(SUM(o.total_amount) / 100.0, 2) as total
            FROM orders o
            JOIN customer c ON o.customer_id = c.id
            JOIN home h ON c.id = h.id 
            WHERE o.payment_status = true
            {date_filter}
            GROUP BY age_range
            ORDER BY age_range
        """)
        age_result = db.session.execute(age_sql).fetchall()
        age_data = [{"name": row.age_range, "value": row.total} for row in age_result]

        # --- 6. Business Categories ---
        biz_sql = text(f"""
            SELECT 
                b.category, 
                ROUND(SUM(o.total_amount) / 100.0, 2) as total
            FROM orders o
            JOIN customer c ON o.customer_id = c.id
            JOIN business b ON c.id = b.id
            WHERE o.payment_status = true
            {date_filter}
            GROUP BY b.category
        """)
        biz_result = db.session.execute(biz_sql).fetchall()

        biz_data = [
            {"name": row.category if row.category else "Other", "value": row.total}
            for row in biz_result
        ]

        # --- 7. Regional Sales Chart ---
        region_sql = text(f"""
            SELECT 
                r.region_name, 
                ROUND(SUM(o.total_amount) / 100.0, 2) as total
            FROM orders o
            JOIN store s ON o.store_id = s.id
            JOIN region r ON s.region_id = r.id
            WHERE o.payment_status = true
            {date_filter}
            GROUP BY r.region_name
            ORDER BY total DESC
        """)
        region_result = db.session.execute(region_sql).fetchall()

        region_data = {
            "names": [row.region_name for row in region_result],
            "values": [row.total for row in region_result]
        }

        # --- 8. The "Whale" Hunt ---
        whale_sql = text(f"""
            SELECT 
                CASE 
                    WHEN h.id IS NOT NULL THEN 'Home (B2C)' 
                    WHEN b.id IS NOT NULL THEN 'Business (B2B)' 
                    ELSE 'Unknown' 
                END AS customer_type,
                COUNT(DISTINCT o.id) as total_orders,
                ROUND(AVG(o.total_amount) / 100.0, 2) as avg_order_value,
                ROUND(SUM(o.total_amount) / 100.0, 2) as total_revenue
            FROM orders o
            JOIN customer c ON o.customer_id = c.id
            LEFT JOIN home h ON c.id = h.id
            LEFT JOIN business b ON c.id = b.id
            WHERE o.payment_status = true
            {date_filter}
            GROUP BY customer_type
        """)
        whale_data = result_to_dict(db.session.execute(whale_sql).fetchall())

        # --- 9. Regional Power Rankings ---
        region_rank_sql = text(f"""
            SELECT 
                r.region_name,
                oa.name AS manager_name,
                COUNT(DISTINCT s.id) AS store_count,
                COUNT(o.id) AS total_sales_count,
                ROUND(SUM(o.total_amount) / 100.0, 2) AS total_revenue
            FROM region r
            LEFT JOIN employee e ON r.region_manager = e.id
            LEFT JOIN onlineaccount oa ON e.online_id = oa.online_id
            JOIN store s ON s.region_id = r.id
            JOIN orders o ON o.store_id = s.id
            WHERE o.payment_status = true
            {date_filter}
            GROUP BY r.id, r.region_name, oa.name
            ORDER BY total_revenue DESC
        """)
        region_rank_data = result_to_dict(db.session.execute(region_rank_sql).fetchall())

        # --- 10. The "Dead Stock" Report ---
        # Important: We filter the JOIN, so we only count sales IN THIS PERIOD.
        # If sales in period < 5, it is "dead stock" for this timeframe.
        dead_stock_sql = text(f"""
            SELECT 
                p.product_name,
                s.name as store_name,
                si.stock as current_stock,
                COALESCE(SUM(oi.quantity), 0) as units_sold,
                ROUND(COALESCE(SUM(oi.sub_price), 0) / 100.0, 2) as revenue_generated
            FROM storeinventory si
            JOIN product p ON si.product_id = p.id
            JOIN store s ON si.store_id = s.id
            LEFT JOIN orders o ON o.store_id = si.store_id 
                AND o.payment_status = true 
                AND o.order_date >= CURRENT_DATE - INTERVAL '{range_days} days'
            LEFT JOIN orderitem oi ON p.id = oi.product_id AND oi.order_id = o.id
            GROUP BY p.id, p.product_name, s.name, si.stock
            HAVING si.stock > 20 AND COALESCE(SUM(oi.quantity), 0) < 5
            ORDER BY si.stock DESC
            LIMIT 10
        """)
        dead_stock_data = result_to_dict(db.session.execute(dead_stock_sql).fetchall())

        # --- 11. Sales Team Efficiency ---
        efficiency_sql = text(f"""
            SELECT 
                oa.name AS salesperson_name,
                e.job_title,
                s.name AS store_location,
                e.salary AS annual_salary,
                ROUND(SUM(o.total_amount) / 100.0, 2) AS revenue_generated,
                -- Multiplier should be based on ANNUAL salary vs PERIOD revenue
                -- We might want to normalize salary to the period, but typically raw ratio is fine for comparison
                ROUND((SUM(o.total_amount) / 100.0) / NULLIF(e.salary, 0), 2) AS salary_multiplier
            FROM salesperson sp
            JOIN employee e ON sp.employee_id = e.id
            JOIN onlineaccount oa ON e.online_id = oa.online_id
            JOIN store s ON sp.store_id = s.id
            JOIN orders o ON o.sales_id = sp.employee_id
            WHERE o.payment_status = true
            {date_filter}
            GROUP BY sp.id, oa.name, e.job_title, s.name, e.salary
            ORDER BY revenue_generated DESC
            LIMIT 10
        """)
        efficiency_data = result_to_dict(db.session.execute(efficiency_sql).fetchall())

        return jsonify({
            "trend": trend_data,
            "topProducts": top_products_data,
            "segments": segment_data,
            "categories": category_data,
            "demographics": age_data,
            "bizCategories": biz_data,
            "regionalSales": region_data,
            "whaleData": whale_data,
            "regionalRankings": region_rank_data,
            "deadStock": dead_stock_data,
            "salesEfficiency": efficiency_data
        })

    except Exception as e:
        print(f"Error generating stats: {e}")
        return jsonify({"error": str(e)}), 500