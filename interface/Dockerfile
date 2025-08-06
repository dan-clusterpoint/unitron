FROM node:18-alpine

WORKDIR /usr/src/app
COPY index.html ./

# install a small static file server and expose the default HTTP port
RUN npm install -g serve
EXPOSE 80

# serve index.html on container start
CMD ["serve", "-l", "80", "."]
