<template>
    <div>
        <button id="login" @click="redirect($event)">Login</button>
        <br>
        <button id="registerUser" @click="redirect($event)">Register</button>
        <br>
        <button id="registerPartner" @click="redirect($event)">Apply to be a Partner</button>
    </div>
</template>

<script>
var redirectDict = {
  'login': '/login',
  'registerUser': '/registerUser',
  'registerPartner': '/registerPartner'
}

export default {
  methods: {
    redirect (event) {
      const targetId = event.currentTarget.id
      this.$router.push(redirectDict[targetId])
    }
  }
}
</script>

<style>

</style>
