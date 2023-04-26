import {HTTP} from '@/services/http'
import {HttpResponse} from './common'

var querystring = require('querystring');
require('dotenv').config();

class UserToken extends HttpResponse {
  constructor(ok, access_token, id_token) {
    super(ok);
    this.access_token = access_token;
    this.id_token = id_token;
  }
}


class UserLogin extends HttpResponse {
  constructor(ok, token) {
    super(ok);
    this.token = token;
  }
}

class UserRegister extends HttpResponse {
  constructor(ok, reason, token) {
    super(ok);
    this.reason = reason;
    this.token = token;
  }
}

class UserDelete extends HttpResponse {
  constructor(ok, reason) {
    super(ok);
    this.reason = reason;
  }
}

class UserUpdate extends HttpResponse {
  constructor(ok, reason) {
    super(ok);
    this.reason = reason;
  }
}

class UserInfo extends HttpResponse {
  constructor(ok, reason, data) {
    super(ok);
    this.reason = reason;
    if (!data) return
    this.name = data.name;
    this.last_name = data.last_name;
    this.avatar = data.avatar;
    this.email = data.email;
    this.login = data.login;
    this.password = data.password;
  }
}

class Report extends HttpResponse {
  constructor(ok, reason, data) {
    super(ok);
    this.reason = reason;
    if (!data) return
    this.downloads_cnt = data.downloads_cnt
    this.search_cnt = data.search_cnt
    this.most_frequent_search = data.most_frequent_search
    this.views_cnt = data.views_cnt
    this.most_frequent_entities = data.most_frequent_entities
  }
}


class UserRepository {
  constructor() {
    this.client_id = process.env.CLIENT_ID
    this.client_secret = process.env.CLIENT_SECRET
    console.log(process.env)
  }

  make_oidc_auth_url() {
    let params = querystring.stringify({
      client_id: this.client_id,
      scope: 'openid profile',
      response_type: 'code'
    })
    return HTTP.defaults.baseURL + 'oauth/authorize?' + params
  }

  get_token(code, callback) {
    let http_callback = (response) => {
      const access_token = response.data.access_token;
      const id_token = response.data.id_token;
      callback(new UserToken(true, access_token, id_token))
    };
    let http_err_callback = (error) => {
      console.log(error.message);
      callback(new UserToken(false, null, null))
    }

    let config = {
      auth: {
        username: this.client_id,
        password: this.client_secret
      }
    }

    const formData = new FormData();
    formData.append('grant_type', 'authorization_code');
    formData.append('code', code);

    HTTP.post('oauth/token', formData, config).then(http_callback).catch(http_err_callback);
  }


  login(login, password, callback) {
    let http_callback = (response) => {
      const token = response.data.access_token;
      callback(new UserLogin(true, token))
    };
    let http_err_callback = (error) => {
      console.log(error.message);
      callback(new UserLogin(false, null))
    }

    HTTP.post('users/login', {
      login: login,
      password: password,
    }).then(http_callback).catch(http_err_callback);
  }

  user_info(callback) {
    let http_callback = (response) => {
      callback(new UserInfo(true, null, response.data))
    };
    let http_err_callback = (error) => {
      console.log(error.message);
      let reason = 'unknown error';
      if (error.response)
        reason = error.response.data
      callback(new UserInfo(false, reason, null))
    }

    HTTP.get('users', {params: {}}).then(http_callback).catch(http_err_callback);
  }

  register(data, callback) {
    let http_callback = (response) => {
      callback(new UserRegister(true, null, response.data))
    };
    let http_err_callback = (error) => {
      console.log(error.message);
      let reason = 'unknown error';
      if (error.response)
        reason = error.response.data
      callback(new UserRegister(false, reason, null))
    }

    HTTP.post('users', data).then(http_callback).catch(http_err_callback);
  }

  update_profile(data, callback) {
    let http_callback = (response) => {
      callback(new UserUpdate(true, null))
    };
    let http_err_callback = (error) => {
      console.log(error.message);
      let reason = 'unknown error';
      if (error.response)
        reason = error.response.data
      callback(new UserUpdate(false, reason))
    }

    HTTP.put('users', data).then(http_callback).catch(http_err_callback)
  }

  delete_profile(callback) {
    let http_callback = (response) => {
      callback(new UserDelete(true, null))
    };
    let http_err_callback = (error) => {
      console.log(error.message);
      let reason = 'unknown error';
      if (error.response)
        reason = error.response.data
      callback(new UserDelete(false, reason))
    }

    HTTP.delete('users').then(http_callback).catch(http_err_callback)
  }

  generate_report(time_from, time_to, callback) {
    let http_callback = (response) => {
      callback(new Report(true, null, response.data))
    };
    let http_err_callback = (error) => {
      console.log(error.message);
      let reason = 'unknown error';
      if (error.response)
        reason = error.response.data
      callback(new Report(false, reason, null))
    }

    HTTP.get('report', {params: {'time_start': time_from, 'time_end': time_to}}).then(http_callback).catch(http_err_callback)
  }
}

export let user_repo = new UserRepository()

export function fillUserInfo(obj) {
  let callback = (userInfo) => {
    let failed = !userInfo.ok;
    if (failed) {
      if (userInfo.reason === 'token expired') {
        obj.$store.dispatch('account/logout')
        obj.$router.push('/auth')
      }
    } else {
      obj.$store.dispatch('account/user_info', userInfo)
    }
  }

  user_repo.user_info(callback)
}
