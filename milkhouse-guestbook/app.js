// ===== NAVIGATION =====
function go(id, btn) {
    document.querySelectorAll('.sec').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.bnav button').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    if (btn) btn.classList.add('active');
    window.scrollTo({top: 0, behavior: 'smooth'});
    if (id === 'karte') setTimeout(() => map.invalidateSize(), 100);
}

// ===== UTILS =====
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function ld(k, fb) { try { return JSON.parse(localStorage.getItem('mh_' + k)) || fb; } catch { return fb; } }
function sv(k, d) { localStorage.setItem('mh_' + k, JSON.stringify(d)); }

// ===== MAP =====
const POI = [
    {cat:'home', name:'Milk House', addr:'Lützestraße 90b, 71384 Weinstadt-Schnait', lat:48.8078, lng:9.3618, hours:''},
    {cat:'parking', name:'Parkplatz Kelter Schnait', addr:'Lützestraße, Weinstadt-Schnait', lat:48.8082, lng:9.3622, hours:''},
    {cat:'parking', name:'Parkplatz Silcherstraße', addr:'Silcherstraße, Weinstadt-Schnait', lat:48.8093, lng:9.3598, hours:''},
    {cat:'parking', name:'Parkplatz Rathaus Schnait', addr:'Beim Rathaus, Weinstadt-Schnait', lat:48.8089, lng:9.3644, hours:''},
    {cat:'restaurant', name:'Krone Schnait', addr:'Lützestraße 97, 71384 Weinstadt-Schnait', lat:48.8075, lng:9.3612, hours:''},
    {cat:'restaurant', name:'Gasthof Lamm', addr:'Silcherstraße 75, 71384 Weinstadt-Schnait', lat:48.8090, lng:9.3593, hours:''},
    {cat:'restaurant', name:'Restaurant Weinstube Anker', addr:'Weinstraße 28, 71384 Weinstadt-Schnait', lat:48.8088, lng:9.3652, hours:''},
    {cat:'restaurant', name:'Gasthof Adler', addr:'Forststraße 12, 71384 Weinstadt-Baach', lat:48.7985, lng:9.3540, hours:''},
    {cat:'restaurant', name:'Gasthaus Rössle', addr:'Forststraße 6, 71384 Weinstadt-Baach', lat:48.7988, lng:9.3533, hours:''},
    {cat:'restaurant', name:'Baacher Forellen', addr:'Brühlweg 9, 71384 Weinstadt-Baach', lat:48.7978, lng:9.3518, hours:''},
    {cat:'restaurant', name:'Reichmanns Cucina', addr:'Marktstraße 36, 71384 Weinstadt-Baach', lat:48.7992, lng:9.3545, hours:''},
    {cat:'restaurant', name:'Kostbar Restaurant', addr:'Bruckwiesenstraße 1, 71384 Weinstadt-Großheppach', lat:48.8130, lng:9.3750, hours:''},
    {cat:'restaurant', name:'Zum Gretle', addr:'Hindenburgstraße 33, 71384 Weinstadt-Strümpfelbach', lat:48.8145, lng:9.3878, hours:''},
    // Nahbereich
    {cat:'shopping', name:'Dorfladen Schnait', addr:'Silcherstraße 40, 71384 Weinstadt-Schnait', lat:48.8092, lng:9.3600, hours:'Mo-Fr 7:00-12:30 / 16:30-18:30, Sa 7:00-12:30'},
    {cat:'shopping', name:'Rewe Beutelsbach', addr:'Daimlerstraße 9, 71384 Weinstadt-Beutelsbach', lat:48.8115, lng:9.3720, hours:'Mo-Sa 7:00-22:00'},
    {cat:'shopping', name:'Edeka Großheppach', addr:'Benzstraße 9, 71384 Weinstadt', lat:48.8140, lng:9.3755, hours:'Mo-Sa 8:00-21:00'},
    {cat:'shopping', name:'Lidl Endersbach', addr:'Großheppacher Straße 70, 71384 Weinstadt-Endersbach', lat:48.8175, lng:9.3700, hours:'Mo-Sa 7:00-21:00'},
    {cat:'shopping', name:'Aldi Endersbach', addr:'Großheppacher Straße 60/1, 71384 Weinstadt', lat:48.8178, lng:9.3693, hours:'Mo-Sa 7:00-21:00'},
    // Erweiterter Umkreis
    {cat:'shopping', name:'Rewe Waiblingen', addr:'Devizesstraße 4, 71332 Waiblingen', lat:48.8295, lng:9.3159, hours:'Mo-Sa 7:00-22:00'},
    {cat:'shopping', name:'Edeka Waiblingen', addr:'Fronackerstraße 55, 71332 Waiblingen', lat:48.8316, lng:9.3187, hours:'Mo-Sa 7:00-21:00'},
    {cat:'shopping', name:'Kaufland Waiblingen', addr:'Dammstraße 2, 71332 Waiblingen', lat:48.8340, lng:9.3168, hours:'Mo-Sa 7:00-22:00'},
    {cat:'shopping', name:'Rewe Fellbach', addr:'Stuttgarter Straße 100, 70734 Fellbach', lat:48.8100, lng:9.2760, hours:'Mo-Sa 7:00-22:00'},
    {cat:'shopping', name:'Edeka Fellbach', addr:'Bahnhofstraße 28, 70734 Fellbach', lat:48.8118, lng:9.2768, hours:'Mo-Sa 7:30-21:00'},
    {cat:'shopping', name:'Kaufland Fellbach', addr:'Höhenstraße 40, 70736 Fellbach', lat:48.8230, lng:9.2820, hours:'Mo-Sa 7:00-22:00'},
    {cat:'shopping', name:'Rewe Schorndorf', addr:'Gmünder Straße 2, 73614 Schorndorf', lat:48.8035, lng:9.5290, hours:'Mo-Sa 7:00-22:00'},
    {cat:'shopping', name:'Edeka Schorndorf', addr:'Heinkelstraße 20, 73614 Schorndorf', lat:48.7990, lng:9.5260, hours:'Mo-Sa 7:00-21:00'},
    {cat:'shopping', name:'Rewe Kernen', addr:'Waiblinger Straße 84, 71394 Kernen', lat:48.8150, lng:9.3230, hours:'Mo-Sa 7:00-22:00'},
    {cat:'shopping', name:'Edeka Korb', addr:'Seestraße 6, 71404 Korb', lat:48.8390, lng:9.3610, hours:'Mo-Sa 7:00-21:00'},
    {cat:'shopping', name:'Rewe Winnenden', addr:'Waiblinger Straße 63, 71364 Winnenden', lat:48.8760, lng:9.3970, hours:'Mo-Sa 7:00-22:00'},
    {cat:'shopping', name:'Edeka Esslingen', addr:'Kollwitzstraße 1, 73728 Esslingen', lat:48.7360, lng:9.3100, hours:'Mo-Sa 7:00-21:00'},
];

