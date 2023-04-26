import Vue from 'vue';
import Router from 'vue-router';

import Home from '@/views/Home';
import Auth from '@/views/Auth';
import AuthOIDC from '@/views/AuthOIDC';
import Register from '@/views/Register';
import Main from '@/views/Main';
import Account from '@/views/Account';
import AuthCallback from '@/views/AuthCallback';
import Book from '@/views/Book';
import Author from '@/views/Author';
import Series from '@/views/Series';
import EditProfile from '@/views/EditProfile';
import Report from '@/views/Report';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/home',
    },
    {
      path: '/home',
      name: 'Home',
      component: Home,
    },
    {
      path: '/auth',    // todo this one
      name: 'Auth',
      component: AuthOIDC,
    },
    // {
    //   path: '/register',
    //   name: 'Register',
    //   component: Register,
    // },
    {
      path: '/main',
      name: 'Main',
      component: Main,
    },
    {
      path: '/account',
      name: 'Account',
      component: Account,
    },
    {
      path: '/auth_callback',
      name: 'AuthCallback',
      component: AuthCallback,
    },
    {
      path: '/book/:id',
      component: Book,
    },
    {
      path: '/author/:id',
      component: Author,
    },
    {
      path: '/series/:id',
      component: Series,
    },
    {
      path: '/report',
      component: Report,
    },
    // {
    //   path: '/edit_profile',
    //   name: 'edit_profile',
    //   component: EditProfile,
    //   props: true,
    // },
  ],
});
