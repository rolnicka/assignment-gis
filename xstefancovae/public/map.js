/**
 * Created by eleon on 15.11.2017.
 */

/* Init map */
mapboxgl.accessToken = 'pk.eyJ1IjoiZWxlb24iLCJhIjoiY2o5eDVtN21rNTY5ZDMybXZjbzJ0dXNiZSJ9.CuTF0IXYJD97VHFjS_UdQg';
var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v10',
    center: [19.65, 48.5],
    zoom: 6.45
});
var layers = [];

/* Erase layers from the map */
document.getElementById("btn_clear").addEventListener("click", function(){clear();});
function clear() {
    layers.forEach((layer) => {
        map.removeLayer(layer.id);
        map.removeSource(layer.id);
    });
    layers = [];
}

/* Listeners for GUI elements */
document.getElementById("btn_city_sport").addEventListener("click", function(){get_data("city_sport",
    document.getElementById('input_location').value, document.getElementById('input_place').value,
    document.getElementById('gradient').checked);});
document.getElementById("btn_city_life").addEventListener("click", function(){get_data("city_life",
    document.getElementById('input_location').value, document.getElementById('input_place').value,
    document.getElementById('gradient').checked);});
document.getElementById("btn_city_tourism").addEventListener("click", function(){get_data("city_tourism",
    document.getElementById('input_location').value, document.getElementById('input_place').value,
    document.getElementById('gradient').checked);});

document.getElementById("btn_kids").addEventListener("click", function(){get_data("kids",
    document.getElementById('input_location').value, document.getElementById('input_place').value,
    document.getElementById('gradient').checked);});
document.getElementById("btn_public_transport").addEventListener("click", function(){get_data("public_transport",
    document.getElementById('input_location').value, document.getElementById('input_place').value,
    document.getElementById('gradient').checked);});
document.getElementById("btn_find_in").addEventListener("click", function(){get_data("find_in",
    document.getElementById('input_location').value, document.getElementById('input_place').value,
    document.getElementById('gradient').checked);});

/* Request for the server */
function get_data(s_type, location, place, gradient){
    // console.log(s_type + " " +new Date().getTime())
    if (location == '') {
        location = 'Slovensko';
    }
    if (place == '' && s_type == 'find_in') {
        return;
    }
    
    if (s_type == 'find_in') {
        var params = "location="+location+"&place="+place;
    }
    else {
        var params = "location="+location+"&gradient="+gradient;
    }
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(xhttp.responseText);
            draw(response, s_type, gradient)
        }
    };
    xhttp.open("GET", "http://127.0.0.1:8099/"+s_type+"?"+params, true);
    xhttp.send(null);
    document.getElementById("loader").style.display = "block";
}

/* Pick color and draw shapes */
function draw(response, s_type, gradient) {
    var itemType;
    var itemCount;
    var itemColor;
    var responseLength = response.length;
    for (var i = 0; i < responseLength; i++) {
        itemType = (JSON.parse(response[i][0].st_asgeojson)).type;
        itemCount = response[i][0].count;

        if (gradient) {
            itemColor = get_color_gradient(i, responseLength);
        }
        else {
            itemColor = get_color(itemCount, s_type);
        }

        if (itemType == "LineString") {
            draw_line(JSON.parse(response[i][0].st_asgeojson), i, itemColor);
        }
        if (itemType == "Polygon") {
            draw_polygon(JSON.parse(response[i][0].st_asgeojson), i, itemColor);
        }
        if (itemType == "Point") {
            draw_point(JSON.parse(response[i][0].st_asgeojson), i);
        }
    }
    document.getElementById("loader").style.display = "none";
}

/* Generate gradient color */
function get_color_gradient(i, n) {
    var color_i = i/n*255;
    var g = 255-color_i;
    return('rgb('+color_i+', '+g+', 0)');
}

/* Generate color for classic shapes and the peaks */
function get_color(count, s_type) {
    if (s_type == 'city_life') {
        if (count >= 5) {
            return('#4ca892');
        }
    }
    if (s_type == 'city_sport') {
        if (count >= 3) {
            return('#4ca892');
        }
    }
    if (s_type == 'city_tourism') {
        if (count >= 3) {
            return('#4ca892');
        }
    }
    if (s_type == 'kids') {
        if (count >= 2) {
            return('#4ca892');
        }
    }
    if (s_type == 'public_transport') {
        if (count >= 3) {
            return('#4ca892');
        }
    }
    return '#f6ff43';
}

/* Draw line */
function draw_line(geojson, id, color) {
    var layer = {
        "id": "line-"+id+"-"+new Date().getTime(),
        "type": "line",
        "source": {
            "type": "geojson",
            "data": {
                "type": "Feature",
                "properties": {},
                "geometry": geojson
            }
        },
        "layout": {
            "line-join": "round",
            "line-cap": "round"
        },
        "paint": {
            "line-color": color,
            "line-width": 5,
            "line-opacity": 0.5
        }
    };

    layers.push(layer);
    map.addLayer(layer);
}

/* Draw polygon */
function draw_polygon(geojson, id, color) {
    var layer = {
        'id': "polygon-"+id+"-"+new Date().getTime(),
        'type': 'fill',
        'source': {
        'type': 'geojson',
            'data': {
            'type': 'Feature',
                'geometry': geojson
        }
    },
        'layout': {},
        'paint': {
        'fill-color': color,
            'fill-opacity': 0.5
        }
    };

    layers.push(layer);
    map.addLayer(layer);
}

/*Draw point */
function draw_point(geojson, id) {
    var layer = {
        'id': "point-"+id+"-"+new Date().getTime(),
        'type': 'symbol',
        'source': {
            'type': 'geojson',
            'data': {
                'type': 'Feature',
                'geometry': geojson,
                'properties': {
                    'icon': 'monument'
                }
            }
        },
        'layout': {
            'icon-image': '{icon}-15'
        }
    };

    layers.push(layer);
    map.addLayer(layer);
}
