<script>
import axios from 'axios';
import mapboxgl from "mapbox-gl";
import "../../node_modules/mapbox-gl/dist/mapbox-gl.css"
import MapboxGeocoder from '@mapbox/mapbox-gl-geocoder';
import '@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.css';
import '../assets/mapbox-bc3.css'

export default {
  data() {
      return {
          temperatures: [],
          latitudes: [],
          longitudes: [],
          data: {},
          accessToken: 'pk.eyJ1Ijoic2hhcmlxYWgiLCJhIjoiY2x0MmQ3OHMzMWt5dTJxbnc0cmk3dHE5cyJ9.HQ80jJpT5LRbIHjQLFgt3Q',
          // colors from IPCC: https://www.ipcc.ch/site/assets/uploads/2022/09/IPCC_AR6_WGI_VisualStyleGuide_2022.pdf#page=13
          celsiusScale: ['rgb(254, 254, 203)', 'rgb(248, 222, 127)', 'rgb(235, 167, 84)', 'rgb(222, 116, 79)', 'rgb(164, 70 ,66)', 'rgb(89 ,47, 35)', 'rgb(25 ,25, 0)'],          
          fahrenheitScale: ['rgb(254, 254, 203)', 'rgb(251, 237, 158)', 'rgb(245, 212, 112)', 'rgb(238, 178, 87)', 'rgb(231, 147, 82)', 'rgb(222, 116, 79)', 'rgb(194, 84, 73)', 'rgb(149, 65, 61)', 'rgb(104, 52, 42)', 'rgb(62, 38, 22)', 'rgb(25, 25, 0)'],
          logBase: 2,
          tbar: undefined,
          map: undefined,
          projection: 'globe',
          unit: undefined,
          loading: true,
          start: undefined,
          dataTime: undefined,
          renderTime: undefined,
          count: 0,
          fillColor: [],
          resolution: undefined,
          tooltip: undefined,
          tooltipCenter: undefined
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

          let polygon;
          if (this.resolution == 1.5) {
              // 4s
              polygon = [[[longitude-.75, latitude-.75], [longitude-.75, latitude+.75], [longitude+.75, latitude+.75], [longitude+.75, latitude-.75], [longitude-.75, latitude-.75]]]
          } else if (this.resolution == 2) {
              polygon = [[[longitude-1, latitude-1], [longitude-1, latitude+1], [longitude+1, latitude+1], [longitude+1, latitude-1], [longitude-1, latitude-1]]]
          }  else { // 1-degree
              //     5.5s
              polygon = [[[longitude-.5, latitude-.5], [longitude-.5, latitude+.5], [longitude+.5, latitude+.5], [longitude+.5, latitude-.5], [longitude-.5, latitude-.5]]]
           } 
          
          const feature = {
            "type": "Feature",
            "geometry": {
              "type": "Polygon",
              "coordinates": polygon
            },
            "properties": {
              'center': [longitude, latitude]
            }
          }
          if (this.unit == 'C') {
            feature.properties.temperature = temperature;
          } else {
            feature.properties.temperature = this.toFahrenheit(temperature);
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
      const projection = this.$route.query.projection

      longitude = longitude ? longitude : 0
      latitude = latitude ? latitude : 0
      zoom = zoom ? zoom : 2
      if (projection) {
        this.projection = projection
      }
      // todo add error handling to ensure in range

      this.map = new mapboxgl.Map({
        container: 'map', 
        projection: this.projection,
        // style: 'mapbox://styles/mapbox/streets-v8', 
        // style: 'mapbox://styles/shariqah/clz1y4dvk02ae01p9697g9k2o/draft', // using coastline data is ~9s as opposed to mapbox countires data (~6s)
        style: 'mapbox://styles/shariqah/clzfw8mfr00cj01qp3qmc1ypy/draft', // takes about 1.2s to render without coastline; 1.4 with
        // style: 'mapbox://styles/mapbox/streets-v12?optimize=true', // takes about 2s to render without coastline; 2.4 wiht
        // ?optimize=true', //adding optimize=true didnt seem to hlep anything
        // style: 'mapbox://styles/mapbox/light-v11', // style URL for Mapbox Light
        zoom: zoom,
        maxZoom: 7,
        center: [longitude, latitude]
      });

      this.map.on('load', () => {
        
        // const layers = this.map.getStyle().layers;
        // for (const layer of layers) {
        //     // console.log(layer)
        //     // if ((layer.type === 'line')) {
        //     //     console.log(layer)
        //     // } 
        //     if ((layer.id === 'water')) {
        //       console.log(layer)
        //     }
        // }

        // // Remove globe halo to allow for contrast between black background and color scale
        // this.map.setFog({
        //     "horizon-blend": 0,
        //   });
          
        this.map.addSource('temperature', {
          type: 'geojson',
          data: this.data,
        });

        this.map.addLayer(
          {
              'id': 'temperature-map',
              'source': 'temperature',
              'type': 'fill',
              'paint': {
                  'fill-color': this.fillColor,
              }
          },
          "countries-bg"
        );

        // todo make this work for equal earth
        if (this.projection == 'globe') {
          const geocoder = new MapboxGeocoder({
            accessToken: this.accessToken,
            mapboxgl: mapboxgl
          })
          this.map.addControl(geocoder);
        }
        this.map.addControl(new mapboxgl.NavigationControl());

        this.tooltip = new mapboxgl.Popup();
        this.map.on('click', 'temperature-map', (e) => {
            console.log('click e', e.features);
            this.tooltipCenter = JSON.parse(e.features[0].properties.center);
            const temperature = this.getTemperature();
            this.tooltip.setLngLat(e.lngLat).setHTML('+' + temperature + ' &deg' + this.unit).addTo(this.map);
        });

        this.sendMapView();
      });
      
      this.map.on('moveend', () => {
        this.sendMapView();
      });

      this.map.on('idle', () => {
        const end = Date.now();
        console.log(`Render time: ${end - this.dataTime} ms`);
        this.loading = false;
      });
    },
    getTemperature() {
      // Convert center of pixel to index for temperature data
      let i;
      let j;
      if (this.resolution == 1.5) {
        i = (this.tooltipCenter[1] + 89.25) / 1.5;
        j = this.tooltipCenter[0] / 1.5;
      } 
      // todo review below
      else if (this.resolution == 2) {
        i = (this.tooltipCenter[1] + 89) / 2;
        j = this.tooltipCenter[0] / 2;
      }  else { // 1-degree
        i = (this.tooltipCenter[1] + 89.5);
        j = this.tooltipCenter[0] - .5;
      }  
      let temperature = this.temperatures[i][j];

      if (temperature < 10) {
        temperature = temperature.toFixed(1)
      } else {
        temperature = Math.round(temperature)
      }

      return temperature
    },
    sendMapView() {
      const center = this.map.getCenter();
        window.parent.postMessage({
          "latitude": center.lat,
          "longitude": center.lng,
          "zoom": this.map.getZoom(),
          "bearing": this.map.getBearing(),
          "pitch": this.map.getPitch()
        }, 
        '*');
    },
    updateMap(updates) {
      if (this.tbar != updates.tbar) {
        if (isNaN(updates.tbar)) {
          console.error('The new tbar value is non a number.');
        } else {
          this.tbar = updates.tbar;
          this.getTemperatures()
            .then(() => {
              const source = this.map.getSource('temperature');
              source.setData(this.data);
              if (this.tooltip.isOpen()) {
                const temperature = this.getTemperature();
                this.tooltip.setHTML('+' + temperature + ' &deg' + this.unit);
              }
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

      // todo ck if update provided AT ALL?
      const center = this.map.getCenter();

      if ((updates.longitude != center.lng) || (updates.latitude != center.lat) || 
        (updates.zoom != this.map.getZoom()) || (updates.bearing != this.map.getBearing()) || (updates.pitch != this.map.getPitch())
        ) 
        {
          let position = {
            "center": [updates.lon, updates.lat],
            "zoom": updates.zoom,
            "bearing": updates.bearing,
            "pitch": updates.pitch
          };
          this.map.jumpTo(position);
      }
      
    },
    async getTemperatures() {
      let url = window.location.origin
      // const path = url + '/api/temperature?tbar=' + this.tbar + '&resolution=' + this.resolution;

      // for local testing
      url = url.slice(0, url.lastIndexOf(":"))
      const path = url + ':5002/temperature?tbar=' + this.tbar + '&resolution=' + this.resolution;

      try {
        const response = await axios.get(path);
        this.temperatures = response.data.temps;
        this.latitudes = response.data.lats;
        this.longitudes = response.data.lons;
        console.log('res', response);
        console.log('temps', this.temperatures);
        this.getGeoJSON();
      } catch (error) {
        console.error('Error occurred while gathering data:', error);
        throw error; 
      }
    },
    getPaintProperties(layerName) {
      const sourcePaint = JSON.parse(JSON.stringify(this.map.getLayer(layerName).paint));
      const properties = Object.keys(sourcePaint._values);
      const paint = {};
      for (let property of properties) {
        // line-floorwidth is in the layer data but not supported when you try to get the property
        if (property != 'line-floorwidth') { 
          paint[property] = this.map.getPaintProperty(layerName, property);
        }
      }
      return paint;
    },
    toFahrenheit(celsius) {
      return celsius * 9 / 5;
    }
  },
  mounted() {
    // todo handle error better here
    const tbar = this.$route.query.tbar
    this.tbar = tbar ? tbar : 0;
    const resolution = this.$route.query.resolution
    this.resolution = resolution ? resolution : 1.5;

    let unit = this.$route.query.temperature_unit;
    if (unit) {
      unit = unit.toUpperCase();
      if ((unit != 'F') && (unit != 'C')) {
        console.error('Temperature unit can be either C or F.');
      }
    } else {
      unit = 'C';
    }
    this.unit = unit;

    this.fillColor = [
      'interpolate',
      ['linear'],
      ['get', 'temperature']
    ];
    let scale = this.celsiusScale;
    if (this.unit == 'F') {
      scale = this.fahrenheitScale;
    }
    for (let i = 0; i < scale.length; i++) {
      this.fillColor.push(...[i, scale[i]]);
    }

    // this.start = Date.now();
    this.getTemperatures()
      .then(() => {
        this.dataTime = Date.now();
        // console.log(`Data time: ${this.dataTime - this.start} ms`);
        this.initMap();
      })
      .catch(error => {
        console.error('Error occurred during the first function:', error);
      });
    window.addEventListener("message", (event) => {
      // if (event.origin !== "https://en-roads.climateinteractive.org") return;
      // if (event.origin !== "https://en-roads.dev.climateinteractive.org") return;
      console.log('received: ', event);
      this.updateMap(event.data);
      
    });
    
  }
}

</script>

<template>
  <div v-if="loading" class="loader-container">
    <div class="loader"></div>
  </div>

  <div id="map"></div>

  <!-- todo move to new component -->
  <div class='my-legend'>
  <div class='legend-title'>Temperature Increase (&deg{{ unit }})</div>
  <div class='legend-scale'>
    <ul class='legend-labels'>
    <!-- todo make this less repetitive -->
      <div v-if="unit == 'C'">
        <li><span :style="{background: celsiusScale[0]}"></span>0</li>
        <li v-for="n in celsiusScale.length-2">
          <span :style="{background: celsiusScale[n]}"></span>{{n}}
        </li>
        <li><span :style="{background: celsiusScale[celsiusScale.length-1]}"></span>{{(celsiusScale.length-1)}}+</li>
      </div>
      <div v-else>
        <li><span :style="{background: fahrenheitScale[0]}"></span>0</li>
        <li v-for="n in fahrenheitScale.length-2">
          <span :style="{background: fahrenheitScale[n]}"></span>{{ n }}
        </li>
        <li><span :style="{background: fahrenheitScale[fahrenheitScale.length-1]}"></span>{{ (fahrenheitScale.length-1) }}+</li>
      </div>
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

  }
.my-legend .legend-scale ul li {
  display: block;
  float: left;
  width: 30px;
  margin-bottom: 6px;
  text-align: center;
  font-size: 80%;
  list-style: none;

  }
.my-legend ul.legend-labels li span {
  display: block;
  float: left;
  height: 15px;
  width: 30px;

  }
  
.my-legend a {
  color: #777;
  }

.my-legend {
  z-index: 2;
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

</style>
