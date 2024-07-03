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
          colorScale: 
          // IPCC
          ['rgb(254, 254, 203)', 'rgb(252, 240, 165)', 'rgb(248, 222, 127)', 'rgb(241, 195, 95)', 'rgb(235, 167, 84)', 'rgb(230, 142, 81)', 'rgb(222, 116, 79)', 'rgb(200, 89 ,74)', 'rgb(164, 70 ,66)', 'rgb(126, 59 ,52)', 'rgb(89 ,47, 35)', 'rgb(55 ,36, 19)', 'rgb(25 ,25, 0)'],
          logBase: 2,
          tbar: 0,
          map: undefined,
          projection: 'globe'
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
      console.log('init');
      mapboxgl.accessToken = this.accessToken;
      let longitude = this.$route.query.lon
      let latitude = this.$route.query.lat
      let zoom = this.$route.query.zoom
      const projection = this.$route.query.projection

      longitude = longitude ? longitude : 0
      latitude = latitude ? latitude : 0
      zoom = zoom ? zoom : 2
      if (projection) {
        this.projection = projection
      }
      console.log('projection: ', this.projection)
      // todo add error handling to ensure in range

      // const 
      this.map = new mapboxgl.Map({
        container: 'map', 
        projection: this.projection,
        // style: 'mapbox://styles/mapbox/streets-v8', 
        style: 'mapbox://styles/mapbox/streets-v12', 
        zoom: zoom,
        maxZoom: 7,
        center: [longitude, latitude]
      });

      this.map.on('load', () => {
        // const layers = this.map.getStyle().layers;
        // // console.log(layers)
        // for (const layer of layers) {
        //     console.log(layer)
        //     // if ((layer.type === 'line')) {
        //     //     console.log(layer)
        //     // } 
        // }

        // // Remove globe halo to allow for contrast between black background and color scale
        // this.map.setFog({
        //     "horizon-blend": 0,
        //   });
          
        this.map.addSource('temperature', {
          type: 'geojson',
          data: this.data,
        });

        // this.map.addLayer({
        //   "id": "waterway-green",
        //   "source": "mapbox-streets",
        //   "source-layer": "waterway",
        //   "type": "line",
        //   "paint": {
        //     "fill-color": "green"
        //   }
        // })

        this.map.addLayer(
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
          // didn't work:
          // anything 'fill' type
          // 'land-structure-line'
          // 'waterway'
          // 'waterway-shadow'
          // 'pitch-outline' HERE
          // 'aeroway-line'
          // 'landuse'
        );

        // const search = new MapboxSearchBox();
        // search.accessToken = this.accessToken;
        // search.bindMap(this.map);
        // this.map.addControl(search);
        // this.map.addControl(new mapboxgl.NavigationControl());

        const popup = new mapboxgl.Popup();
        this.map.on('click', 'temperature-map', (e) => {
            const temperature = e.features[0].properties.temperature.toFixed(1)
            popup.setLngLat(e.lngLat).setHTML('+' + temperature + ' &degC').addTo(this.map);
        });

        // const camera = this.map.getCamera();
        // console.log(camera);
        // this.loaded = true;

        this.sendMapView();
      });

      this.map.on('moveend', () => {
        this.sendMapView();
      });
    },
    sendMapView() {
      const center = this.map.getCenter();
        window.parent.postMessage({
          "latitude": center.lat,
          "longitude": center.lng,
          "zoom": this.map.getZoom()
        }, 
        '*');
    },
    updateMap(updates) {
      console.log('updating')
      if (this.tbar != updates.tbar) {
        if (isNaN(updates.tbar)) {
          console.error('The new tbar value is non a number.');
        } else {
          this.tbar = updates.tbar;
          console.log('new tbar: ', this.tbar);
          this.getTemperatures()
            .then(() => {
              console.log(this.data.features[0])
              const source = this.map.getSource('temperature');
              source.setData(this.data);
              console.log('data was set');
            })
            .catch(error => {
              console.error('Error occurred while updating temperatures:', error);
            });
          }
      }

      if(updates.projection && (this.projection != updates.projection)) {
        this.projection = updates.projection;
        this.map.setProjection(this.projection);
      }
      
    },
    async getTemperatures() {
      let url = window.location.origin
      // const path = url + '/api/temperature?tbar=' + this.tbar;

      // for local testing
      url = url.slice(0, url.lastIndexOf(":"))
      const path = url + ':5002/temperature?tbar=' + this.tbar;

      try {
        const response = await axios.get(path);
        this.temperatures = response.data.temps;
        this.latitudes = response.data.lats;
        this.longitudes = response.data.lons;
        this.getGeoJSON();
        console.log('temps gotten')
      } catch (error) {
        console.error('Error occurred while gathering data:', error);
        throw error; 
      }
    },
  },
  mounted() {
    const query = this.$route.query.tbar
    // todo handle error better here
    if (query) {
      this.tbar = query;
    }
    this.getTemperatures()
      .then(() => {
        this.initMap();
      })
      .catch(error => {
        console.error('Error occurred during the first function:', error);
      });
    window.addEventListener("message", (event) => {
      // if (event.origin !== "https://en-roads.climateinteractive.org") return;
      // console.log(event.data);
      this.updateMap(event.data);
      
    });
    
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