const CAT_CONFIG = {
    home: {label:'Unterkunft', color:'#1a1a1a', emoji:'🏠'},
    parking: {label:'Parkplätze', color:'#1976d2', emoji:'🅿️'},
    restaurant: {label:'Restaurants', color:'#e65100', emoji:'🍽️'},
    shopping: {label:'Einkaufen', color:'#2e7d32', emoji:'🛒'},
};

const map = L.map('map').setView([48.8085, 9.3630], 14);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap', maxZoom: 19
}).addTo(map);

let activeFilters = new Set(Object.keys(CAT_CONFIG));
let markers = [];

function makeIcon(color, emoji) {
    return L.divIcon({
        className: '',
        html: '<div style="background:'+color+';width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;border:2.5px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);">'+emoji+'</div>',
        iconSize: [34, 34], iconAnchor: [17, 17], popupAnchor: [0, -20]
    });
}

function renderMarkers() {
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    POI.forEach(p => {
        if (!activeFilters.has(p.cat)) return;
        const cfg = CAT_CONFIG[p.cat];
        const m = L.marker([p.lat, p.lng], {icon: makeIcon(cfg.color, cfg.emoji)}).addTo(map);
        let popup = '<div class="popup-title">' + p.name + '</div><div class="popup-addr">' + p.addr + '</div>';
        if (p.hours) popup += '<div class="popup-hours">🕐 ' + p.hours + '</div>';
        popup += '<a class="popup-nav" href="https://www.google.com/maps/dir/?api=1&destination='+p.lat+','+p.lng+'" target="_blank">🧭 Navigation</a>';
        m.bindPopup(popup);
        markers.push(m);
    });
}

