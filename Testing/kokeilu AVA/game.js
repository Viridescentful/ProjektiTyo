'use strict';

let playerName = '';
let visaValue = 0;
let trashWeight = 0;
let currentLocation = 'Finland';
let currentMarker;
let map;


function initializeMap(lat, lon) {
    map = L.map('map').setView([lat, lon], 4);


    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    currentMarker = L.marker([lat, lon]).addTo(map);
}

function updateGameInfo() {
    $('#visa-value').text(`Visa-arvo: ${visaValue}`);
    $('#backpack-status').text(`Reppu: ${trashWeight} kg Roskaa`);
    $('#location').text(`Nykyinen sijainti: ${currentLocation}`);
}

$('#startGameBtn').on('click', function() {
    playerName = prompt("Syötä nimesi:");
    if (!playerName) return;

    $.get(`/aloitapeli/${playerName}`, function(data) {
        $('#player-name').text(`Pelaaja: ${data["Pelaajan Nimi"]}`);
        visaValue = 0;
        trashWeight = 0;
        currentLocation = 'Finland';
        updateGameInfo();
        $('#startGameBtn').hide();
        $('#travelBtn').show();
    });
});

$('#travelBtn').on('click', function() {
    let icaoCode = prompt("Syötä ICAO-koodi, johon haluat matkustaa:");

    if (!icaoCode) return;

    $.get(`/maantiedot/${icaoCode}`, function(data) {
        currentLocation = data.maanimi;
        visaValue += data.arvoesine;
        trashWeight += data.roska;

        currentMarker.setLatLng([data.lat, data.lon]);
        map.setView([data.lat, data.lon], 4);

        updateGameInfo();

        if (visaValue >= 100) {
            let travelHome = confirm("Visa-arvosi on 100. Haluatko matkustaa Suomeen?");
            if (travelHome) {
                $.get(`/paluusuomeen/${playerName}`, function() {
                    alert("Olet palannut Suomeen!");
                    visaValue = 0;
                    trashWeight = 0;
                    currentLocation = 'Finland';
                    currentMarker.setLatLng([60.1699, 24.9384]);
                    map.setView([60.1699, 24.9384], 4);
                    updateGameInfo();
                });
            }
        } else {
            $('#collectSouvenirBtn').show();
        }
    });
});

$('#collectSouvenirBtn').on('click', function() {
    let collect = confirm("Haluatko kerätä matkamuiston?");

    if (collect) {

        $.get(`/lento?name=${playerName}&maa=${currentLocation}`, function(data) {
            visaValue += data.arvoesine;
            $('#souvenir-info').text(`Keräsit matkamuiston: ${data.arvoesine} arvosta!`);
            updateGameInfo();
            $('#collectSouvenirBtn').hide();
        });
    } else {
        $('#collectSouvenirBtn').hide();
    }
});

// Lopeta peli
$('#endGameBtn').on('click', function() {
    $.get(`/lopetapeli/${playerName}`, function() {
        alert("Peli päättyi. Tiedot on tyhjennetty.");
        visaValue = 0;
        trashWeight = 0;
        currentLocation = 'Finland';
        currentMarker.setLatLng([60.1699, 24.9384]); // Suomi
        map.setView([60.1699, 24.9384], 4);
        updateGameInfo();
    });
});

// Alustetaan kartta ja pelitiedot
$(document).ready(function() {
    // Muutetaan aloituspaikka Tiranaksi, Albania
    initializeMap(41.3275, 19.8189); // Tirana, Albania
    updateGameInfo();
});
