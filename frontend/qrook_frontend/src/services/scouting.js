import { HTTP } from '@/services/http';

function log_event(event, data={}) {
  let token = localStorage.getItem('auth_token')
  if (!token) return

  // let time = Math.round(Date.now() /1000)
  // HTTP.post('events', {
  //   time: time,
  //   event: event,
  //   data: data
  // })
  //   .then(function (response) {})
  //   .catch(function (error) {
  //     console.log(error.response)
  //   });
}

export {log_event}