function renderFilters() {
    document.getElementById('map-filters').innerHTML = Object.entries(CAT_CONFIG).map(([key, cfg]) =>
        '<button class="mf-btn'+(activeFilters.has(key)?' active':'')+'" onclick="toggleFilter(\''+key+'\',this)">'+cfg.emoji+' '+cfg.label+'</button>'
    ).join('');
}

function toggleFilter(cat, btn) {
    if (activeFilters.has(cat)) activeFilters.delete(cat); else activeFilters.add(cat);
    btn.classList.toggle('active');
    renderMarkers();
}

renderFilters();
renderMarkers();

// ===== GALLERY =====
let galleryIdx = 0;
const slides = document.querySelectorAll('.gallery-slide');
function updateGallery() {
    document.getElementById('gallery-track').style.transform = 'translateX(-' + (galleryIdx * 100) + '%)';
    document.querySelectorAll('.gallery-dot').forEach((d, i) => d.classList.toggle('active', i === galleryIdx));
}
function galleryNext() { galleryIdx = (galleryIdx + 1) % slides.length; updateGallery(); }
function galleryPrev() { galleryIdx = (galleryIdx - 1 + slides.length) % slides.length; updateGallery(); }
function galleryGo(i) { galleryIdx = i; updateGallery(); }
// Dots
(function() {
    const dots = document.getElementById('gallery-dots');
    for (let i = 0; i < slides.length; i++) {
        dots.innerHTML += '<button class="gallery-dot'+(i===0?' active':'')+'" onclick="galleryGo('+i+')"></button>';
    }
})();
// Touch swipe
let touchX = 0;
document.getElementById('gallery-slider').addEventListener('touchstart', e => { touchX = e.touches[0].clientX; });
document.getElementById('gallery-slider').addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 50) { dx < 0 ? galleryNext() : galleryPrev(); }
});

// ===== PLANNER =====
let days = ld('plan', []);
function renderPlan() {
    const c = document.getElementById('planner-days');
    if (!days.length) {
        c.innerHTML = '<div class="empty"><div class="ei">📅</div><p>Noch keine Tage geplant.<br>Füge euren ersten Tag hinzu!</p></div>';
        return;
    }
    c.innerHTML = days.map((d, di) => {
        const done = d.items.filter(i => i.done).length;
        const total = d.items.length;
        return '<div class="day-card"><div class="day-hdr" onclick="togD('+di+')"><span>'+esc(d.label)+'</span><span><span class="dd">'+done+'/'+total+'</span> <button class="dbtn" onclick="event.stopPropagation();delD('+di+')">✕</button></span></div>' +
        '<div class="day-body'+(d.open?' open':'')+'">'+
        d.items.map((it,ii) => '<div class="pi"><input type="checkbox" '+(it.done?'checked':'')+' onchange="togI('+di+','+ii+')"><span class="pt'+(it.done?' done':'')+'">'+esc(it.text)+'</span><button class="dbtn" onclick="delI('+di+','+ii+')">✕</button></div>').join('') +
        '<div class="add-row"><input type="text" placeholder="Aktivität..." id="pi-'+di+'" onkeydown="if(event.key===\'Enter\')addI('+di+')"><button class="voice-btn" onclick="voiceAddItem('+di+')" title="Spracheingabe">🎙️</button><button class="btn btn-sm" onclick="addI('+di+')">+</button></div></div></div>';
    }).join('');
}
function addDay() { const n = days.length + 1; days.push({label:'Tag '+n, items:[], open:true}); days.forEach((d,i) => { if (i < days.length-1) d.open = false; }); sv('plan',days); renderPlan(); }
function delD(i) { if (confirm('Tag löschen?')) { days.splice(i,1); sv('plan',days); renderPlan(); } }
function togD(i) { days[i].open = !days[i].open; sv('plan',days); renderPlan(); }
function addI(di) { const inp = document.getElementById('pi-'+di); const t = inp.value.trim(); if (!t) return; days[di].items.push({text:t,done:false}); sv('plan',days); renderPlan(); setTimeout(() => { const n = document.getElementById('pi-'+di); if (n) n.focus(); }, 50); }
function togI(di,ii) { days[di].items[ii].done = !days[di].items[ii].done; sv('plan',days); renderPlan(); }
function delI(di,ii) { days[di].items.splice(ii,1); sv('plan',days); renderPlan(); }

