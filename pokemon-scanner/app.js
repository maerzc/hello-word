// Pokemon Karten Scanner App
// Verwendet Tesseract.js für OCR und Pokemon TCG API für Preise

class PokemonCardScanner {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');

        this.captureBtn = document.getElementById('captureBtn');
        this.switchCameraBtn = document.getElementById('switchCameraBtn');
        this.newScanBtn = document.getElementById('newScanBtn');
        this.searchBtn = document.getElementById('searchBtn');
        this.searchInput = document.getElementById('searchInput');

        this.loadingSection = document.getElementById('loadingSection');
        this.loadingText = document.getElementById('loadingText');
        this.progressFill = document.getElementById('progressFill');
        this.resultSection = document.getElementById('resultSection');
        this.searchResults = document.getElementById('searchResults');

        this.currentStream = null;
        this.facingMode = 'environment'; // Rückkamera als Standard
        this.tesseractWorker = null;

        this.init();
    }

    async init() {
        this.bindEvents();
        await this.startCamera();
        await this.initTesseract();
    }

    bindEvents() {
        this.captureBtn.addEventListener('click', () => this.captureAndAnalyze());
        this.switchCameraBtn.addEventListener('click', () => this.switchCamera());
        this.newScanBtn.addEventListener('click', () => this.resetToCamera());
        this.searchBtn.addEventListener('click', () => this.manualSearch());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.manualSearch();
        });
    }

    async startCamera() {
        try {
            if (this.currentStream) {
                this.currentStream.getTracks().forEach(track => track.stop());
            }

            const constraints = {
                video: {
                    facingMode: this.facingMode,
                    width: { ideal: 1280 },
                    height: { ideal: 960 }
                }
            };

            this.currentStream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.currentStream;

        } catch (error) {
            console.error('Kamera-Fehler:', error);
            alert('Kamera konnte nicht gestartet werden. Bitte erlaube den Kamera-Zugriff.');
        }
    }

    async switchCamera() {
        this.facingMode = this.facingMode === 'environment' ? 'user' : 'environment';
        await this.startCamera();
    }

    async initTesseract() {
        try {
            this.updateLoading('OCR wird vorbereitet...', 10);
            // Tesseract Worker wird bei Bedarf initialisiert
        } catch (error) {
            console.error('Tesseract Init Fehler:', error);
        }
    }

    async captureAndAnalyze() {
        // Bild aufnehmen
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        this.ctx.drawImage(this.video, 0, 0);

        const imageData = this.canvas.toDataURL('image/jpeg', 0.9);

        // UI Update
        this.showLoading();

        try {
            // OCR durchführen
            this.updateLoading('Lese Text von der Karte...', 20);
            const ocrResult = await this.performOCR(imageData);

            // Kartenname extrahieren
            this.updateLoading('Analysiere erkannten Text...', 50);
            const cardName = this.extractCardName(ocrResult);

            if (!cardName) {
                throw new Error('Kartenname konnte nicht erkannt werden. Versuche es erneut oder nutze die manuelle Suche.');
            }

            // Karte in API suchen
            this.updateLoading(`Suche "${cardName}" in Datenbank...`, 70);
            const cardData = await this.searchPokemonCard(cardName);

            if (!cardData) {
                throw new Error(`Keine Karte gefunden für: ${cardName}. Versuche die manuelle Suche.`);
            }

            // Ergebnis anzeigen
            this.updateLoading('Lade Preisinformationen...', 90);
            this.displayResult(cardData);

        } catch (error) {
            console.error('Analyse-Fehler:', error);
            alert(error.message || 'Fehler bei der Analyse. Bitte erneut versuchen.');
            this.hideLoading();
        }
    }

    async performOCR(imageData) {
        try {
            const result = await Tesseract.recognize(imageData, 'eng', {
                logger: (m) => {
                    if (m.status === 'recognizing text') {
                        const progress = 20 + (m.progress * 30);
                        this.updateLoading('Lese Text...', progress);
                    }
                }
            });
            return result.data.text;
        } catch (error) {
            console.error('OCR Fehler:', error);
            throw new Error('Texterkennung fehlgeschlagen');
        }
    }

    extractCardName(ocrText) {
        // OCR Text bereinigen und analysieren
        const lines = ocrText.split('\n').map(line => line.trim()).filter(line => line.length > 0);

        // Pokemon-Namen sind oft in den ersten Zeilen
        // Filtere typische Pokémon-Kartentexte
        const pokemonPatterns = [
            /^[A-Z][a-z]+$/,  // Einzelnes Wort mit Großbuchstabe am Anfang
            /^[A-Z][a-z]+ [A-Z][a-z]+$/,  // Zwei Wörter
            /^[A-Z][a-z]+-?[A-Z]?[a-z]*$/,  // Mit Bindestrich
        ];

        // Bekannte Pokemon-Namen für bessere Erkennung
        const knownPokemon = [
            'Pikachu', 'Charizard', 'Glurak', 'Blastoise', 'Turtok', 'Venusaur', 'Bisaflor',
            'Mewtwo', 'Mewtu', 'Mew', 'Gengar', 'Alakazam', 'Machamp', 'Machomei',
            'Dragonite', 'Dragoran', 'Gyarados', 'Garados', 'Lapras', 'Snorlax', 'Relaxo',
            'Articuno', 'Arktos', 'Zapdos', 'Moltres', 'Lavados', 'Eevee', 'Evoli',
            'Vaporeon', 'Aquana', 'Jolteon', 'Blitza', 'Flareon', 'Flamara',
            'Bulbasaur', 'Bisasam', 'Charmander', 'Glumanda', 'Squirtle', 'Schiggy',
            'Lugia', 'Ho-Oh', 'Celebi', 'Rayquaza', 'Kyogre', 'Groudon',
            'Lucario', 'Garchomp', 'Knakrack', 'Umbreon', 'Nachtara', 'Espeon', 'Psiana'
        ];

        // Suche nach bekannten Pokemon-Namen im Text
        const textLower = ocrText.toLowerCase();
        for (const pokemon of knownPokemon) {
            if (textLower.includes(pokemon.toLowerCase())) {
                return pokemon;
            }
        }

        // Fallback: Ersten sinnvollen Namen nehmen
        for (const line of lines) {
            // Ignoriere HP, Energie-Typen und Nummern
            if (line.match(/^\d+/) || line.match(/HP/i) || line.length < 3 || line.length > 25) {
                continue;
            }

            // Prüfe auf Pokemon-ähnliche Namen
            for (const pattern of pokemonPatterns) {
                if (pattern.test(line)) {
                    return line;
                }
            }
        }

        // Letzter Versuch: Erste Zeile mit mehr als 3 Buchstaben
        for (const line of lines) {
            if (line.length >= 3 && line.length <= 20 && /^[A-Za-z]/.test(line)) {
                return line.split(' ')[0]; // Nur erstes Wort
            }
        }

        return null;
    }

    async searchPokemonCard(query) {
        try {
            // Pokemon TCG API verwenden
            const response = await fetch(
                `https://api.pokemontcg.io/v2/cards?q=name:"${encodeURIComponent(query)}"&pageSize=1`,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                throw new Error('API-Anfrage fehlgeschlagen');
            }

            const data = await response.json();

            if (data.data && data.data.length > 0) {
                return data.data[0];
            }

            // Fallback: Wildcard-Suche
            const wildcardResponse = await fetch(
                `https://api.pokemontcg.io/v2/cards?q=name:${encodeURIComponent(query)}*&pageSize=1`,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            const wildcardData = await wildcardResponse.json();

            if (wildcardData.data && wildcardData.data.length > 0) {
                return wildcardData.data[0];
            }

            return null;

        } catch (error) {
            console.error('API-Fehler:', error);
            throw new Error('Fehler bei der Kartensuche');
        }
    }

    async manualSearch() {
        const query = this.searchInput.value.trim();

        if (!query) {
            alert('Bitte gib einen Kartennamen ein.');
            return;
        }

        this.searchResults.classList.remove('hidden');
        this.searchResults.innerHTML = '<div class="loading-section"><div class="spinner"></div><p>Suche...</p></div>';

        try {
            const response = await fetch(
                `https://api.pokemontcg.io/v2/cards?q=name:"${encodeURIComponent(query)}"&pageSize=10`,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            const data = await response.json();

            if (data.data && data.data.length > 0) {
                this.displaySearchResults(data.data);
            } else {
                // Wildcard-Suche
                const wildcardResponse = await fetch(
                    `https://api.pokemontcg.io/v2/cards?q=name:${encodeURIComponent(query)}*&pageSize=10`
                );
                const wildcardData = await wildcardResponse.json();

                if (wildcardData.data && wildcardData.data.length > 0) {
                    this.displaySearchResults(wildcardData.data);
                } else {
                    this.searchResults.innerHTML = '<p style="text-align: center; color: var(--text-muted);">Keine Karten gefunden.</p>';
                }
            }

        } catch (error) {
            console.error('Suchfehler:', error);
            this.searchResults.innerHTML = '<p style="text-align: center; color: var(--accent-color);">Fehler bei der Suche.</p>';
        }
    }

    displaySearchResults(cards) {
        this.searchResults.innerHTML = cards.map(card => `
            <div class="search-result-item" data-card-id="${card.id}">
                <img src="${card.images?.small || ''}" alt="${card.name}">
                <div class="search-result-info">
                    <h4>${card.name}</h4>
                    <p>${card.set?.name || 'Unbekanntes Set'} • ${card.rarity || 'Unbekannt'}</p>
                </div>
            </div>
        `).join('');

        // Click-Events für Suchergebnisse
        this.searchResults.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', async () => {
                const cardId = item.dataset.cardId;
                const card = cards.find(c => c.id === cardId);
                if (card) {
                    this.displayResult(card);
                    this.searchResults.classList.add('hidden');
                }
            });
        });
    }

    displayResult(card) {
        // Kamera ausblenden
        document.querySelector('.camera-section').classList.add('hidden');
        document.querySelector('.manual-search').classList.add('hidden');
        this.hideLoading();

        // Ergebnis anzeigen
        this.resultSection.classList.remove('hidden');

        // Karteninfos
        document.getElementById('cardName').textContent = card.name;
        document.getElementById('cardSet').textContent = card.set?.name || 'Unbekanntes Set';

        // Kartenbild
        const cardImage = document.getElementById('cardImage');
        const cardImageContainer = document.getElementById('cardImageContainer');
        if (card.images?.large || card.images?.small) {
            cardImage.src = card.images.large || card.images.small;
            cardImageContainer.classList.remove('hidden');
        } else {
            cardImageContainer.classList.add('hidden');
        }

        // Preise
        const prices = card.tcgplayer?.prices || {};

        document.getElementById('priceNormal').textContent = this.formatPrice(prices.normal?.market || prices.normal?.mid);
        document.getElementById('priceHolo').textContent = this.formatPrice(prices.holofoil?.market || prices.holofoil?.mid);
        document.getElementById('priceReverse').textContent = this.formatPrice(prices.reverseHolofoil?.market || prices.reverseHolofoil?.mid);
        document.getElementById('priceFirst').textContent = this.formatPrice(prices['1stEditionHolofoil']?.market || prices['1stEdition']?.market);

        // Details
        document.getElementById('cardRarity').textContent = card.rarity || '-';
        document.getElementById('cardNumber').textContent = card.number ? `${card.number}/${card.set?.printedTotal || '?'}` : '-';
        document.getElementById('cardArtist').textContent = card.artist || '-';
    }

    formatPrice(price) {
        if (!price) return '-';
        return `$${price.toFixed(2)}`;
    }

    resetToCamera() {
        this.resultSection.classList.add('hidden');
        document.querySelector('.camera-section').classList.remove('hidden');
        document.querySelector('.manual-search').classList.remove('hidden');
        this.searchResults.classList.add('hidden');
        this.searchInput.value = '';
    }

    showLoading() {
        document.querySelector('.camera-section').classList.add('hidden');
        document.querySelector('.manual-search').classList.add('hidden');
        this.loadingSection.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingSection.classList.add('hidden');
    }

    updateLoading(text, progress) {
        this.loadingText.textContent = text;
        this.progressFill.style.width = `${progress}%`;
    }
}

// App starten wenn DOM geladen
document.addEventListener('DOMContentLoaded', () => {
    new PokemonCardScanner();
});
