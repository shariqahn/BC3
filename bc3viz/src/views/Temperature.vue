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
          // colors from IPCC: https://www.ipcc.ch/site/assets/uploads/2022/09/IPCC_AR6_WGI_VisualStyleGuide_2022.pdf#page=13
          celsiusScale: ['rgb(254, 254, 203)', 'rgb(248, 222, 127)', 'rgb(235, 167, 84)', 'rgb(222, 116, 79)', 'rgb(164, 70 ,66)', 'rgb(89 ,47, 35)', 'rgb(25 ,25, 0)'],          
          fahrenheitScale: ['rgb(254, 254, 203)', 'rgb(245, 212, 112)', 'rgb(231, 147, 82)', 'rgb(194, 84, 73)', 'rgb(104, 52, 42)', 'rgb(25, 25, 0)'],
          logBase: 2,
          tbar: undefined,
          map: undefined,
          projection: 'globe',
          unit: undefined,
          loading: true,
          fillColor: [],
          resolution: undefined,
          tooltip: undefined,
          geocoder: undefined,
          navigation: undefined,
          hideLegend: undefined,
          tooltipText: 'Temperature increase<br>at this location',
          tooltipColor: 'black',
          marker: null
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
            }
          }
          if (this.unit == 'C') {
            feature.properties = {'temperature': temperature};
          } else {
            feature.properties = {'temperature': this.toFahrenheit(temperature)};
          }
          this.data.features.push(feature)
        })
      })
    },
    initMap() {
      mapboxgl.accessToken = import.meta.env.VITE_APP_MAPBOX_KEY;
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
        zoom: this.zoom,
        maxZoom: 5, // Note: Layers beyond this zoom point were removed for performance reasons ("POI", "settlement-subdivision-label", "waterway-label", "admin-1-boundary-bg"). Add them back if this parameter changes.
        // todo change this to a not "this" var
        center: [this.longitude, this.latitude]
      });

      this.map.on('load', () => {
          
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
        // todo include this check upon update
        // if (this.projection == 'globe') {
        //   this.geocoder = new MapboxGeocoder({
        //     accessToken: import.meta.env.VITE_APP_MAPBOX_KEY,
        //     mapboxgl: mapboxgl,
        //     placeholder: 'Search places'
        //   })
        //   this.map.addControl(this.geocoder);
        // }
        this.navigation = new mapboxgl.NavigationControl({showCompass: false});
        this.map.addControl(this.navigation);

        this.tooltip = new mapboxgl.Popup();
        this.map.on('click', 'temperature-map', (e) => {
            const tooltipLatitude = e.lngLat.lat;
            const tooltipLongitude = e.lngLat.lng;
            this.tooltip
              .setLngLat([tooltipLongitude, tooltipLatitude])
            // todo include year from enroads
              .setHTML(this.getTooltipHTML())             
              .addTo(this.map);
            console.log('popup was added');
            console.log({
              "kind": 'tooltip-changed',
              "lat": tooltipLatitude,
              "lon": tooltipLongitude
            });
            window.parent.postMessage({
              "kind": 'tooltip-changed',
              "lat": tooltipLatitude,
              "lon": tooltipLongitude
            }, 
            '*');
        });
        // todo differentiate bw message close to prevent infiinite loop
        this.tooltip.on('close', () => {
          
          // todo better solution
          if (this.messageClosed){
            this.messageClosed = false;
          } else {
            window.parent.postMessage({
              "kind": 'tooltip-changed'
            }, 
            '*');
            console.log('popup was closed');
            console.log({
              "kind": 'tooltip-changed'
            })
          }

          
        });
      });
      
      // this.map.on('dragend', () => {
      //   this.sendMapView();
      // });
      this.map.on('moveend', (event) => {
        if (event.originalEvent) {
          this.sendMapView();
        }
      });

      this.map.on('idle', () => {
        this.loading = false;
        window.parent.postMessage({ kind: 'map-loaded' }, '*');
        console.log('map loaded');
      });
    },
    getTooltipHTML() {
      const tooltipLocation = this.tooltip.getLngLat();
      const temperature = this.getTemperature(tooltipLocation.lng, tooltipLocation.lat);
      return `<div id="tooltip-temperature" style="color: ${this.tooltipColor}">
                <span style="font-size: 8vw">+${temperature}</span><span style="font-size: 3.5vw; vertical-align: 90%">&deg;${this.unit}</span>                
              </div>
              <div style="font-size: 2.5vw; font-weight: bold; white-space: nowrap">
                ${this.tooltipText}
              </div>`
    },
    getTemperature(longitude, latitude) {
      // Convert center of pixel to index for temperature data
      let latitudeIndex;
      let longitudeIndex;
      if (this.resolution == 1.5) {
        const minLatitude = -89.25;
        let i = Math.round((latitude - minLatitude) / this.resolution);
        // Ensure the index is within bounds
        latitudeIndex = Math.max(0, Math.min(i, this.temperatures.length - 1));

        i = Math.round((((longitude % 360) + 360) % 360) / this.resolution);
        longitudeIndex = i % this.temperatures[0].length;
      } 
      // else if (this.resolution == 2) {
      //   latitudeIndex = (location[1] + 89) / 2;
      //   longitudeIndex = location[0] / 2;
      // }  else { // 1-degree
      //   latitudeIndex = location[1] + 89.5;
      //   longitudeIndex = location[0] - .5;
      // }  
      // console.log(latitudeIndex, longitudeIndex);
      let temperature = this.temperatures[latitudeIndex][longitudeIndex];

      if (this.unit == 'F') {
        temperature = this.toFahrenheit(temperature);
      }

      if (temperature < 10) {
        temperature = temperature.toFixed(1)
      } else {
        temperature = Math.round(temperature)
      }

      return temperature
    },
    sendMapView() {
      const center = this.map.getCenter();
        console.log('map changed. notifying en-roads:');
        console.log({
          "kind": 'position-changed',
          "lat": center.lat,
          "lon": center.lng,
          "zoom": this.map.getZoom(),
        });
        window.parent.postMessage({
          "kind": 'position-changed',
          "lat": center.lat,
          "lon": center.lng,
          "zoom": this.map.getZoom(),
        }, 
        '*');
    },
    setMap(features) {
      const messageType = features.kind;
      switch (messageType) {
        case 'set-config':
          this.tooltipColor = features.scenarioColor;
          this.tooltipText = features.tooltipText;
          if (this.tooltip.isOpen()) {
            this.tooltip.setHTML(this.getTooltipHTML());
          }
          break;
        case 'set-params':
          // Sent from En-ROADS to BC3 to change map temperature, projection, and/or position.
          let updateTooltip = false;
          if (this.unit != features.temperature_unit) {
            this.setUnit(features.temperature_unit);
            updateTooltip = true;
          }
          if (this.tbar != features.tbar) {
            console.log('termperatue changed');
            this.tbar = features.tbar;
            updateTooltip = true;
          }
          if (updateTooltip) {
            this.getData()
              .then(() => {
                console.log('updating temp');
                const source = this.map.getSource('temperature');
                source.setData(this.data);
                if (this.tooltip.isOpen()) {
                  this.tooltip.setHTML(this.getTooltipHTML());
                }
              })
              .catch(error => {
                console.error('Error occurred while updating temperatures:', error);
              });
          }

          // todo ck if update provided AT ALL?
          const keys = ['lon', 'lat', 'zoom'];
          const hasAllKeys = keys.every(key => key in features);
          if (!hasAllKeys) {
            // todo should other things still be updated if this fails
            console.error('The object does not contain all of the required keys to change the map view: lon, lat, and zoom.');
          } else {
            const center = this.map.getCenter();
            if (
              features.lon != center.lng || 
              features.lat != center.lat || 
              features.zoom != this.map.getZoom()
            ) {
              let position = {
                "center": [features.lon, features.lat],
                "zoom": features.zoom,
                "bearing": 0,
                "pitch": 0
              };
              this.map.jumpTo(position);
            }
          }

          if (this.projection != features.projection) {
            this.projection = features.projection;
            this.map.setProjection(this.projection);
            // if (this.projection == 'globe') {
            //   this.map.removeControl(this.navigation);
            //   this.map.addControl(this.geocoder);
            //   this.map.addControl(this.navigation);
            // } else {
            //   this.map.removeControl(this.geocoder);
            // }
          }
          break;

        // TOOLTIPS
        case 'set-tooltip':
            // Sent from En-ROADS to BC3 to synchronize the tooltip position on a map (after
            // receiving a 'tooltip-changed' event from the other map).
            console.log('set tooltip', this.tooltip);
            if (!('lat' in features)) {
              // Set this flag to differentiate between message close and click close
              this.messageClosed = true;
              this.tooltip.remove();
            } else {
              console.log('setting tooltip');
              this.tooltip
                .setLngLat([features.lon, features.lat])
                .setHTML(this.getTooltipHTML());
                if (!this.tooltip.isOpen()) {
                  console.log('tooltip not open, so addign it');
                  this.tooltip.addTo(this.map);
                }
            }
            break;
          
        // MARKERS
        case 'set-marker':
          // Sent from En-ROADS to BC3 to set or clear the marker/pin position on a map (after
          // the user selects a location in the search results or resets the search box).
          // todo change this to match tooltip logic with addto
          if (!this.marker) {
            console.log('new marker')
            this.marker = new mapboxgl.Marker()
              .setLngLat([features.lon, features.lat])
              .addTo(this.map);
          } else if (!('lat' in features)) {
            this.marker.remove();
            this.marker = null;
            console.log('no lat')
          } else {
            console.log('setting marker')
            this.marker.setLngLat([features.lon, features.lat]);
          }
          break;
      }
    },
    async getData() {
      let url = window.location.origin
      const path = url + '/api/temperature?tbar=' + this.tbar + '&resolution=' + this.resolution;

      // for local testing
      // url = url.slice(0, url.lastIndexOf(":"))
      // const path = url + ':5002/temperature?tbar=' + this.tbar + '&resolution=' + this.resolution;

      try {
        const response = await axios.get(path);
        this.temperatures = response.data.temps;
        this.latitudes = response.data.lats;
        this.longitudes = response.data.lons;
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
    },
    setUnit(unit) {
      unit = unit.toUpperCase();
      if ((unit != 'F') && (unit != 'C')) {
        // todo check this error handling
        console.error('Temperature unit can be either C or F. Defaulting to C.');
        unit = 'C';
      }
      this.unit = unit;
      this.fillColor = [
        'interpolate',
        ['linear'],
        ['get', 'temperature']
      ];
      if (this.unit == 'C') {
        for (let i = 0; i < this.celsiusScale.length; i++) {
          this.fillColor.push(...[i, this.celsiusScale[i]]);
        }
      } else {
        for (let i = 0; i < this.fahrenheitScale.length; i++) {
          this.fillColor.push(...[i*2, this.fahrenheitScale[i]]);
        }
      }
    }
  },
  mounted() {
    // todo handle error better here
    const tbar = this.$route.query.tbar;
    this.tbar = tbar ? tbar : 0;
    let longitude = this.$route.query.lon
    let latitude = this.$route.query.lat
    this.longitude = longitude ? longitude : 0
    this.latitude = latitude ? latitude : 0
    let zoom = this.$route.query.zoom
    this.zoom = zoom ? zoom : 2
    const projection = this.$route.query.projection
    if (projection) {
      this.projection = projection
    }
    const resolution = this.$route.query.resolution;
    this.resolution = resolution ? resolution : 1.5;
    const hideLegend = this.$route.query['hide-legend'];
    this.hideLegend = hideLegend ? hideLegend.toLowerCase() : false;

    let unit = this.$route.query.temperature_unit;
    unit = unit ? unit : 'C';
    this.setUnit(unit);

    this.getData()
      .then(() => {
        this.initMap();
      })
      .catch(error => {
        console.error('Error occurred during the first function:', error);
      });
    window.addEventListener("message", (event) => {
      // if (event.origin !== "https://en-roads.climateinteractive.org") return;
      // if (event.origin !== "https://en-roads.dev.climateinteractive.org") return;
      console.log('received: ', event);
      this.setMap(event.data);
      
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
  <div v-if="!hideLegend" class='my-legend'>
  <div class='legend-title'>Local Temperature Increase (&deg{{ unit }})</div>
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
          <span :style="{background: fahrenheitScale[n]}"></span>{{ n*2 }}
        </li>
        <li><span :style="{background: fahrenheitScale[fahrenheitScale.length-1]}"></span>{{ (fahrenheitScale.length-1)*2 }}+</li>
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
  margin-bottom: .2vw;
  font-size: 90%;
  font-weight: bold;
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
  text-align: center;
  font-size: 80%;
  list-style: none;
  font-weight: bold;
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
  padding-right: 5px;
  padding-left: 5px;
  border-color:rgba(0, 0, 0, .1);
  border-style: solid;
  border-radius: 5px;
  border-width: 1px;
}

.my-legend:hover .legend-scale ul li {
  width: 45px;
}

.my-legend:hover ul.legend-labels li span {
  height: 23px;
  width: 45px;
}
  
.my-legend:hover {
  bottom: 43px;
  right: 23px;
  font-size: 135%;
}

</style>
