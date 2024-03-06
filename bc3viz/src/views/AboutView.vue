<!-- <script setup> -->
<script>
// import { RouterLink, RouterView } from 'vue-router'
// import HelloWorld from './components/HelloWorld.vue'
import axios from 'axios';
import chroma from "chroma-js"
import { setBlockTracking, toHandlers } from 'vue';
import grid from '../assets/shortgrid.json';
import mapboxgl from "mapbox-gl";
import "../../node_modules/mapbox-gl/dist/mapbox-gl.css"

export default {
  components: {
      // Logo
  },
  data() {
      return {
          temperatures: [],
          latitudes: [],
          longitudes: [],
          minTemperature: null,
          maxTemperature: null,
          // Map: undefined,
          loaded: false,
          // grid: grid,
          data: {}
      }
  },
  methods: {
    getGeoJSON(){
      this.data = {
        "type":"FeatureCollection",
        "features":[]
      }

      this.temperatures.forEach((lats, i) => {
        lats.forEach((temperature, j) => {
          const latitude = this.latitudes[i]
          const longitude = this.longitudes[j]

          const polygon = [[[longitude-.5, latitude-.5], [longitude-.5, latitude+.5], [longitude+.5, latitude+.5], [longitude+.5, latitude-.5], [longitude-.5, latitude-.5]]]
          const feature = {
            "type": "Feature",
            "geometry": {
              "type": "Polygon",
              "coordinates": polygon
            },
            "properties": {'temperature': temperature}
          }
          this.data.features.push(feature)
        })
      })
      // this.data.features = this.data.features.slice(20000,24000)
    },
    initMap() {
      console.log('data',this.data)
      mapboxgl.accessToken = 'pk.eyJ1Ijoic2hhcmlxYWgiLCJhIjoiY2x0MmQ3OHMzMWt5dTJxbnc0cmk3dHE5cyJ9.HQ80jJpT5LRbIHjQLFgt3Q';
 
      const map = new mapboxgl.Map({
      container: 'map', // HTML container id
      projection: 'mercator',
      style: 'mapbox://styles/mapbox/streets-v12', // style URL
      // center: [-21.92661562, 64.14356426], // starting position as [lng, lat]
      // center: [300, -30], // starting position
      zoom: 4
      });

      // const minTemperature = Number(this.temperatures['minTemperature'])
      // const maxTemperature = Number(this.temperatures['maxTemperature'])
      console.log(this.minTemperature, this.maxTemperature)
      // var minTemperature, maxTemperature;
      // this.temperatures.temps.forEach(function(itm) {
      //   const min = Math.min(...itm)
      //   const max = Math.max(...itm)
      //   minTemperature = (minTemperature == undefined || min<minTemperature) ? min : minTemperature;
      //   maxTemperature = (maxTemperature == undefined || max>maxTemperature) ? max : maxTemperature;
      // });

      map.on('load', () => {
        // const layers = map.getStyle().layers;
        // for (const layer of layers) {
        //     if (layer.type === 'line') {
        //         console.log(layer)
        //     }
        // }

        map.addSource('temperature', {
          type: 'geojson',
          data: this.data,
        });

        map.addLayer(
            {
                'id': 'temperature-map',
                'source': 'temperature',
                // 'source-layer': 'state_county_population_2014_cen',
                // 'maxzoom': zoomThreshold,
                'type': 'fill',
                // only include features for which the "isState"
                // property is "true"
                // 'filter': ['==', 'isState', true],
                'paint': {
                    'fill-color': [
                        'interpolate',
                        ['linear'],
                        ['get', 'temperature'],
                        0,
                        'white',
                        5,
                        'yellow',
                        10,
                        'orange',
                        15,
                        'red'
                    ],
                    // 'fill-opacity': 0.75,
                }
            },
            // todo play w layers more
        "admin-1-boundary",
        // 'pitch-outline'
        // "admin-0-boundary-bg"
        );
      });
    },
    getTemperatures() {
      const tbar = this.$route.query.tbar
      console.log(tbar)
      const path = 'http://localhost:5000/temperature?tbar=' + tbar;
      axios.get(path)
        .then((res) => {
          // console.log(res)
          // todo structure data
          this.temperatures = res.data.temps;
          this.latitudes = res.data.lats;
          this.longitudes = res.data.lons;
          // todo calc in js
          this.minTemperature = Number(res.data.minTemperature)
          this.maxTemperature =  Number(res.data.maxTemperature)
          // (!this.loaded) ? this.initMap() : this.refreshMap()
         
          this.getGeoJSON();
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
  <div id="map"></div>
  <div class='my-legend'>
  <div class='legend-title'>Temperature Anomaly (K)</div>
  <div class='legend-scale'>
    <ul class='legend-labels'>
      <li><span style='background:white;'></span>0</li>
      <li><span style='background:yellow;'></span>5</li>
      <li><span style='background:orange;'></span>10</li>
      <li><span style='background:red;'></span>15</li>
    </ul>
  </div>
  </div>
</template>

<style scoped>

#map {
  /* todo miminze styling */
  position:absolute;

  top:0;
  left:0;

  width: 100%;
  height: 100%;

  z-index: 1;
}

.my-legend .legend-title {
  text-align: left;
  margin-bottom: 8px;
  font-weight: bold;
  font-size: 90%;
  }
.my-legend .legend-scale ul {
  margin: 0;
  padding: 0;
  float: left;
  list-style: none;
  }
.my-legend .legend-scale ul li {
  display: block;
  float: left;
  width: 50px;
  margin-bottom: 6px;
  text-align: center;
  font-size: 80%;
  list-style: none;
  }
.my-legend ul.legend-labels li span {
  display: block;
  float: left;
  height: 15px;
  width: 50px;
  }
.my-legend .legend-source {
  font-size: 70%;
  color: #999;
  clear: both;
  }
.my-legend a {
  color: #777;
  }

.my-legend {
  z-index: 1;
  bottom: 30px;
  right: 20px;
  position: absolute;
  background-color: white;
  padding-right: 5px;
  padding-left: 5px;
}

</style>
