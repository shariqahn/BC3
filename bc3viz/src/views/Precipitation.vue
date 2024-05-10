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
          // ['rgb(255, 111, 0)', 'rgb(255, 125, 25)', 'rgb(255, 140, 51)', 'rgb(255, 154, 77)', 'rgb(255, 169, 102)', 'rgb(255, 183, 128)', 
          // 'rgb(255, 197, 153)', 'rgb(255, 212, 179)', 'rgb(255, 226, 204)', 'rgb(255, 241, 230)', 'rgb(255, 255, 255)', 
          // 'rgb(242, 230, 242)', 'rgb(230, 204, 230)', 'rgb(217, 179, 217)', 'rgb(204, 153, 204)', 'rgb(192, 128, 192)', 
          // 'rgb(179, 102, 179)', 'rgb(166, 77, 166)', 'rgb(153, 51, 153)', 'rgb(141, 26, 141)', 'rgb(128, 0, 128)'],
          ['#ff6f00', '#ff9550', '#ffb889', '#ffdcc3', 'white', '#e2c5df', '#c38bbf', '#a2529f', '#800080']

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
      zoom = zoom ? zoom : 1
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
                //   'fill-color': [
                //       'interpolate',
                //       ['linear'],
                //       ['get', 'change'],
                //       -100,
                //       'yellow',
                //       0,
                //       'white',
                //       100,
                //       'purple'
                //   ],
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

        const search = new MapboxSearchBox();
        search.accessToken = this.accessToken;
        map.addControl(search);
        map.addControl(new mapboxgl.NavigationControl());
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
  padding-right: 7px;
  padding-left: 7px;
  border-color: grey;
  border-style: solid;
  border-radius: 5px;
  border-width: 1px;
}

</style>
