FROM nginx:alpine

# Simple nginx config that proxies to the host systemd service
RUN echo 'server { \
    listen 80; \
    location / { \
        proxy_pass http://host.docker.internal:5000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
        client_max_body_size 16M; \
        proxy_connect_timeout 120s; \
        proxy_send_timeout 120s; \
        proxy_read_timeout 120s; \
    } \
}' > /etc/nginx/conf.d/default.conf