// ===== VOICE INPUT =====
let voiceRecognition = null;
function getRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { alert('Spracherkennung wird von deinem Browser nicht unterstützt. Probiere Chrome.'); return null; }
    const r = new SR();
    r.lang = 'de-DE';
    r.continuous = false;
    r.interimResults = false;
    return r;
}

function voiceAddItem(dayIdx) {
    const r = getRecognition();
    if (!r) return;
    const btns = document.querySelectorAll('.voice-btn');
    r.onstart = () => { btns.forEach(b => b.classList.add('recording')); };
    r.onend = () => { btns.forEach(b => b.classList.remove('recording')); };
    r.onresult = (e) => {
        const text = e.results[0][0].transcript;
        if (text.trim()) {
            days[dayIdx].items.push({text: text.trim(), done: false});
            sv('plan', days);
            renderPlan();
        }
    };
    r.onerror = () => { btns.forEach(b => b.classList.remove('recording')); };
    r.start();
}

let planVoiceActive = false;
function togglePlanVoice() {
    const r = getRecognition();
    if (!r) return;
    const btn = document.getElementById('plan-voice-btn');
    const status = document.getElementById('voice-status');

    if (planVoiceActive && voiceRecognition) {
        voiceRecognition.stop();
        planVoiceActive = false;
        btn.classList.remove('recording');
        status.style.display = 'none';
        return;
    }

    r.continuous = true;
    r.interimResults = true;
    planVoiceActive = true;
    btn.classList.add('recording');
    status.style.display = 'block';
    status.textContent = '🎙️ Sprich jetzt... z.B. "Tag 1: Wandern gehen, Weingut besuchen"';

    r.onresult = (e) => {
        let final = '';
        for (let i = e.resultIndex; i < e.results.length; i++) {
            if (e.results[i].isFinal) final += e.results[i][0].transcript;
        }
        if (final.trim()) {
            parsePlanVoice(final.trim());
            status.textContent = '✅ "' + final.trim() + '" — Sprich weiter oder tippe Stop';
        }
    };
    r.onend = () => {
        if (planVoiceActive) r.start(); // restart if still active
        else { btn.classList.remove('recording'); status.style.display = 'none'; }
    };
    r.onerror = () => { planVoiceActive = false; btn.classList.remove('recording'); status.style.display = 'none'; };
    voiceRecognition = r;
    r.start();
}

function parsePlanVoice(text) {
    // Try to parse "Tag X: activity1, activity2"
    const tagMatch = text.match(/tag\s*(\d+)\s*[:\.]\s*(.*)/i);
    if (tagMatch) {
        const dayNum = parseInt(tagMatch[1]);
        const activities = tagMatch[2].split(/[,\.und]+/).map(s => s.trim()).filter(s => s);
        while (days.length < dayNum) addDay();
        activities.forEach(a => { if (a) days[dayNum-1].items.push({text:a,done:false}); });
        sv('plan', days); renderPlan();
    } else {
        // Add to last day or create first
        if (!days.length) addDay();
        const lastDay = days[days.length - 1];
        const activities = text.split(/[,\.]+/).map(s => s.trim()).filter(s => s);
        activities.forEach(a => { if (a) lastDay.items.push({text:a,done:false}); });
        sv('plan', days); renderPlan();
    }
}

