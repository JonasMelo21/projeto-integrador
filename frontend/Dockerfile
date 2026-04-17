FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/rentmaster.conf
COPY . /usr/share/nginx/html/

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=2 \
    CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
