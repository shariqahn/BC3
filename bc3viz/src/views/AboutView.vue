<!-- <script setup> -->
<script>
// import { RouterLink, RouterView } from 'vue-router'
// import HelloWorld from './components/HelloWorld.vue'
import axios from 'axios';
import { Loader } from "@googlemaps/js-api-loader"
import chroma from "chroma-js"
import { toHandlers } from 'vue';
import grid from '../assets/grid.json';
import mapboxgl from "mapbox-gl";
import "../../node_modules/mapbox-gl/dist/mapbox-gl.css"

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
  methods: {
    initMap() {
      mapboxgl.accessToken = 'pk.eyJ1Ijoic2hhcmlxYWgiLCJhIjoiY2x0MmQ3OHMzMWt5dTJxbnc0cmk3dHE5cyJ9.HQ80jJpT5LRbIHjQLFgt3Q';
 
      const map = new mapboxgl.Map({
      container: 'map', // HTML container id
      projection: 'mercator',
      style: 'mapbox://styles/mapbox/streets-v12', // style URL
      center: [-21.92661562, 64.14356426], // starting position as [lng, lat]
      zoom: 1
      });

      const minTemperature = Number(this.temperatures['minTemperature'])
      const maxTemperature = Number(this.temperatures['maxTemperature'])
      console.log(minTemperature, maxTemperature)

      map.on('load', () => {
        map.addSource('temperature', {
          type: 'geojson',
          data: grid
        });
        // add heatmap layer here
        map.addLayer(
        {
          id: 'trees-heat',
          type: 'heatmap',
          source: 'temperature',
          maxzoom: 15,
          paint: {
            'heatmap-weight': {
              property: 'temperature',
              type: 'exponential',
              stops: [
                [minTemperature, 0],
                [maxTemperature, 1]
              ]
            },
            // increase intensity as zoom level increases
            'heatmap-intensity': {
              stops: [
                [11, 1],
                [15, 3]
              ]
            },
            // assign color values be applied to points depending on their density
            'heatmap-color': [
              'interpolate',
              ['linear'],
              ['heatmap-density'],
              0,
              'rgba(236,222,239,0)',
              0.2,
              'rgb(208,209,230)',
              0.4,
              'rgb(166,189,219)',
              0.6,
              'rgb(103,169,207)',
              0.8,
              'rgb(28,144,153)'
            ],
            // increase radius as zoom increases
            'heatmap-radius': {
              stops: [
                [11, 15],
                [15, 20]
              ]
            },
            // // decrease opacity to transition into the circle layer
            // 'heatmap-opacity': {
            //   default: 1,
            //   stops: [
            //     [14, 1],
            //     [15, 0]
            //   ]
            // }
          }
        },
        'waterway-label'
      );
        // add circle layer here
      });
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
