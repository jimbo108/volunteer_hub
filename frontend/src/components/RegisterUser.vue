<template>
    <div>
        <b-input-group prepend="email">
            <b-input id="inlineFormInputGroupEmail" placeholder="Email" v-model="email" :disabled="inputsActive == 1? false: true" />
        </b-input-group>
        <b-input-group prepend="password">
            <b-input type="password" id=inlineFormInputGroupPassword placeholder="Password" v-model="password" :disabled="inputsActive == 1? false: true"/>
        </b-input-group>
        <b-input-group prepend="first name">
            <b-input id=inlineFormInputGroupFirstName placeholder="First Name" v-model="firstName" :disabled="inputsActive == 1? false: true"/>
        </b-input-group>
        <b-input-group prepend="last name">
            <b-input id=inlineFormInputGroupLastName placeholder="Last Name" v-model="lastName" :disabled="inputsActive == 1? false: true"/>
        </b-input-group>
        <b-input-group prepend="phone number">
            <b-input id=inlineFormInputGroupPhoneNumber placeholder="Phone Number" v-model="phoneNumber" :disabled="inputsActive == 1? false: true"/>
        </b-input-group>
        <br/>
        <button id="submit" v-on:click="submit" :disabled="buttonActive == 1 ? false : true">Submit</button>
        <p> {{ validMessage }} </p>
        <p> {{ submittedMsg }} </p>
    </div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      email: '',
      password: '',
      firstName: '',
      lastName: '',
      phoneNumber: '',
      validMessage: '',
      inputsActive: true,
      submittedMsg: '',
      submitResult: ''
    }
  },
  computed: {
    buttonActive: {
      get () {
        return this.email.length > 0 && this.password.length > 0
      },
      set () {
        return
      }
    }

  },
  methods: {
    submit () {
      let input = {}

      input.email = this.email
      input.password = this.password
      input.firstName = this.firstName
      input.lastName = this.lastName
      input.phoneNumber = this.phoneNumber

      this.clearAndDisableInputs()

      let validated = this.validateInputs(input)

      let allInputsValid = this.allInputsValid(validated)

      if (!allInputsValid) {
        this.handleInvalidInput(validated)
      } else {
        this.handleValidInput(input)
      }

      this.enableInputs()

    },
    validateInputs (input) {
      let validated = {}

      validated.email = this.validateEmail(input.email)
      validated.password = this.validatePassword(input.password)
      validated.phoneNumber = this.validatePhoneNumber(input.phoneNumber)
      validated.name = this.validateName(input.firstName, input.lastName)

      return validated
    },
    allInputsValid (validated) {
      if (!validated.email || !validated.password || !validated.phoneNumber || !validated.name) {
        return false
      } else {
        return true
      }
    },
    handleValidInput (email, password) {
      const path = 'http://localhost:5001/api/submit_login'
      const requestDict = this.createUserRequest(email, password)
      axios.post(path, requestDict)
        .then(this.handlePOSTResponse)
        .catch(this.handlePOSTError)
    },
    handleInvalidInput (validated) {
      if (!validated.email) {
        this.validMessage = 'Not a valid email address'
      } else if (!validated.password) {
        this.validMessage = 'Password must be nine or more characters'
      }
    },
    handlePOSTResponse (response) {
      if (response == null) {
        this.handleFailedSubmission()
      }
      this.submitResult = response
      const success = this.submitResult.data.success

      if (!success) {
        this.handleFailedSubmission()
      } else {
        this.handleSuccessfulSubmission()
      }
    },
    // eslint-disable-next-line handle-callback-err
    handlePOSTError (err) {
      this.submittedMsg = 'There was a problem with the server.  Please contact an administrator.'
    },
    clearAndDisableInputs () {
      this.inputsActive = false
      this.buttonActive = false
      this.email = ''
      this.password = ''
    },
    enableInputs () {
      this.inputsActive = true
      this.buttonActive = true
    },
    validateEmail (email) {
      return true
    },
    validatePassword (password) {
      return true
    },
    validateName (firstName, lastName) {
      return true
    },
    validatePhoneNumber (phoneNumber) {
      return true
    },

    createUserRequest (email, password) {
      return {
        email: email,
        password: password
      }
    },
    handleFailedSubmission () {
      const errorMessage = this.submitResult.data.error_string
      if (errorMessage == null) {
        this.submittedMsg = 'Registration failed for an unknown reason.'
      } else {
        this.submittedMsg = errorMessage
      }
    },
    handleSuccessfulSubmssion () {
      this.submittedMsg = 'Registration successful!'
      // TODO: Redirect to user home page
    }

  }

}
</script>
