server {
    listen 80;
    server_name vivat-alushta.ru www.vivat-alushta.ru;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API - убираем /api/ префикс при проксировании
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_cookie_domain localhost vivat-alushta.ru;
        proxy_cookie_domain 89.208.14.214 vivat-alushta.ru;
        proxy_cookie_path / /;

        # CORS headers
        add_header Access-Control-Allow-Origin "http://vivat-alushta.ru" always;
        add_header Access-Control-Allow-Credentials true always;
        
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin "http://vivat-alushta.ru";
            add_header Access-Control-Allow-Credentials true;
            add_header Access-Control-Allow-Methods "GET, POST, OPTIONS, PUT, DELETE";
            add_header Access-Control-Allow-Headers "Authorization, Content-Type";
            return 204;
        }
    }
}