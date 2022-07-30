var app = new Vue({
  el: '#app',
  data:  {
    mkl: [],
    info: {},
    report: {},
    track_report: [],
    pollInterval: '',
    status: '',
    darkMode: true
  },
  created() {
    this.fetchData();
    this.pollInterval = setInterval(this.fetchData, 30000);
  },
  beforeDestroy() {
    clearInterval(this.pollInterval)
  },
  methods: {
    fetchData: function() {
      console.log("here I go fetching data again...");
      axios.get('api/mkl.json?t=' + new Date().getTime())
      .then((response) => {
        this.mkl = response.data;
      });
      axios.get('api/info.json?t=' + new Date().getTime())
      .then((response) => {
        this.info = response.data;
      });
      axios.get('api/report.json?t=' + new Date().getTime())
      .then((response) => {
        this.report = response.data;
      });
      axios.get('api/track_report.json?t=' + new Date().getTime())
      .then((response) => {
        this.track_report = response.data;
      });
    },
    processExpm: function(track) {
      var duration = 1
      var exp = 0
      if (track.duration && track.duration !== 0) {
        duration = parseFloat(track.duration)/60
      }
      else {
        return 0
      }

      if (track.exp && track.exp != 0) {
        exp = track.exp
      }

      return Math.floor(exp / duration);
    }
  },
  computed: {
    bodyClass: function() {
      return {'dark_mode': this.darkMode}
    },
    sorted_mkl: function() {
      return this.mkl.sort();
    },
    experience: function() {
      return this.report.exp + parseInt(this.info.total_exp);
    },
    exph: function() {
      var output = 0
      if (this.report !== {}) {
        output = this.report.expm*60
      }
      return output
    },
    mobs_killed: function() {
      var list = {};
      if (this.report.mobs_killed) {
        var keys = Object.keys(this.report.mobs_killed)
        for (var i = keys.length - 1; i >= 0; i--) {
          list[keys[i]] = this.report.mobs_killed[keys[i]]
        }
      }
      return list
    },
    effective_phys: function() {
      var output = 0
      if (this.report !== {}) {
        output = Math.round((this.report.phys_hit_rate/100 * this.report.average_phys_damage)*100)/100
      }
      return output
    },
    effective_spell: function() {
      var output = 0
      if (this.report !== {}) {
        output = Math.round((this.report.spell_hit_rate/100 * this.report.average_spell_damage)*100)/100
      }
      return output
    },
    total_kills: function() {
      var count = 0
      if (this.report.mobs_killed) {
        var keys = Object.keys(this.report.mobs_killed)
        for (var i = keys.length - 1; i >= 0; i--) {
          count += this.report.mobs_killed[keys[i]]
        }     
      }
      return count
    },
    kpm: function() {
      var output = 0
      var runtime = Math.round(this.report.runtime)

      if (runtime == 0) {
        return -1
      }

      return Math.round((this.total_kills*100)/runtime)/100
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