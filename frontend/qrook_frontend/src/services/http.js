const axios = require('axios');
require('dotenv').config();

export const HTTP = axios.create({
  baseURL: process.env.API_URL,
  headers: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
  },
});

export function set_token(token) {
  console.log('setting token', token)
  localStorage.setItem('auth_token', token);
  HTTP.defaults.headers.common.Authorization = `Bearer ${token}`;
}

export function reset_token() {
  localStorage.removeItem('auth_token')
  HTTP.defaults.headers.common.Authorization = undefined
  delete HTTP.defaults.headers.common["Authorization"];
}
