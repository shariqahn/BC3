<!-- <script setup> -->
<script>
// import { RouterLink, RouterView } from 'vue-router'
// import HelloWorld from './components/HelloWorld.vue'
import axios from 'axios';
import { Loader } from "@googlemaps/js-api-loader"
import chroma from "chroma-js"
import { toHandlers } from 'vue';
import grid from '../assets/grid.json';
// import {Legend, Swatches} from "@d3/color-legend"
// (g=>{var h,a,k,p="The Google Maps JavaScript API",c="google",l="importLibrary",q="__ib__",m=document,b=window;b=b[c]||(b[c]={});var d=b.maps||(b.maps={}),r=new Set,e=new URLSearchParams,u=()=>h||(h=new Promise(async(f,n)=>{await (a=m.createElement("script"));e.set("libraries",[...r]+"");for(k in g)e.set(k.replace(/[A-Z]/g,t=>"_"+t[0].toLowerCase()),g[k]);e.set("callback",c+".maps."+q);a.src=`https://maps.${c}apis.com/maps/api/js?`+e;d[q]=f;a.onerror=()=>h=n(Error(p+" could not load."));a.nonce=m.querySelector("script[nonce]")?.nonce||"";m.head.append(a)}));d[l]?console.warn(p+" only loads once. Ignoring:",g):d[l]=(f,...n)=>r.add(f)&&u().then(()=>d[l](f,...n))})
//         ({key: "AIzaSyB41DRUbKWJHPxaFjMAwdrzWzbVKartNGg", v: "weekly"});