// ===== JOURNAL WITH MEDIA & GPS =====
let pendingMedia = [];
let currentGPS = null;

function capturePhoto() { document.getElementById('cam-photo').click(); }
function captureVideo() { document.getElementById('cam-video').click(); }
function pickFile() { document.getElementById('cam-file').click(); }

['cam-photo', 'cam-video', 'cam-file'].forEach(id => {
    document.getElementById(id).addEventListener('change', function(e) {
        Array.from(e.target.files).forEach(f => {
            const r = new FileReader();
            r.onload = ev => {
                const type = f.type.startsWith('video') ? 'video' : 'image';
                pendingMedia.push({data: ev.target.result, type: type});
                renderMediaPreview();
            };
            r.readAsDataURL(f);
        });
        e.target.value = '';
    });
});

function renderMediaPreview() {
    const pv = document.getElementById('media-preview');
    pv.innerHTML = pendingMedia.map((m, i) => {
        if (m.type === 'video') {
            return '<div style="position:relative"><video src="'+m.data+'" style="width:60px;height:60px;object-fit:cover;border-radius:8px"></video><button onclick="pendingMedia.splice('+i+',1);renderMediaPreview()" style="position:absolute;top:-4px;right:-4px;width:18px;height:18px;border-radius:50%;background:#c62828;color:white;border:none;font-size:10px;cursor:pointer">✕</button></div>';
        }
        return '<div style="position:relative"><img src="'+m.data+'" style="width:60px;height:60px;object-fit:cover;border-radius:8px"><button onclick="pendingMedia.splice('+i+',1);renderMediaPreview()" style="position:absolute;top:-4px;right:-4px;width:18px;height:18px;border-radius:50%;background:#c62828;color:white;border:none;font-size:10px;cursor:pointer">✕</button></div>';
    }).join('');
    // Get GPS
    if (pendingMedia.length > 0 && !currentGPS) getGPS();
}

function getGPS() {
    const status = document.getElementById('gps-status');
    if (!navigator.geolocation) { status.textContent = 'GPS nicht verfügbar'; return; }
    status.textContent = '📍 Standort wird ermittelt...';
    navigator.geolocation.getCurrentPosition(
        pos => { currentGPS = {lat: pos.coords.latitude, lng: pos.coords.longitude}; status.textContent = '📍 Standort erfasst'; },
        () => { status.textContent = '📍 Standort konnte nicht ermittelt werden'; },
        {enableHighAccuracy: true, timeout: 10000}
    );
}

let jEntries = ld('journal', []);
function addJournalEntry() {
    const t = document.getElementById('journal-input').value.trim();
    if (!t && !pendingMedia.length) return;
    jEntries.unshift({
        date: new Date().toLocaleString('de-DE', {weekday:'long', day:'numeric', month:'long', year:'numeric', hour:'2-digit', minute:'2-digit'}),
        text: t,
        media: pendingMedia.slice(0, 10),
        gps: currentGPS
    });
    sv('journal', jEntries);
    document.getElementById('journal-input').value = '';
    document.getElementById('media-preview').innerHTML = '';
    document.getElementById('gps-status').textContent = '';
    pendingMedia = [];
    currentGPS = null;
    renderJournal();
}

function delJE(i) { if (confirm('Eintrag löschen?')) { jEntries.splice(i,1); sv('journal',jEntries); renderJournal(); } }

