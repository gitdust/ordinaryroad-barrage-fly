/*
 * Copyright 2023 OrdinaryRoad
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import errorCode from './errorCode'

// Create a custom axios instance
export default function (context, inject) {
  // $dialog和$snackbar必须通过context.$xxx方式调用
  const {
    $axios
    // route,
    // app
  } = context
  // const {
  // store
  // router
  // } = app
  // 请求拦截器
  $axios.onRequest((config) => {
    // ignore
  })

  // 响应拦截器
  $axios.interceptors.response.use((res) => {
    // 未设置状态码则默认成功状态
    const code = res.data.code || 200
    if (code === 200) {
      return res.data
    } else {
      // 获取错误信息
      const msg = errorCode[code] || res.data.msg || errorCode.default
      process.client && context.$snackbar.error(msg)
      return Promise.reject(msg)
    }
  },
  (error) => {
    // Object.keys(error).forEach((key) => {
    //   console.log(key, error[key])
    // })
    const { response } = error
    // const status = response.status
    // let { message } = error
    // if (message === 'Network Error') {
    //   message = '后端接口连接异常'
    // } else if (message.includes('timeout')) {
    //   message = '系统接口请求超时'
    // } else if (message.includes('Request failed with status code')) {
    //   message = '系统接口' + message.substr(message.length - 3) + '异常'
    // }
    process.client && context.$snackbar.error(response.data || response.data.message || error.message)
    return Promise.reject(error)
  })
}