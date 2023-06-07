<template>
<div class="wrapper columns">
  <div class="column">
    <div class="box"><strong>{{info.name}} the {{info.race}} {{classname}}</strong>
      <div class="stat">Level {{info.level}}</div>
      <div class="stat">HP {{report.hp}} / {{info.hp}}</div>
      <div class="stat">MP {{report.mp}} / {{info.mp}}</div>
    </div>
    <div class="box">
      <strong>Recent State</strong>
      <div class="stat">As of {{adjustedTimestamp}}</div>
      <div class="stat">Fighting {{report.mobs}}</div>
      <div class="stat">Area {{report.area}}</div>
      <div class="stat">Total runtime {{report.runtime}}</div>
      <div class="stat">Resting {{report.percent_rest}}% of the time</div>
      <div class="stat">Tracking {{report.percent_track}}% of the time</div>
      <div class="stat">Fighting {{report.percent_combat}}% of the time</div>
    </div>
    <div class="box"><strong>Juicy reporting...</strong>
      <div class="stat">Current Aura: {{report.aura}}</div>
      <div class="stat">EXP/Min: {{report.expm}} ({{this.exph}}/hr)</div>
      <div class="stat">Exp Gained: {{report.exp}}</div>
      <div class="stat">Hit Rate (Phys): {{report.phys_hit_rate}}%</div>
      <div class="stat">Avg Dmg (Phys): {{report.average_phys_damage}} ({{effective_phys}})</div>
      <div class="stat">Crit Rate (attack): {{crit_to_attack}}%</div>
      <div class="stat">Crit Rate (hit): {{crit_to_hit}}%</div>
      <div class="stat">Attack/Hit/Crit: {{report.total_phys_attacks}}/{{report.total_phys_hits}}/{{report.phys_crits}}</div>
      <div class="stat">Hit Rate (Spell): {{report.spell_hit_rate}}%</div>
      <div class="stat">Avg Dmg (Spell): {{report.average_spell_damage}} ({{effective_spell}})</div>
      <div class="stat">Crit Rate (cast): {{crit_to_cast}}%</div>
      <div class="stat">Crit Rate (hit): {{crit_to_cast_hit}}%</div>
      <div class="stat">Cast/Hit/Crit: {{report.spells_cast}}/{{report.spells_hit}}/{{report.spell_crits}}</div>
      <div class="stat">Total KILLS: {{total_kills}}</div>
      <div class="stat">KPM: {{this.kpm}}</div>
      <div class="stat">DEATHS {{report.deaths}}</div>
    </div>
    <div class="box"><strong>Paper doll...</strong>
      <div class="stat">Preferred Aura: {{info.preferred_aura}}</div>
      <div class="stat">Exp: {{experience}}</div>
      <div class="stat">Exp To Level: {{info.exp_to_level}}</div>
    </div>
    <div class="box"><strong>Stats...</strong>
      <apexchart width="250" type="radar" :options="statOptions" :series="statSeries"></apexchart>
      <div class="stats" :key="stat.name" v-for="stat in info.stats">
        <div class="stat">{{stat.name}} {{stat.value}}</div>
      </div>
    </div>
    <div class="box"><strong>Debug stuff...</strong>
      <div class="stat">Last Direction: {{report.last_direction}}</div>
      <div class="stat">Sucessful Go: {{report.successful_go}}</div>
      <div class="stat">Blocking Mob: [{{report.blocking_mob}}]</div>
      <div class="stat">Please Wait: {{report.go_please_wait}}</div>
      <div class="stat">No Exit: {{report.go_no_exit}}</div>
      <div class="stat">Timeout: {{report.go_timeout}}</div>
      <div class="stat">Confused: {{report.confused}}</div>
      <div class="stat">Can See: {{report.can_see}}</div>
    </div>
  </div>
  <div class="column is-half">
    <div class="box"><strong>Tracks run...</strong>
        <table class="table is-fullwidth">
          <tr>
            <th title="Active Track"></th>
            <th>Name</th>
            <th title="Runs">R</th>
            <th title="Abandons">A</th>
            <th title="Completes">C</th>
            <th>Exp</th>
            <th title="Exp per minute">Expm</th>
            <th title="Kills">K</th>
            <th title="Duration in minutes">D</th>
          </tr>
          <tr :key="track.name" v-for="track in this.sorted_tracks">
            <td v-if="track.name == report.track">*</td>
            <td v-else></td>
            <td>{{track.name}}</td>
            <td>{{track.runs}}</td>
            <td>{{track.abandons}}</td>
            <td>{{track.completes}}</td>
            <td>{{track.exp}}</td>
            <td>{{ processExpm(track) }}/min</td>
            <td>{{track.kills}}</td>
            <td>{{ Math.floor(track.duration/60*100)/100 }}</td>
          </tr>
        </table>
    </div>
    <div class="box"><strong>Physical damage...</strong>
      <apexchart width="500" type="bar" :options="attackOptions" :series="attackSeries"></apexchart>
    </div>
    <div class="box"><strong>Spell damage...</strong>
      <apexchart width="500" type="bar" :options="castOptions" :series="castSeries"></apexchart>
    </div>
    <div class="box"><strong>Inventory...</strong>
        <table class="table is-fullwidth">
          <tr>
            <th>Name</th>
            <th>Quantity</th>
          </tr>
          <tr :key="item" v-for="quantity,item in report.inventory">
            <td>{{item}}</td>
            <td>{{quantity}}</td>
          </tr>
        </table>
    </div>
  </div>
  <div class="column">
    <div class="box"><strong>Equipment...</strong>
        <div class="stat">Wielded: [{{report.weapon1}}]</div>
        <div class="stat" v-if="report.weapon2 != ''">Wielded: {{report.weapon2}}</div>
        <div :key="index" v-for="(item,slot,index) in equipment">
          <div class="stat">{{slot}}: [{{item}}]</div>
        </div>
    </div>
    <div class="box"><strong>Mobs killed...</strong>
      <div :key="mob" v-for="count, mob in mobs_killed">{{count}} {{mob}}</div>
    </div>
    <div class="box"><strong>Mobs targetted...</strong>
      <div :key="mob" v-for="mob in sorted_mkl">{{mob}}</div>
    </div>
  </div>