function renderJournal() {
    const c = document.getElementById('journal-entries');
    if (!jEntries.length) {
        c.innerHTML = '<div class="empty"><div class="ei">📝</div><p>Noch keine Einträge.<br>Haltet eure Erlebnisse fest!</p></div>';
        return;
    }
    c.innerHTML = jEntries.map((e, i) => {
        let html = '<div class="je"><div style="display:flex;justify-content:space-between"><div class="je-date">' + esc(e.date) + '</div><button class="dbtn" onclick="delJE('+i+')">✕</button></div>';
        if (e.text) html += '<div class="je-text">' + esc(e.text) + '</div>';
        if (e.gps) html += '<div class="je-loc">📍 <a href="https://www.google.com/maps?q='+e.gps.lat+','+e.gps.lng+'" target="_blank" style="color:inherit;text-decoration:underline">Standort anzeigen</a></div>';
        if (e.media && e.media.length) {
            html += '<div class="je-media">';
            e.media.forEach(m => {
                if (m.type === 'video') html += '<video src="'+m.data+'" onclick="openLightbox(this.outerHTML.replace(\'width:100px;height:100px;object-fit:cover;\',\'width:auto;height:auto;\'))" style="width:100px;height:100px;object-fit:cover;border-radius:10px;cursor:pointer"></video>';
                else html += '<img src="'+m.data+'" onclick="openLightbox(\'<img src=&quot;'+m.data+'&quot;>\')" style="cursor:pointer">';
            });
            // Compat: old entries with .photos
            if (e.photos) e.photos.forEach(p => { html += '<img src="'+p+'" onclick="openLightbox(\'<img src=&quot;'+p+'&quot;>\')">'; });
            html += '</div>';
        } else if (e.photos && e.photos.length) {
            html += '<div class="je-media">';
            e.photos.forEach(p => { html += '<img src="'+p+'" onclick="openLightbox(\'<img src=&quot;'+p+'&quot;>\')">'; });
            html += '</div>';
        }
        html += '</div>';
        return html;
    }).join('');
}

// Lightbox
function openLightbox(content) {
    const lb = document.getElementById('lightbox');
    document.getElementById('lightbox-content').innerHTML = content;
    lb.classList.add('show');
    event.stopPropagation();
}
function closeLightbox() { document.getElementById('lightbox').classList.remove('show'); }

// ===== LISTS =====
function showList(id, btn) {
    document.querySelectorAll('.list-sec').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('#listen .chip').forEach(c => c.classList.remove('active'));
    document.getElementById('list-' + id).classList.add('active');
    if (btn) btn.classList.add('active');
}
// Add active style for list-sec
document.querySelectorAll('.list-sec').forEach(s => { if (!s.classList.contains('active')) s.style.display = 'none'; });
// Fix display
const listObserver = new MutationObserver(() => {
    document.querySelectorAll('.list-sec').forEach(s => { s.style.display = s.classList.contains('active') ? 'block' : 'none'; });
});
document.querySelectorAll('.list-sec').forEach(s => listObserver.observe(s, {attributes:true, attributeFilter:['class']}));

// Packing list
let packItems = ld('pack', []);
const PACK_PRESETS = {
    kleidung: ['T-Shirts','Hosen','Unterwäsche','Socken','Jacke','Schlafanzug','Badehose/Bikini','Schuhe'],
    hygiene: ['Zahnbürste','Zahnpasta','Shampoo','Duschgel','Deo','Sonnencreme','Handtücher'],
    tech: ['Ladekabel','Powerbank','Kopfhörer','Kamera','Adapter'],
    kinder: ['Windeln','Feuchttücher','Spielzeug','Malbuch','Snacks','Trinkflasche','Kuscheltier'],
};
function renderPack() {
    const c = document.getElementById('pack-items');
    if (!packItems.length) { c.innerHTML = '<div class="empty"><div class="ei">🧳</div><p>Noch nichts auf der Packliste.<br>Füge Gegenstände hinzu!</p></div>'; return; }
    const done = packItems.filter(i => i.done).length;
    c.innerHTML = '<div style="font-size:0.8rem;color:var(--text-lighter);margin-bottom:0.5rem">'+done+' / '+packItems.length+' gepackt</div>' +
        packItems.map((it, i) => '<div class="list-item"><input type="checkbox" '+(it.done?'checked':'')+' onchange="togPack('+i+')"><span class="lt'+(it.done?' done':'')+'">'+esc(it.text)+'</span><button class="dbtn" onclick="delPack('+i+')">✕</button></div>').join('');
}
function addPackItem() { const inp = document.getElementById('pack-input'); const t = inp.value.trim(); if (!t) return; packItems.push({text:t,done:false}); sv('pack',packItems); renderPack(); inp.value=''; inp.focus(); }
function togPack(i) { packItems[i].done = !packItems[i].done; sv('pack',packItems); renderPack(); }
function delPack(i) { packItems.splice(i,1); sv('pack',packItems); renderPack(); }
function addPackPreset(key) { PACK_PRESETS[key].forEach(t => { if (!packItems.some(p => p.text === t)) packItems.push({text:t,done:false}); }); sv('pack',packItems); renderPack(); }

