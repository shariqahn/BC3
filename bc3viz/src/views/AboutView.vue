<!-- <script setup> -->
<script>
// import { RouterLink, RouterView } from 'vue-router'
// import HelloWorld from './components/HelloWorld.vue'
import axios from 'axios';
import { Loader } from "@googlemaps/js-api-loader"
import chroma from "chroma-js"
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
      }
  },
  methods: {
    getGreeting() {
      const path = 'http://localhost:5000/greeting';
      axios.get(path)
        .then((res) => {
          this.flaskGreeting = res.data.greeting;

        })
        .catch((error) => {
          console.error(error);
        });
    },
//     Legend() {
//       // Copyright 2021, Observable Inc.
// // Released under the ISC license.
// // https://observablehq.com/@d3/color-legend
// function Legend(color, {
//   title,
//   tickSize = 6,
//   width = 320, 
//   height = 44 + tickSize,
//   marginTop = 18,
//   marginRight = 0,
//   marginBottom = 16 + tickSize,
//   marginLeft = 0,
//   ticks = width / 64,
//   tickFormat,
//   tickValues
// } = {}) {

//   function ramp(color, n = 256) {
//     const canvas = document.createElement("canvas");
//     canvas.width = n;
//     canvas.height = 1;
//     const context = canvas.getContext("2d");
//     for (let i = 0; i < n; ++i) {
//       context.fillStyle = color(i / (n - 1));
//       context.fillRect(i, 0, 1, 1);
//     }
//     return canvas;
//   }

//   const svg = d3.create("svg")
//       .attr("width", width)
//       .attr("height", height)
//       .attr("viewBox", [0, 0, width, height])
//       .style("overflow", "visible")
//       .style("display", "block");

//   let tickAdjust = g => g.selectAll(".tick line").attr("y1", marginTop + marginBottom - height);
//   let x;

//   // Continuous
//   if (color.interpolate) {
//     const n = Math.min(color.domain().length, color.range().length);

//     x = color.copy().rangeRound(d3.quantize(d3.interpolate(marginLeft, width - marginRight), n));

//     svg.append("image")
//         .attr("x", marginLeft)
//         .attr("y", marginTop)
//         .attr("width", width - marginLeft - marginRight)
//         .attr("height", height - marginTop - marginBottom)
//         .attr("preserveAspectRatio", "none")
//         .attr("xlink:href", ramp(color.copy().domain(d3.quantize(d3.interpolate(0, 1), n))).toDataURL());
//   }

//   // Sequential
//   else if (color.interpolator) {
//     x = Object.assign(color.copy()
//         .interpolator(d3.interpolateRound(marginLeft, width - marginRight)),
//         {range() { return [marginLeft, width - marginRight]; }});

//     svg.append("image")
//         .attr("x", marginLeft)
//         .attr("y", marginTop)
//         .attr("width", width - marginLeft - marginRight)
//         .attr("height", height - marginTop - marginBottom)
//         .attr("preserveAspectRatio", "none")
//         .attr("xlink:href", ramp(color.interpolator()).toDataURL());

//     // scaleSequentialQuantile doesn’t implement ticks or tickFormat.
//     if (!x.ticks) {
//       if (tickValues === undefined) {
//         const n = Math.round(ticks + 1);
//         tickValues = d3.range(n).map(i => d3.quantile(color.domain(), i / (n - 1)));
//       }
//       if (typeof tickFormat !== "function") {
//         tickFormat = d3.format(tickFormat === undefined ? ",f" : tickFormat);
//       }
//     }
//   }

//   // Threshold
//   else if (color.invertExtent) {
//     const thresholds
//         = color.thresholds ? color.thresholds() // scaleQuantize
//         : color.quantiles ? color.quantiles() // scaleQuantile
//         : color.domain(); // scaleThreshold

//     const thresholdFormat
//         = tickFormat === undefined ? d => d
//         : typeof tickFormat === "string" ? d3.format(tickFormat)
//         : tickFormat;

//     x = d3.scaleLinear()
//         .domain([-1, color.range().length - 1])
//         .rangeRound([marginLeft, width - marginRight]);

//     svg.append("g")
//       .selectAll("rect")
//       .data(color.range())
//       .join("rect")
//         .attr("x", (d, i) => x(i - 1))
//         .attr("y", marginTop)
//         .attr("width", (d, i) => x(i) - x(i - 1))
//         .attr("height", height - marginTop - marginBottom)
//         .attr("fill", d => d);

//     tickValues = d3.range(thresholds.length);
//     tickFormat = i => thresholdFormat(thresholds[i], i);
//   }

//   // Ordinal
//   else {
//     x = d3.scaleBand()
//         .domain(color.domain())
//         .rangeRound([marginLeft, width - marginRight]);

//     svg.append("g")
//       .selectAll("rect")
//       .data(color.domain())
//       .join("rect")
//         .attr("x", x)
//         .attr("y", marginTop)
//         .attr("width", Math.max(0, x.bandwidth() - 1))
//         .attr("height", height - marginTop - marginBottom)
//         .attr("fill", color);

//     tickAdjust = () => {};
//   }

//   svg.append("g")
//       .attr("transform", `translate(0,${height - marginBottom})`)
//       .call(d3.axisBottom(x)
//         .ticks(ticks, typeof tickFormat === "string" ? tickFormat : undefined)
//         .tickFormat(typeof tickFormat === "function" ? tickFormat : undefined)
//         .tickSize(tickSize)
//         .tickValues(tickValues))
//       .call(tickAdjust)
//       .call(g => g.select(".domain").remove())
//       .call(g => g.append("text")
//         .attr("x", marginLeft)
//         .attr("y", marginTop + marginBottom - height - 6)
//         .attr("fill", "currentColor")
//         .attr("text-anchor", "start")
//         .attr("font-weight", "bold")
//         .attr("class", "title")
//         .text(title));

//   return svg.node();
// }
//     },
    initMap() {
      // todo improve import
      const loader = new Loader({
        apiKey: "AIzaSyB41DRUbKWJHPxaFjMAwdrzWzbVKartNGg",
        version: "weekly",
        // ...additionalOptions,
      });

      loader.load().then(async () => {
        const { Map } = await google.maps.importLibrary("maps");
        const { HeatmapLayer } = await google.maps.importLibrary("visualization");

        
        var sanFrancisco = new google.maps.LatLng(37.774546, -122.433523);

        map = new Map(document.getElementById("map"), {
          zoom: 2,
          center: sanFrancisco,
        });

        var heatMapData = []
        var data = []
        const colors = chroma.scale(['yellow', 'red', 'black']);
        var minTemperature,maxTemperature;
        this.temperatures.temps.forEach(function(itm) {
          const min = Math.min(...itm)
          const max = Math.max(...itm)
          minTemperature = (minTemperature == undefined || min<minTemperature) ? min : minTemperature;
          maxTemperature = (maxTemperature == undefined || max>maxTemperature) ? max : maxTemperature;
        });
        colors.domain([minTemperature, maxTemperature])
        // for (let i = 0; i < this.temperatures.lats.length; i++) {
        //   for (let j = 0; j < this.temperatures.lons.length; j++) {
        //       // const temperature = {location: new google.maps.LatLng(this.temperatures.lats[i], this.temperatures.lons[j]), weight: this.temperatures.temps[i][j]}
        //       // heatMapData.push(temperature)            
              
        //       const latitude = this.temperatures.lats[i]
        //       const longitude = this.temperatures.lons[j]
        //       // const color = colors(this.temperatures.temps[i][j]).css()
        //       const color = "#FF0000"
        //       const square = new google.maps.Rectangle({
        //         strokeColor: color,
        //         strokeOpacity: 0,
        //         strokeWeight: 2,
        //         fillColor: color,
        //         fillOpacity: 0.6,
        //         map,
        //         bounds: {
        //           north: latitude + .5,
        //           south: latitude - .5,
        //           east: longitude + .5,
        //           west: longitude - .5,
        //         },
        //       });
        //       data.push(square)
        //   }
        // }
        console.log('counting')

        let count = 0

        this.temperatures.temps.forEach((lats, i) => {
          lats.forEach((lon, j) => {
            const latitude = this.temperatures.lats[i]
            const longitude = this.temperatures.lons[j]
            const color = colors(this.temperatures.temps[i][j]).css()
            // const color = "#FF0000"
            // const square = new google.maps.Rectangle({
            //   strokeColor: color,
            //   strokeOpacity: 0,
            //   strokeWeight: 2,
            //   fillColor: color,
            //   fillOpacity: 0.6,
            //   map,
            //   bounds: {
            //     north: latitude + .5,
            //     south: latitude - .5,
            //     east: longitude + .5,
            //     west: longitude - .5,
            //   },
            // });
            // map.data.add(square)

            const outerCoords = [
              { lat: latitude + .5, lng: longitude + .5 },
              { lat: latitude + .5, lng: longitude - .5 },
              { lat: latitude - .5, lng: longitude - .5 },
              { lat: latitude - .5, lng: longitude + .5 }, // north east
            ];

            const x = map.data.add({
              geometry: new google.maps.Data.Polygon([
                outerCoords
              ]),
              fillColor: color
            });
            console.log(x)
            count += 1;
          })
        })
        console.log(count)

        // const legend = document.getElementById("legend");
        // const l = Legend(d3.scaleDiverging([-0.1, 0, 0.1], d3.interpolatePiYG), {
        //   title: "Daily change",
        //   tickFormat: "+%"
        // })
        // var legend = d3
        //   .select('#legend')
        //   .append('svg')
        //             // .selectAll('.legendItem')
        //             .data(l);
        
        // map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(legend);


        // var heatmap = new HeatmapLayer({
        //   data: heatMapData,
        //   // dissipating: true,
        //   map: map,
        //   gradient: ['yellow', 'red', 'black'],
        //   radius: 50
        // });
        // heatmap.setMap(map);


      });
    },
    getTemperatures() {
      // console.log(this.$route.query)
      const tbar = this.$route.query.tbar
      const path = 'http://localhost:5000/temperature?tbar=' + tbar;
      console.log(path)
      axios.get(path)
        .then((res) => {
          // console.log(res)
          this.temperatures = res.data;
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
        console.log('q change')
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