export default {
  components: {
      // Logo
  },
  data() {
      return {
          // greeting: 'Hello, Vue!',
          temperatures: '',
          // flaskGreeting: '',
          // Map: undefined,
          // AdvancedMarkerElement: undefined
          loaded: false,
          squares: [],
          grid: grid
      }
  },
  // mounted() {
  //   console.log(`the component is now mounted.`)
  //   console.log(grid)
  // },
  methods: {
    initMap() {
      // todo improve import
      const loader = new Loader({
        apiKey: "AIzaSyB41DRUbKWJHPxaFjMAwdrzWzbVKartNGg",
        version: "weekly",
        // ...additionalOptions,
      });

      loader.load().then(async () => {
        const start = Date.now();
        const { Map } = await google.maps.importLibrary("maps");
        const { HeatmapLayer } = await google.maps.importLibrary("visualization");

        
        var sanFrancisco = new google.maps.LatLng(37.774546, -122.433523);

        map = new Map(document.getElementById("map"), {
          zoom: 2,
          center: sanFrancisco,
        });

        map.data.addGeoJson(this.grid);
        map.data.setStyle({
          fillColor: 'green',
          strokeWeight: 1
        });



        // var heatMapData = []
        // var data = []
        // const colors = chroma.scale(['yellow', 'red', 'black']);
        // var minTemperature,maxTemperature;
        // this.temperatures.temps.forEach(function(itm) {
        //   const min = Math.min(...itm)
        //   const max = Math.max(...itm)
        //   minTemperature = (minTemperature == undefined || min<minTemperature) ? min : minTemperature;
        //   maxTemperature = (maxTemperature == undefined || max>maxTemperature) ? max : maxTemperature;
        // });
        // colors.domain([minTemperature, maxTemperature])
        // // const squares = []
        // this.temperatures.temps.forEach((lats, i) => {
        //   lats.forEach((lon, j) => {
        //     const latitude = this.temperatures.lats[i]
        //     const longitude = this.temperatures.lons[j]
        //     const color = colors(this.temperatures.temps[i][j]).css()
        //     const square = new google.maps.Rectangle({
        //       strokeColor: color,
        //       strokeOpacity: 0,
        //       strokeWeight: 2,
        //       fillColor: color,
        //       fillOpacity: 0.6,
        //       map,
        //       bounds: {
        //         north: latitude + .5,
        //         south: latitude - .5,
        //         east: longitude + .5,
        //         west: longitude - .5,
        //       },
        //     });
        //     this.squares.push(square)
        //     // map.data.add(square)

        //     // const outerCoords = [
        //     //   { lat: latitude + .5, lng: longitude + .5 },
        //     //   { lat: latitude + .5, lng: longitude - .5 },
        //     //   { lat: latitude - .5, lng: longitude - .5 },
        //     //   { lat: latitude - .5, lng: longitude + .5 }, // north east
        //     // ];

        //     // const x = map.data.add({
        //     //   geometry: new google.maps.Data.Polygon([
        //     //     outerCoords
        //     //   ]),
        //     //   fillColor: color
        //     // });
        //     // console.log(x)
        //     // count += 1;
        //   })
        // })
        this.loaded = true
        // map.data.add({
        //   geometry: new google.maps.Data.Polygon(squares),
        // });

      });
    },
    refreshMap() {
        // const colors = chroma.scale(['yellow', 'red', 'black']);
        // var minTemperature,maxTemperature;
        // this.temperatures.temps.forEach(function(itm) {
        //   const min = Math.min(...itm)
        //   const max = Math.max(...itm)
        //   minTemperature = (minTemperature == undefined || min<minTemperature) ? min : minTemperature;
        //   maxTemperature = (maxTemperature == undefined || max>maxTemperature) ? max : maxTemperature;
        // });
        // colors.domain([minTemperature, maxTemperature])
        // // const squares = []
        // this.temperatures.temps.forEach((lats, i) => {
        //   lats.forEach((lon, j) => {
        //     const latitude = this.temperatures.lats[i]
        //     const longitude = this.temperatures.lons[j]
        //     const color = colors(this.temperatures.temps[i][j]).css()
        //     const square = new google.maps.Rectangle({
        //       strokeColor: color,
        //       strokeOpacity: 0,
        //       strokeWeight: 2,
        //       fillColor: color,
        //       fillOpacity: 0.6,
        //       map,
        //       bounds: {
        //         north: latitude + .5,
        //         south: latitude - .5,
        //         east: longitude + .5,
        //         west: longitude - .5,
        //       },
        //     });
        //     this.squares.push(square)
        //   })
        // })
    },
    getTemperatures() {
      const tbar = this.$route.query.tbar
      const path = 'http://localhost:5000/temperature?tbar=' + tbar;
      // console.log(path)
      axios.get(path)
        .then((res) => {
          // console.log(res)
          this.temperatures = res.data;
          // console.log(!this.loaded);
          // (!this.loaded) ? this.initMap() : this.refreshMap()
         

          this.initMap();
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
  created() {
    // Map = await google.maps.importLibrary("maps");
    // AdvancedMarkerElement = await google.maps.importLibrary("marker");
    // this.getGreeting(); 
    this.getTemperatures();
    this.$watch(
      () => this.$route.query,
      (toParams, previousParams) => {
        // react to route changes...
        this.getTemperatures();
      }
    )
  }
}

</script>

<template>
  <!-- <header>
    <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="125" height="125" />

    <div class="wrapper">
      <HelloWorld msg="You did it!" />

      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
      </nav>
    </div>
  </header> -->
  <!-- <div id="app">
    <p>{{ greeting }}</p>
    <p>{{ flaskGreeting }}</p>
  </div> -->
  <!--The div element for the map -->
  <div id="map"></div>
  <!-- <div id="legend"><h3>Legend</h3></div> -->
  <!-- <RouterView /> -->
</template>

<style scoped>

#map {
  /* todo miminze styling */
  position:absolute;

  top:0;
  left:0;

  width: 100%;
  height: 100%;
}

#legend {
  font-family: Arial, sans-serif;
  background: #fff;
  padding: 10px;
  margin: 10px;
  border: 3px solid #000;
}

#legend h3 {
  margin-top: 0;
}

</style>