// Shopping list
let shopItems = ld('shop', []);
function renderShop() {
    const c = document.getElementById('shop-items');
    if (!shopItems.length) { c.innerHTML = '<div class="empty"><div class="ei">🛒</div><p>Einkaufsliste ist leer.</p></div>'; return; }
    c.innerHTML = shopItems.map((it, i) => '<div class="list-item"><input type="checkbox" '+(it.done?'checked':'')+' onchange="togShop('+i+')"><span class="lt'+(it.done?' done':'')+'">'+esc(it.text)+'</span><button class="dbtn" onclick="delShop('+i+')">✕</button></div>').join('');
}
function addShopItem() { const inp = document.getElementById('shop-input'); const t = inp.value.trim(); if (!t) return; shopItems.push({text:t,done:false}); sv('shop',shopItems); renderShop(); inp.value=''; inp.focus(); }
function togShop(i) { shopItems[i].done = !shopItems[i].done; sv('shop',shopItems); renderShop(); }
function delShop(i) { shopItems.splice(i,1); sv('shop',shopItems); renderShop(); }

// Expenses
let expenses = ld('expenses', []);
function openExpModal() { document.getElementById('expense-modal').classList.add('show'); }
function closeExpModal() { document.getElementById('expense-modal').classList.remove('show'); document.getElementById('exp-desc').value=''; document.getElementById('exp-amount').value=''; }
function addExpense() {
    const desc = document.getElementById('exp-desc').value.trim();
    const amount = parseFloat(document.getElementById('exp-amount').value);
    const cat = document.getElementById('exp-cat').value;
    if (!desc || isNaN(amount)) return;
    expenses.unshift({desc, amount, cat, date: new Date().toLocaleDateString('de-DE', {day:'numeric', month:'short'})});
    sv('expenses', expenses);
    closeExpModal();
    renderExpenses();
}
function delExp(i) { expenses.splice(i,1); sv('expenses',expenses); renderExpenses(); }
function renderExpenses() {
    const total = expenses.reduce((s, e) => s + e.amount, 0);
    const byCat = {};
    expenses.forEach(e => { byCat[e.cat] = (byCat[e.cat] || 0) + e.amount; });

    document.getElementById('expense-summary').innerHTML =
        '<div class="expense-summary"><div class="expense-total">€ '+total.toFixed(2)+'</div><div class="expense-label">Gesamtausgaben</div>' +
        '<div class="expense-cats">'+Object.entries(byCat).map(([c,a]) => '<span class="expense-cat-badge">'+c+': €'+a.toFixed(2)+'</span>').join('')+'</div></div>';

    const c = document.getElementById('expense-items');
    if (!expenses.length) { c.innerHTML = '<div class="empty" style="padding:1rem"><p>Noch keine Ausgaben erfasst.</p></div>'; return; }
    c.innerHTML = '<div class="card">' + expenses.map((e, i) =>
        '<div class="expense-item"><div><div class="ei-name">'+esc(e.desc)+'</div><div class="ei-cat">'+esc(e.cat)+' · '+esc(e.date)+'</div></div><div style="display:flex;align-items:center;gap:0.5rem"><span class="ei-amount">€'+e.amount.toFixed(2)+'</span><button class="dbtn" onclick="delExp('+i+')">✕</button></div></div>'
    ).join('') + '</div>';
}

// ===== INIT =====
renderPlan();
renderJournal();
renderPack();
renderShop();
renderExpenses();
