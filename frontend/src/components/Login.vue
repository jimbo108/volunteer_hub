<template>
    <div>
        <input id="email" v-model="email" :disabled="inputsActive == 1 ? false : true"/>
        <input id="password" v-model="password" :disabled="inputsActive == 1 ? false : true"/>
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
            email: "",
            password: "",
            validMessage: "",
            inputsActive: true,
            submittedMsg: "",
            submitResult: ""
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
            const email = this.email
            const password = this.password

            this.clearAndDisableInputs()

            const emailValidated = this.validateEmail(email)
            const passwordValidated = this.validatePassword(password)

            if (!emailValidated || !passwordValidated) {
                this.handleInvalidInput(emailValidated, passwordValidated)
            }
            else {
                this.handleValidInput(email, password)
            }
            this.enableInputs()
        },
        handleValidInput (email, password) {
            const path = "http://localhost:5001/api/submit_login"
            const requestDict = this.createUserRequest(email, password)
            axios.post(path, requestDict)
                .then(this.handlePOSTResponse)
                .catch(this.handlePOSTError)
            
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
        handlePOSTError (err) {
            this.submittedMsg = "There was a problem with the server.  Please contact an administrator."
        },
        handleInvalidInput (emailValidated, passwordValidated) {
            if (!emailValidated)  {
                this.validMessage = "Not a valid email address"
            } else if (!passwordValidated) {
                this.validMessage = "Password must be nine or more characters"
            }
        },
        clearAndDisableInputs () {
            this.inputsActive = false
            this.buttonActive = false
            this.email = ""
            this.password = ""
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
        createUserRequest (email, password) {
            return {
                email: email,
                password: password
            }
        },
        handleFailedSubmission () {
            const errorMessage = this.submitResult.data.error_string
            if (errorMessage == null) {
                this.submittedMsg = "Registration failed for an unknown reason."
            } else {
                this.submittedMsg = errorMessage
            }
        },
        handleSuccessfulSubmssion () {
            this.submittedMsg = "Registration successful!"
            // TODO: Redirect to user home page
        }

    }

}
</script>