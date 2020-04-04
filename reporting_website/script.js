var app = new Vue({
  el: '#app',
  data:  {
    json: '{}',
    pollInterval: null,
    status: ''
  },
  mounted() {
    this.fetchData();
    
    if (this.status != 'completed') {
      this.pollInterval = setInterval(this.fetchData(), 120000);
    }
  },
  methods: {
    fetchData: function() {      
      axios.get('/los-helper/main/report.json')
      .then((response) => {
        this.json = response.data;
      });
    }
  },
  computed: {
    report: function() { 
      return this.json
    }, 
    experience: function() {
      return this.report.exp + parseInt(this.report.total_exp);
    },
    classname: function() {
      switch (this.report.class) {
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