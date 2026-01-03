from http.server import BaseHTTPRequestHandler
import duckdb
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Parse the fighter name from the URL query
        query = parse_qs(urlparse(self.path).query)
        fighter_name = query.get('name', ['Jon Jones'])[0]

        # 2. Connect to data (Same URLs from your Streamlit app)
        # In a production app, you'd want to cache these or use a database
        fs = duckdb.read_csv("https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fight_stats.csv")
        
        # 3. Perform your logic (Simplified example of your "One Sheet" logic)
        stats = duckdb.sql(f"""
            SELECT 
                sum(CAST(split_part("SIG.STR.", ' of ', 1) AS INTEGER)) as sig_str_landed,
                sum(KD::INTEGER) as knockdowns,
                count(DISTINCT BOUT) as total_fights
            FROM fs 
            WHERE trim(FIGHTER) = '{fighter_name}'
        """).df().to_dict(orient='records')[0]

        # 4. Send Response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode())