</div>
</template>

<script>

import axios from 'axios'
export default {
  name: 'App',
  data:  function() {
return {
    mkl: [],
    info: {},
    report: {},
    track_report: [],
    equipment: {"body": "", "arms": "", "legs": "", "neck": "", "neck2": "", "hands": "", "head": "", "feet": "", "face": "", "finger": "", "finger2": "", "finger3": "", "finger4": "", "finger5": "", "finger6": "", "finger7": "", "finger8": "", "shield": "", "wielded": null, "seconded": null, "holding": null},
    pollInterval: '',
    status: '',
    darkMode: true,
    statOptions: {
      chart: {
        id: 'stat-chart'
      },
      xaxis: {
        categories: ['STR', 'DEX', 'CON', 'INT', 'PTY']
      }
    },
    attackOptionsTemp: {
      chart: {
        id: 'attack-chart'
      },
      yaxis: {
        categories: ['0', '10'],
      },
      xaxis: {
        tickAmount: 20
      }
    },
    series: [{
      name: 'series-1',
      data: [18, 18, 3, 18, 3]
    }]
  }
},
  created() {
    this.fetchData();
    this.pollInterval = setInterval(this.fetchData, 30000);
  },
  beforeUnmount() {
    clearInterval(this.pollInterval)
  },
  methods: {
    fetchData: function() {
      console.log("here I go fetching data again...");
      axios.get('api/mkl.json?t=' + new Date().getTime())
      .then((response) => {
        this.mkl = response.data;
      });
      axios.get('../api/info.json?t=' + new Date().getTime())
      .then((response) => {
        this.info = response.data;
      });
      axios.get('../api/report.json?t=' + new Date().getTime())
      .then((response) => {
        this.report = response.data;
      });
      axios.get('../api/track_report.json?t=' + new Date().getTime())
      .then((response) => {
        this.track_report = response.data;
      });
      axios.get('../api/equipment.json?t=' + new Date().getTime())
      .then((response) => {
        this.equipment = response.data;
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
  watch: {
    // report(newReport, oldReport) {
    //   console.log(newReport, oldReport)
    // }
  },
  computed: {
    adjustedTimestamp: function() {
      let output = ''
      //"timestamp": "19:11:57.36"
      if (this.report.timestamp) {
        // subtract six hours from the timestamp
        output = new Date()
        let time = this.report.timestamp.split(':')
        output.setHours(time[0] - 6)
        output.setMinutes(time[1])
        output.setSeconds(time[2])
        output = output.toLocaleString()
      }
      return output
    },
    attackOptions: function () {
      let output = this.attackOptionsTemp
      if (this.report !== {} && this.report.attacks) {
        let keys = Object.keys(this.report.attacks['p'])
        output = {
          chart: {
            id: 'attack-chart'
          },
          xaxis: {
            categories: keys
          }
        }
      }
      return output
    },
    attackSeries: function() {
      let output = [{
          name: 'hits',
          data: [0]
        }]
      let physHits = []
      // let castHits = []
      if (this.report && this.report.attacks) {
        for (var i = 0; i < Object.keys(this.report.attacks['p']).length; i++) {
          let curKey = Object.keys(this.report.attacks['p'])[i]
          let attack = this.report.attacks['p'][curKey]
          physHits.push(attack)
        }

        output = [{
          name: 'hits',
          data: physHits
        }]
      }
      return output
    },
    castOptions: function () {
      let output = this.attackOptionsTemp
      if (this.report !== {} && this.report.attacks) {
        let keys = Object.keys(this.report.attacks['s'])
        output = {
          chart: {
            id: 'attack-chart'
          },
          xaxis: {
            categories: keys
          }
        }
      }
      return output
    },
    castSeries: function() {
      let output = [{
          name: 'cast',
          data: [0]
        }]
      let physHits = []
      // let castHits = []
      if (this.report && this.report.attacks) {
        for (var i = 0; i < Object.keys(this.report.attacks['s']).length; i++) {
          let curKey = Object.keys(this.report.attacks['s'])[i]
          let attack = this.report.attacks['s'][curKey]
          physHits.push(attack)
        }

        output = [{
          name: 'hits',
          data: physHits
        }]
      }
      return output
    },
    statSeries: function() {
      let output = this.series
      if (this.info !== {} && this.info.stats && this.info.stats[0]) {
          output = [{
          name: 'series-1',
          data: [
            this.info.stats[0].value,
            this.info.stats[1].value,
            this.info.stats[2].value,
            this.info.stats[3].value,
            this.info.stats[4].value
          ]
        }]
      }
      return output
    },
    bodyClass: function() {
      return {'dark_mode': this.darkMode}
    },
    sorted_tracks: function() {
      function compare(a,b) {
        if (a.last_run < b.last_run) {
          return 1;
        } else if (a.last_run > b.last_run) {
          return -1;
        } else {
          return 0;
        }
      }

      let track_copy = JSON.parse(JSON.stringify(this.track_report))
      return track_copy.sort(compare);
    },
    sorted_mkl: function() {
      let mkl_copy = JSON.parse(JSON.stringify(this.mkl))
      return mkl_copy.sort();
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
    crit_to_hit: function() {
      let output = 0
      if (this.report !== {} & this.report.total_phys_hits > 0) {
        output = Math.round((this.report.phys_crits / this.report.total_phys_hits)*10000)/100
      }
      return output
    },
    crit_to_attack: function() {
      let output = 0
      if (this.report !== {} & this.report.total_phys_attacks > 0) {
        output = Math.round((this.report.phys_crits / this.report.total_phys_attacks)*10000)/100
      }
      return output
    },
    crit_to_cast: function() {
      let output = 0
      if (this.report !== {} & this.report.spells_cast > 0) {
        output = Math.round((this.report.spell_crits / this.report.spells_cast)*10000)/100
      }
      return output
    },
    crit_to_cast_hit: function() {
      let output = 0
      if (this.report !== {} & this.report.spells_hit > 0) {
        output = Math.round((this.report.spell_crits / this.report.spells_hit)*10000)/100
      }
      return output
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
        case 'Bar':
          return 'Barbarian';
        case 'Cle':
          return 'Cleric';
        case 'Fig':
          return 'Fighter';
        case 'Brd':
          return 'Bard';
        case 'Mon':
          return 'Monk';
        case 'Mag':
          return 'Mage';
        case 'Pal':
          return 'Paladin';
        case 'Ran':
          return 'Ranger';
        case 'Thi':
          return 'Thief';
        case 'Dru':
          return 'Druid';
        case 'Alc':
          return 'Alchemist';
        case 'Dar':
          return 'Anti-Paladin';
        default:
          return 'Meow';
      }
    }
  }
  // components: {
  //   VueApexCharts
  // }
}
</script>

<style>

</style>
