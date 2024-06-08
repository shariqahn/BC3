<script>
import axios from 'axios';
import mapboxgl from "mapbox-gl";
import "../../node_modules/mapbox-gl/dist/mapbox-gl.css"
import { MapboxSearchBox } from "@mapbox/search-js-web"

export default {
  data() {
      return {
          temperatures: [],
          latitudes: [],
          longitudes: [],
          data: {},
          accessToken: 'pk.eyJ1Ijoic2hhcmlxYWgiLCJhIjoiY2x0MmQ3OHMzMWt5dTJxbnc0cmk3dHE5cyJ9.HQ80jJpT5LRbIHjQLFgt3Q',
          // todo improve colors
          colorScale: 
          // IPCC
          ['rgb(254, 254, 203)', 'rgb(252, 240, 165)', 'rgb(248, 222, 127)', 'rgb(241, 195, 95)', 'rgb(235, 167, 84)', 'rgb(230, 142, 81)', 'rgb(222, 116, 79)', 'rgb(200, 89 ,74)', 'rgb(164, 70 ,66)', 'rgb(126, 59 ,52)', 'rgb(89 ,47, 35)', 'rgb(55 ,36, 19)', 'rgb(25 ,25, 0)'],
          // even colorful
          // ['white', '#fff4b0', '#fbd584', '#fab35f', '#fa8d45', '#f8613a', '#f3183c', '#dd0050', '#c2005e', '#a20067', '#801569', '#5e1d65', '#3c1f5b'],
          // even mono
          // ['white', '#fff0ff', '#ffe0ff', '#e6c4eb', '#cda8d8', '#b38dc6', '#a17cba', '#8f6baf', '#7c5ba3', '#694b98', '#553c8d', '#3f2e83', '#252178'],
          // unbalanced colorful
            // ['white', '#fff4b0', '#f9d08c', '#f2ab72', '#e88563', '#d85e5e', '#c23560', '#a20067', '#8e0f69', '#791769', '#641c66', '#501f62', '#3c1f5b'],
          // unbalanced mono
          // ['white', '#fff0ff', '#e4cce8', '#c8a9d2', '#aa88be', '#8b69aa', '#694b98', '#5f4493', '#553c8d', '#4a3588', '#3f2e82', '#33277d', '#252178'],
          logBase: 2,
          loaded: false
          // ,
          // map
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
            "properties": {
              'temperature': temperature,
              'center': [longitude, latitude]
            }
          }
          this.data.features.push(feature)
        })
      })
    },
    initMap() {
      mapboxgl.accessToken = this.accessToken;
      let longitude = this.$route.query.lon
      let latitude = this.$route.query.lat
      let zoom = this.$route.query.zoom

      longitude = longitude ? longitude : 0
      latitude = latitude ? latitude : 0
      zoom = zoom ? zoom : 2
      // todo add error handling to ensure in range
      console.log(this.$route.query, longitude, latitude)
 
      const map = new mapboxgl.Map({
      container: 'map', 
      // todo fix search to work on equal projection
      projection: 'globe',
      // style: 'mapbox://styles/mapbox/streets-v8', 
      style: 'mapbox://styles/mapbox/streets-v12', 
      zoom: zoom,
      maxZoom: 7,
      center: [longitude, latitude]
      });

      map.on('load', () => {
        // const layers = map.getStyle().layers;
        // // console.log(layers)
        // for (const layer of layers) {
        //     // console.log(layer)
        //     if ((layer.type === 'line')) {
        //         console.log(layer)
        //     } 
        // }

        // remove globe halo
        map.setFog({
            // "color": "#245cdf",
            "horizon-blend": 0,
            // "space-color": "red",
            // "high-color": "yellow",
          });
          
        map.addSource('temperature', {
          type: 'geojson',
          data: this.data,
        });

        map.addLayer(
          {
              'id': 'temperature-map',
              'source': 'temperature',
              'type': 'fill',
              'paint': {
                  'fill-color': [
                      'interpolate',
                      ['linear'],
                      ['get', 'temperature'],
                      0,
                      this.colorScale[0],
                      .5,
                      this.colorScale[1],
                      1,
                      this.colorScale[2],
                      1.5,
                      this.colorScale[3],
                      2,
                      this.colorScale[4],
                      2.5,
                      this.colorScale[5],
                      3,
                      this.colorScale[6],
                      3.5,
                      this.colorScale[7],
                      4,
                      this.colorScale[8],
                      4.5,
                      this.colorScale[9],
                      5,
                      this.colorScale[10],
                      5.5,
                      this.colorScale[11],
                      6,
                      this.colorScale[12],
                  ],
              }
          },
          // todo play w layers more
          "admin-1-boundary-bg",
          // "admin-2-boundaries-bg"
        );

        const popup = new mapboxgl.Popup();
        map.on('click', 'temperature-map', (e) => {
            const temperature = e.features[0].properties.temperature.toFixed(1)
            popup.setLngLat(e.lngLat).setHTML('+' + temperature + ' &degC').addTo(map);
        });

        const search = new MapboxSearchBox();
        search.accessToken = this.accessToken;
        search.bindMap(map);
        map.addControl(search);
        map.addControl(new mapboxgl.NavigationControl());

        // const camera = map.getCamera();
        // console.log(camera);
        // this.loaded = true;
      });

      map.on('moveend', () => {
        let win = window.parent;
        win.postMessage('hi parent');
        win = window.opener;
        win.postMessage('hi open');
        win = window;
        win.postMessage('hi window');
        // window.postMessage({
        //   "center": map.getCenter(),
        //   "zoom": map.getZoom()
        // });
      });
    },
    updateMap() {
      let longitude = this.$route.query.lon
      let latitude = this.$route.query.lat
      let zoom = this.$route.query.zoom

      longitude = longitude ? longitude : 0
      latitude = latitude ? latitude : 0
      zoom = zoom ? zoom : 1
      console.log('updating')
 
      
    },
    getTemperatures() {
      const query = this.$route.query.tbar
      // todo handle error better here
      const tbar = query ? query : 0
      let url = window.location.origin
      // const path = url + '/api/?tbar=' + tbar;
      url = url.slice(0, url.lastIndexOf(":"))
      const path = url + ':5002/temperature?tbar=' + tbar;
      axios.get(path)
        .then((res) => {
          // todo structure data
          this.temperatures = res.data.temps;
          this.latitudes = res.data.lats;
          this.longitudes = res.data.lons;
          // window.addEventListener("message", (event) => {
          //     console.log('messaged!')
          //     if (event.origin !== "http://localhost:5173") return;
              
          //     console.log('received!')
          //     console.log(event);
          // });
          this.getGeoJSON();
          this.initMap();
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
  created() {
    this.getTemperatures();
    this.$watch(
      () => this.$route.query,
      (toParams, previousParams) => {
        // todo react to route changes
        this.updateMap();
      }
    )
  }
}

</script>

<template>
  <div id="map"></div>
  <!-- todo move to new component -->
  <div class='my-legend'>
  <div class='legend-title'>Temperature Increase (&degC)</div>
  <div class='legend-scale'>
    <ul class='legend-labels'>
      <li><span :style="{background: colorScale[0]}"></span>0</li>
      <li v-for="n in colorScale.length-2">
        <span :style="{background: colorScale[n]}"></span>{{.5*n}}
      </li>
      <li><span :style="{background: colorScale[colorScale.length-1]}"></span>{{.5*(colorScale.length-1)}}+</li>
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
  color: black;
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
  /* -webkit-text-stroke-color: white; */

  }
.my-legend .legend-scale ul li {
  display: block;
  float: left;
  width: 30px;
  margin-bottom: 6px;
  text-align: center;
  font-size: 80%;
  list-style: none;
  /* -webkit-text-stroke-color: white;
  -webkit-text-stroke-width: .2px; */

  }
.my-legend ul.legend-labels li span {
  display: block;
  float: left;
  height: 15px;
  width: 30px;
  /* -webkit-text-stroke-color: white;
  -webkit-text-stroke-width: 3px; */

  }
/* .my-legend .legend-source {
  font-size: 70%;
  color: #999;
  clear: both;
  } */
.my-legend a {
  color: #777;
  }

.my-legend {
  z-index: 1;
  bottom: 35px;
  right: 15px;
  position: absolute;
  background-color: white;
  color: #333333;
  padding-right: 7px;
  padding-left: 7px;
  border-color:rgba(0, 0, 0, .1);
  border-style: solid;
  border-radius: 5px;
  border-width: 1px;
}

/* @media (prefers-color-scheme: dark) {
  .my-legend {
    background-color: #181818;
  }
} */

</style>
