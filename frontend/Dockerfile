FROM node:lts-alpine

WORKDIR /qrook_frontend

ENV PATH /qrook_frontend/node_modules/.bin:$PATH

COPY ./qrook_frontend/package.json /qrook_frontend/package.json
COPY ./qrook_frontend .
RUN npm install
RUN npm install @vue/cli@3.7.0 -g
RUN npm install -g serve

EXPOSE 8080
# start app
#CMD ["npm", "run", "start"]
CMD ["serve", "-s", "dist", "-l", "8080"]
