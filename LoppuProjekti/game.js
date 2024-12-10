'use strict';

let playerName = '';
let visaValue = 0;
let trashWeight = 0;
let currentLocation = 'Albania';
let currentMarker;
let map;

function initializeMap(lat, lon) {
    map = L.map('map').setView([lat, lon], 8);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    currentMarker = L.marker([lat, lon]).addTo(map);
}

function updateGameInfo() {
    $('#name-output').text(playerName);
    $('#trash-output').text(`${trashWeight} kg Roskaa`);
    $('#location-output').text(currentLocation);
}


$('#startGameBtn').on('click', function() {
    playerName = localStorage.getItem('playerName');

    if (!playerName) {
        playerName = prompt("Syötä nimesi:");
        if (!playerName) return;
        localStorage.setItem('playerName', playerName);
    }

    $.get(`http://127.0.0.1:5000/aloitapeli/${playerName}`, function(data) {
        $('#name-output').text(data["Pelaajan Nimi"]);
        visaValue = 0;
        trashWeight = 0;
        currentLocation = 'Finland';
        updateGameInfo();
        $('#startGameBtn').hide();
        $('#travelBtn').show();
    });
});

$('#travelBtn').on('click', function() {
    let countryName = prompt("Syötä Maan nimi, johon haluat matkustaa:");

    if (!countryName) return;

    $.get(`http://127.0.0.1:5000/maantiedot/${countryName}`, function(data) {
        if (!data) {
            alert("Maa ei löytynyt. Yritä uudelleen.");
            return;
        }

        currentLocation = data.maanimi;
        visaValue += data.arvoesine;
        trashWeight += data.roska;

        currentMarker.setLatLng([data.lat, data.lon]);
        map.setView([data.lat, data.lon], 4);

        updateGameInfo();

        if (visaValue >= 100) {
            let travelHome = confirm("Visa-arvosi on 100. Haluatko matkustaa Suomeen?");
            if (travelHome) {
                $.get(`http://127.0.0.1:5000/paluusuomeen/${playerName}`, function() {
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
    }).fail(function() {
        alert("Virhe tiedon hakemisessa. Yritä myöhemmin.");
    });
});

$('#collectSouvenirBtn').on('click', function() {
    let collect = confirm("Haluatko kerätä matkamuiston?");
    if (collect) {
        $.get(`http://127.0.0.1:5000/lento?name=${playerName}&maa=${currentLocation}`, function(data) {
            visaValue += data.arvoesine;
            $('#souvenir-info').text(`Keräsit matkamuiston: ${data.arvoesine} arvosta!`);
            updateGameInfo();
            $('#collectSouvenirBtn').hide();
        }).fail(function() {
            alert("Virhe matkamuiston keräämisessä. Yritä myöhemmin.");
        });
    } else {
        $('#collectSouvenirBtn').hide();
    }
});

$('#endGameBtn').on('click', function() {
    $.get(`http://127.0.0.1:5000/lopetapeli/${playerName}`, function() {
        alert("Peli päättyi. Tiedot on tyhjennetty.");
        visaValue = 0;
        trashWeight = 0;
        currentLocation = 'Albania';
        currentMarker.setLatLng([41.3275, 19.8189]);
        map.setView([41.3275, 19.8189], 4);
        updateGameInfo();

        localStorage.removeItem('playerName');
    }).fail(function() {
        alert("Virhe pelin lopettamisessa. Yritä myöhemmin.");
    });
});

$(document).ready(function() {
    initializeMap(41.3275, 19.8189);

    playerName = localStorage.getItem('playerName');

    if (playerName) {
        $('#name-output').text(playerName);
    } else {
        $('#name-output').text("Tuntematon pelaaja");
    }

    updateGameInfo();
});
