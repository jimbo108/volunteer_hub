<template>
    <div>
        <p>Home Page</p>
        <p>Random number from backend: {{randomNumber}}</p>
        <button @click="getRandom">New random number</button>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    data () {
        return {
            randomNumber: 0
        }
    },
    methods: {
        getRandom () {
            this.randomNumber = this.getRandomFromBackend()
        },
        getRandomFromBackend () {
            const path = 'http://localhost:5001/api/random'
            axios.get(path)
            .then(response => {
                this.randomNumber = response.data.randomNumber
            })
            .catch(error => {
                console.log(error)
            })
        }
    }
}    
</script>
