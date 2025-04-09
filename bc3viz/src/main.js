import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import mapboxgl from "mapbox-gl";


// XXX: This is a customized implementation of the `Popup._getAnchor` method from the mapbox-gl package:
//   https://github.com/mapbox/mapbox-gl-js/blob/main/src/ui/popup.ts
// We monkey patch (override) the default implementation with our custom implementation so that
// it takes the map padding into account when positioning the Popup, which is needed to avoid
// overlap issues with the scenario box in the upper left.
mapboxgl.Popup.prototype._getAnchor = function (bottomY) {
    if (this.options.anchor) {
      return this.options.anchor
    }
  
    const map = this._map
    const container = this._container
    const pos = this._pos
  
    if (!map || !container || !pos) return 'bottom'
  
    const width = container.offsetWidth
    // const height = container.offsetHeight
    const tipHeight = getComputedStyle(document.querySelector('.mapboxgl-popup-tip')).borderTopWidth;
    const height = parseInt(tipHeight, 10) + container.offsetHeight;
  
    // XXX: The following change is based on a draft PR that takes map padding
    // into account when positioning the Popup:
    //   https://github.com/mapbox/mapbox-gl-js/pull/11846/files
    // const isTop = pos.y + bottomY < height
    // const isBottom = pos.y > map.transform.height - height
    // const isLeft = pos.x < width / 2
    // const isRight = pos.x > map.transform.width - width / 2
    const isTop = pos.y + bottomY < height + map.transform.padding.top
    const isBottom = pos.y > map.transform.height - height - map.transform.padding.bottom
    const isLeft = pos.x < width / 2 + map.transform.padding.left
    const isRight = pos.x > map.transform.width - width / 2 - map.transform.padding.right
  
    if (isTop) {
      if (isLeft) return 'top-left'
      if (isRight) return 'top-right'
      return 'top'
    }
    if (isBottom) {
      if (isLeft) return 'bottom-left'
      if (isRight) return 'bottom-right'
    }
    if (isLeft) return 'left'
    if (isRight) return 'right'
  
    return 'bottom'
  }

const app = createApp(App)

app.use(router)

app.mount('#app')
