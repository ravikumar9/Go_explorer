document.addEventListener('DOMContentLoaded', function () {
    const slider = document.querySelector('.image-slider');
    // collect images from slider and room thumbnails
    const imgs = [];
    if (slider) imgs.push(...Array.from(slider.querySelectorAll('img')));
    imgs.push(...Array.from(document.querySelectorAll('.room-thumb')));
    // also include thumb-strip images if present
    imgs.push(...Array.from(document.querySelectorAll('.thumb-item')));
    // dedupe by src
    const seen = new Set();
    const uniq = imgs.filter(i => {
        if (!i || !i.src) return false;
        if (seen.has(i.src)) return false;
        seen.add(i.src);
        return true;
    });
    if (!uniq.length) return;

    // build overlay
    const overlay = document.createElement('div');
    overlay.className = 'lb-overlay';
    overlay.innerHTML = `
        <button class="lb-close" aria-label="Close">✕</button>
        <button class="lb-prev" aria-label="Previous">◀</button>
        <img class="lb-img" src="" alt="">
        <div class="lb-caption" style="color:#fff;margin-top:10px;font-size:14px;text-align:center"></div>
        <button class="lb-next" aria-label="Next">▶</button>
    `;
    document.body.appendChild(overlay);

    const lbImg = overlay.querySelector('.lb-img');
    const btnClose = overlay.querySelector('.lb-close');
    const btnPrev = overlay.querySelector('.lb-prev');
    const btnNext = overlay.querySelector('.lb-next');

    let index = 0;
    // disable autoplay by default to avoid interrupting user interactions
    let autoplay = false;
    const interval = 3500; // ms
    let timer = null;

    function startTimer(){ if(timer) clearInterval(timer); if(autoplay) timer = setInterval(()=> show(index+1), interval); }
    function stopTimer(){ if(timer){ clearInterval(timer); timer=null; } }

    function show(i) {
        index = (i + uniq.length) % uniq.length;
        lbImg.src = uniq[index].src;
        // caption: prefer data-caption then alt
        const cap = uniq[index].getAttribute('data-caption') || uniq[index].alt || '';
        const capEl = overlay.querySelector('.lb-caption');
        if(capEl) capEl.textContent = cap;
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        // update active thumb
        document.querySelectorAll('.thumb-item').forEach(t=> t.classList.remove('active'));
        const activeThumb = Array.from(document.querySelectorAll('.thumb-item')).find(t => t.src === uniq[index].src);
        if(activeThumb) activeThumb.classList.add('active');
        // ensure the corresponding image is scrolled into view if inside slider
        if(uniq[index].scrollIntoView){ try{ uniq[index].scrollIntoView({behavior:'smooth', inline:'center', block:'nearest'}); }catch(e){} }
        // do not auto-start timer here (autoplay disabled by default)
    }

    function hide() {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    uniq.forEach((img, i) => {
        img.style.cursor = 'zoom-in';
        img.addEventListener('click', (e) => { e.preventDefault(); show(i); });
    });

    // thumbnail strip clicks
    document.querySelectorAll('.thumb-item').forEach(t => {
        t.addEventListener('click', (e)=>{
            const idx = parseInt(t.getAttribute('data-index')||'0',10);
            show(idx);
        });
    });

    // pause on hover (do not toggle autoplay flag automatically)
    const hoverTargets = [document.querySelector('.image-slider'), document.querySelector('.thumb-strip')].filter(Boolean);
    hoverTargets.forEach(el=>{
        el.addEventListener('mouseenter', ()=>{ stopTimer(); });
        el.addEventListener('mouseleave', ()=>{ if(autoplay) startTimer(); });
    });

    // Play/Pause control: add small buttons inside the global thumb-strip and inside each room card
    const thumbStrip = document.querySelector('.thumb-strip');
    const roomRights = Array.from(document.querySelectorAll('.room-right'));
    const playButtons = [];

    function updatePlayButtons() {
        playButtons.forEach(pb => {
            pb.textContent = autoplay ? 'Pause' : 'Play';
            pb.setAttribute('aria-pressed', String(autoplay));
        });
    }

    // create a play button element
    function createPlayButton() {
        const btn = document.createElement('button');
        btn.className = 'play-btn';
        btn.setAttribute('aria-pressed','false');
        btn.textContent = 'Play';
        btn.style.marginLeft = '8px';
        btn.addEventListener('click', function(e){
            e.preventDefault();
            autoplay = !autoplay;
            if (autoplay) startTimer(); else stopTimer();
            updatePlayButtons();
        });
        return btn;
    }

    if (thumbStrip) {
        const tb = createPlayButton();
        thumbStrip.appendChild(tb);
        playButtons.push(tb);
    }

    // add play button inside each room-right so controls are available per-room
    roomRights.forEach(rr => {
        const pb = createPlayButton();
        // place the button just before the plans container (so it appears visually next to plans)
        rr.insertBefore(pb, rr.querySelector('.plans-container') || rr.lastChild);
        playButtons.push(pb);
    });

    btnClose.addEventListener('click', hide);
    overlay.addEventListener('click', function (e) { if (e.target === overlay) hide(); });
    btnPrev.addEventListener('click', function (e) { e.stopPropagation(); show(index - 1); });
    btnNext.addEventListener('click', function (e) { e.stopPropagation(); show(index + 1); });

    // keyboard support
    document.addEventListener('keydown', function (e) {
        if (!overlay.classList.contains('active')) return;
        if (e.key === 'Escape') hide();
        if (e.key === 'ArrowLeft') show(index - 1);
        if (e.key === 'ArrowRight') show(index + 1);
    });
});
