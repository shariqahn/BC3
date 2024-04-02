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
          loaded: false,
          data: {},
          accessToken: 'pk.eyJ1Ijoic2hhcmlxYWgiLCJhIjoiY2x0MmQ3OHMzMWt5dTJxbnc0cmk3dHE5cyJ9.HQ80jJpT5LRbIHjQLFgt3Q',
          colorScale: ['white', '#ffe95c', '#ff9b4b', '#f34f66', '#ad1f84', '#2b278d'],
          logBase: 2
      }
  },
  methods: {
    getGeoJSON(){
      this.data = {
        "type":"FeatureCollection",
        "features":[]
      }

      var count = 0
      var maxCount = 0
      this.temperatures.forEach((lats, i) => {
        lats.forEach((temperature, j) => {
          if (temperature >= 10) {
            maxCount = maxCount + 1;
          }
          count = count + 1;
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

      console.log(maxCount/count);
    },
    initMap() {
      mapboxgl.accessToken = this.accessToken;
 
      const map = new mapboxgl.Map({
      container: 'map', 
      projection: 'mercator',
      style: 'mapbox://styles/mapbox/streets-v12', 
      zoom: 4,
      maxZoom: 7
      });

      map.on('load', () => {
        // const layers = map.getStyle().layers;
        // for (const layer of layers) {
        //     if ((layer.type === 'line') || (layer.type === 'symbol')) {
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
              'type': 'fill',
              'paint': {
                  'fill-color': [
                      'interpolate',
                      ['linear'],
                      ['get', 'temperature'],
                      // 0,
                      // this.colorScale[0],
                      // this.logBase,
                      // this.colorScale[1],
                      // this.logBase**2,
                      // this.colorScale[2],
                      // this.logBase**3,
                      // this.colorScale[3],
                      // this.logBase**4,
                      // this.colorScale[4],
                      // this.logBase**5,
                      // this.colorScale[5]
                      0,
                      this.colorScale[0],
                      2,
                      this.colorScale[1],
                      4,
                      this.colorScale[2],
                      6,
                      this.colorScale[3],
                      8,
                      this.colorScale[4],
                      10,
                      this.colorScale[5]
                  ],
              }
          },
          // todo play w layers more
          "admin-1-boundary-bg",
        );

        const search = new MapboxSearchBox();
        search.accessToken = this.accessToken;
        map.addControl(search);
      });
    },
    getTemperatures() {
      const query = this.$route.query.tbar
      // todo handle error better here
      const tbar = query ? query : 0
      let url = window.location.origin
      url = url.slice(0, url.lastIndexOf(":"))
      // const path = 'http://localhost:5000/temperature?tbar=' + tbar;
      const path = url + ':5000/temperature?tbar=' + tbar;
      axios.get(path)
        .then((res) => {
          // console.log(res)
          // todo structure data
          this.temperatures = res.data.temps;
          this.latitudes = res.data.lats;
          this.longitudes = res.data.lons;
          console.log(res.data.maxTemperature)
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
        this.getTemperatures();
      }
    )
  }
}

</script>

<template>
  <div id="map"></div>
  <!-- todo move to new component -->
  <div class='my-legend'>
  <div class='legend-title'>Temperature Increase (C)</div>
  <div class='legend-scale'>
    <ul class='legend-labels'>
      <li><span :style="{background: colorScale[0]}"></span>0</li>
      <li v-for="n in colorScale.length-2">
        <span :style="{background: colorScale[n]}"></span>{{2*n}}
      </li>
      <li><span :style="{background: colorScale[colorScale.length-1]}"></span>{{2*(colorScale.length-1)}}+</li>
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
  bottom: 35px;
  right: 15px;
  position: absolute;
  background-color: white;
  padding-right: 7px;
  padding-left: 7px;
  border-color: grey;
  border-style: solid;
  border-radius: 5px;
  border-width: 1px;
}

</style>
