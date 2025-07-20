This repo creates a visualization of temperature projections using pattern scaling data as a part of MIT's [Bringing Computation to the Climate Challenge](https://bc3.mit.edu/). See a demo of the work we did in collaboration with En-ROADS [here](https://bc3.mit.edu/demos/en-roads/).

# Local Testing
1. clone repo
2. (optional) create a local python environment
```
cd api
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3. start the API from that same directory with
`python3 main.py`
4. start the front end
```
cd ../bc3viz
npm install
npm run dev
```
5. view the map at http://localhost:5173/temperature

example with parameter options:
http://localhost:5173/temperature?tbar=2.5&temperature_unit=C&projection=equalEarth&lat=18&lon=0&zoom=0.28&bearing=0&pitch=0&hide-legend=1

6. ensure line 343 in bc3viz/src/views/Temperature.vue is commented and the "local testing" lines are uncommented. It should look like:
```
let url = window.location.origin
// const path = url + '/api/temperature?tbar=' + this.tbar + '&resolution=' + this.resolution;

// for local testing
url = url.slice(0, url.lastIndexOf(":"))
const path = url + ':5002/temperature?tbar=' + this.tbar + '&resolution=' + this.resolution;
```
7. add .env file in bc3viz with `VITE_APP_MAPBOX_KEY=<mapbox api token>`