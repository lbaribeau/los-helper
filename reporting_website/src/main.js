import { createApp } from 'vue'
import VueApexCharts from 'vue3-apexcharts';
import App from './App.vue'

const myApp = createApp(App)
    
myApp.use(VueApexCharts)
myApp.mount('#app')