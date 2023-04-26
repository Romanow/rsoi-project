<template>
  <div>
    OIDC auth
  </div>
</template>

<script>
import { user_repo } from '@/services/repositories/user';

export default {

  created() {
      window.location.href = user_repo.make_oidc_auth_url();
    },
};
</script>
