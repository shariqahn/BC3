<script>
import axios from 'axios';
import mapboxgl from "mapbox-gl";
import "../../node_modules/mapbox-gl/dist/mapbox-gl.css"
import { MapboxSearchBox } from "@mapbox/search-js-web"

export default {
  data() {
      return {
          changes: [],
          latitudes: [],
          longitudes: [],
          data: {},
          accessToken: 'pk.eyJ1Ijoic2hhcmlxYWgiLCJhIjoiY2x0MmQ3OHMzMWt5dTJxbnc0cmk3dHE5cyJ9.HQ80jJpT5LRbIHjQLFgt3Q',
          // todo improve colors
          colorScale: 
          ['rgb(84, 48, 5)', 'rgb(150, 98, 30)', 'rgb(200, 148, 79)', 'rgb(224, 199, 164)', 'rgb(248, 248, 247)', 'rgb(167, 208, 204)', 'rgb(85, 167, 160)', 'rgb(33, 116, 107)', 'rgb(0, 60, 48)']
          // ['#ff6f00', '#ff9550', '#ffb889', '#ffdcc3', 'white', '#e2c5df', '#c38bbf', '#a2529f', '#800080']

      }
  },
  methods: {
    getGeoJSON(){
      this.data = {
        "type":"FeatureCollection",
        "features":[]
      }

      this.changes.forEach((lats, i) => {
        lats.forEach((change, j) => {
          const latitude = this.latitudes[i]
          const longitude = this.longitudes[j]

          const polygon = [[[longitude-.5, latitude-.5], [longitude-.5, latitude+.5], [longitude+.5, latitude+.5], [longitude+.5, latitude-.5], [longitude-.5, latitude-.5]]]
          const feature = {
            "type": "Feature",
            "geometry": {
              "type": "Polygon",
              "coordinates": polygon
            },
            "properties": {'change': change}
          }
          this.data.features.push(feature)
        })
      })

    },
    initMap() {
      console.log('color len', this.colorScale.size)
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
      // projection: 'equalEarth',
      projection: 'globe',
      // style: 'mapbox://styles/mapbox/streets-v8', 
      style: 'mapbox://styles/mapbox/streets-v12', 
      zoom: zoom,
      maxZoom: 7,
      center: [longitude, latitude]
      });

      map.on('load', () => {
        const search = new MapboxSearchBox();
        search.accessToken = this.accessToken;
        map.addControl(search);
        map.addControl(new mapboxgl.NavigationControl());
        // // remove globe halo
        map.setFog({
            "horizon-blend": 0,
          });

        map.addSource('precipitation', {
          type: 'geojson',
          data: this.data,
        });

        map.addLayer(
          {
              'id': 'precipitation-map',
              'source': 'precipitation',
              'type': 'fill',
              'paint': {
                    'fill-color': [
                        'interpolate',
                        ['linear'],
                        ['get', 'change'],
                        -40,
                        this.colorScale[0],
                        -30,
                        this.colorScale[1],
                        -20,
                        this.colorScale[2],
                        -10,
                        this.colorScale[3],
                        0,
                        this.colorScale[4],
                        10,
                        this.colorScale[5],
                        20,
                        this.colorScale[6],
                        30,
                        this.colorScale[7],
                        40,
                        this.colorScale[8]

                    ],

              }
          },
          // todo play w layers more
          "admin-1-boundary-bg",
          // "admin-2-boundaries-bg"
        );

        const popup = new mapboxgl.Popup();
        map.on('click', 'precipitation-map', (e) => {
            const change = e.features[0].properties.change.toFixed(1)
            popup.setLngLat(e.lngLat).setHTML(change + '%').addTo(map);
        });
      });
    },
    getPrecipitationChange() {
      const query = this.$route.query.tbar
      // todo handle error better here
      const tbar = query ? query : 0
      let url = window.location.origin
      //url = url.slice(0, url.lastIndexOf(":"))
      const path = url + '/api/precipitation?tbar=' + tbar;
      axios.get(path)
        .then((res) => {
          // todo structure data
          this.changes = res.data.changes;
          this.latitudes = res.data.lats;
          this.longitudes = res.data.lons;
          this.getGeoJSON();
          this.initMap();
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
  created() {
    this.getPrecipitationChange();
    this.$watch(
      () => this.$route.query,
      (toParams, previousParams) => {
        // todo react to route changes
        this.getPrecipitationChange();
      }
    )
  }
}

</script>

<template>
  <div id="map"></div>
  <!-- todo move to new component -->
  <div class='my-legend'>
  <div class='legend-title'>Precipitation Change (%PI)</div>
  <div class='legend-scale'>
    <ul class='legend-labels'>
      <li v-for="n in colorScale.length">
        <span :style="{background: colorScale[n-1]}"></span>{{10*(n-1)-40}}
      </li>
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
  width: 35px;
  margin-bottom: 6px;
  text-align: center;
  font-size: 80%;
  list-style: none;
  }
.my-legend ul.legend-labels li span {
  display: block;
  float: left;
  height: 15px;
  width: 35px;
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
  color: #333333;
  padding-right: 7px;
  padding-left: 7px;
  border-color:rgba(0, 0, 0, .1);
  border-style: solid;
  border-radius: 5px;
  border-width: 1px;
}

</style>
