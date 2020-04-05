var app = new Vue({
  el: '#app',
  data:  {
    mkl: {},
    info: {},
    report: {},
    pollInterval: '',
    status: ''
  },
  created() {
    this.fetchData();    
    this.pollInterval = setInterval(this.fetchData(), 30000);
  },
  beforeDestroy() {
    clearInterval(this.pollInterval)
  },
  methods: {
    fetchData: function() {
      axios.get('/api/mkl.json?t=' + new Date().getTime())
      .then((response) => {
        this.mkl = response.data;
      });
      axios.get('/api/info.json?t=' + new Date().getTime())
      .then((response) => {
        this.info = response.data;
      });
      axios.get('/api/report.json?t=' + new Date().getTime())
      .then((response) => {
        this.report = response.data;
      });
    }
  },
  computed: {
    experience: function() {
      return this.report.exp + parseInt(this.info.total_exp);
    },
    classname: function() {
      switch (this.info.class) {
        case 'Ass':
          return 'Assassin';
          break; 
        case 'Bar':
          return 'Barbarian';
          break;
        case 'Cle':
          return 'Cleric';
          break;
        case 'Fig':
          return 'Fighter';
          break;
        case 'Brd':
          return 'Bard';
          break;
        case 'Mon':
          return 'Monk';
          break;
        case 'Mag':
          return 'Mage';
          break;
        case 'Pal':
          return 'Paladin';
          break;
        case 'Ran':
          return 'Ranger';
          break;
        case 'Thi':
          return 'Thief';
          break;
        case 'Dru':
          return 'Druid';
          break;
        case 'Alc':
          return 'Alchemist';
          break;
        case 'Dar':
          return 'Anti-Paladin';
          break;
        default:
          return 'Meow';
      }
    }
  }
});