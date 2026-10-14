document.addEventListener('DOMContentLoaded', () => {

    const fileInputs = document.querySelectorAll('.file-input');
    const pdfBtn = document.getElementById('pdfBtn');
    const resetBtn = document.getElementById('resetBtn');
    const dateInputs = document.querySelectorAll('.date-part');
    const qInputs = document.querySelectorAll('.q-input, .q-textarea, .family-tree-box, .family-tree-line, .tree-node');
    const imagePrefixes = Array.from(fileInputs)
        .map(input => input.getAttribute('data-id'))
        .filter(Boolean)
        .map(id => id.replace(/-img$/, ''));

    // Handle Image Uploads and Preview
    fileInputs.forEach(input => {
        input.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (event) {
                    const dataUrl = event.target.result;
                    const img = new Image();
                    img.onload = function () {
                        const canvas = document.createElement('canvas');
                        const maxDim = 800; // max dimension to prevent QuotaExceededError
                        let w = img.width;
                        let h = img.height;
                        if (w > maxDim || h > maxDim) {
                            if (w > h) { h *= maxDim / w; w = maxDim; }
                            else { w *= maxDim / h; h = maxDim; }
                        }
                        canvas.width = w;
                        canvas.height = h;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0, w, h);

                        // Compress to WebP for massive sizes savings
                        const compressedDataUrl = canvas.toDataURL('image/webp', 0.7);

                        const previewId = input.getAttribute('data-id') + '-preview';
                        const previewElement = document.getElementById(previewId);
                        if (previewElement) {
                            previewElement.dataset.scale = 1;
                            previewElement.dataset.tx = 0;
                            previewElement.dataset.ty = 0;
                            previewElement.innerHTML = `<img src="${compressedDataUrl}" style="width:100%; height:100%; object-fit:cover; display:block; transform: scale(1) translate(0px, 0px); transform-origin: center; pointer-events: none;" />`;
                        }

                        // Show zoom controls
                        const controlsId = input.getAttribute('data-id').replace(/-img$/, '') + '-controls';
                        const controls = document.getElementById(controlsId);
                        if (controls) controls.style.display = 'block';

                        saveDraft();
                    };
                    img.src = dataUrl;
                };
                reader.readAsDataURL(file);
            }
        });
    });

    dateInputs.forEach(input => {
        input.addEventListener('input', saveDraft);
    });

    qInputs.forEach(input => {
        input.addEventListener('input', saveDraft);
    });

    // Helper to apply transform
    function updateTransform(previewElement) {
        const img = previewElement.querySelector('img');
        if (img) {
            const scale = previewElement.dataset.scale || 1;
            const tx = previewElement.dataset.tx || 0;
            const ty = previewElement.dataset.ty || 0;
            img.style.transform = `translate(${tx}px, ${ty}px) scale(${scale})`;
            saveDraft();
        }
    }

    const zoomSliders = document.querySelectorAll('.zoom-slider');
    zoomSliders.forEach(slider => {
        slider.addEventListener('input', function (e) {
            const targetId = this.getAttribute('data-target');
            const previewElement = document.getElementById(targetId);
            if (previewElement) {
                previewElement.dataset.scale = this.value;
                updateTransform(previewElement);
            }
        });
    });

    // --- Panning Logic ---
    let isDragging = false;
    let startX, startY;
    let activePreview = null;
    let isDragEvent = false;

    document.addEventListener('mousedown', startDrag);
    document.addEventListener('touchstart', startDrag, { passive: false });

    function startDrag(e) {
        const preview = e.target.closest('.image-preview');
        // Only drag if it actually has an image
        if (!preview || !preview.innerHTML.includes('<img')) return;

        isDragging = true;
        isDragEvent = false;
        activePreview = preview;

        startX = e.type.includes('mouse') ? e.pageX : e.touches[0].pageX;
        startY = e.type.includes('mouse') ? e.pageY : e.touches[0].pageY;
    }

    document.addEventListener('mousemove', drag);
    document.addEventListener('touchmove', drag, { passive: false });

    function drag(e) {
        if (!isDragging || !activePreview) return;

        const currentX = e.type.includes('mouse') ? e.pageX : e.touches[0].pageX;
        const currentY = e.type.includes('mouse') ? e.pageY : e.touches[0].pageY;

        const dx = currentX - startX;
        const dy = currentY - startY;

        // If moved more than 2px, mark as drag event
        if (Math.abs(dx) > 2 || Math.abs(dy) > 2) {
            isDragEvent = true;
            e.preventDefault(); // prevents scroll while panning
        }

        let tx = parseFloat(activePreview.dataset.tx || 0);
        let ty = parseFloat(activePreview.dataset.ty || 0);

        // Adjust for scale: moving mouse 10px when scaled 2x means image translation moves ~10px/scale natively 
        // We'll just translate without scale compensation or compensate by dividing by scale
        const scale = parseFloat(activePreview.dataset.scale || 1);
        activePreview.dataset.tx = tx + (dx / scale);
        activePreview.dataset.ty = ty + (dy / scale);

        startX = currentX;
        startY = currentY;

        updateTransform(activePreview);
    }

    document.addEventListener('mouseup', stopDrag);
    document.addEventListener('touchend', stopDrag);
    document.addEventListener('mouseleave', stopDrag);

    function stopDrag() {
        if (isDragging) {
            isDragging = false;
            activePreview = null;
        }
    }

    // Prevent 'click' firing on the <label> which triggers <input type="file"> if we were actually dragging
    document.addEventListener('click', function (e) {
        if (isDragEvent) {
            e.preventDefault();
            e.stopPropagation();
            isDragEvent = false;
        }
    }, true);

    let isRestoring = false;

    function saveDraft() {
        if (isRestoring) return;

        const questionnaireDraft = {};
        qInputs.forEach(input => {
            if (input.id) questionnaireDraft[input.id] = input.value;
        });

        const draft = {
            date1: dateInputs[0]?.value || '',
            date2: dateInputs[1]?.value || '',
            date3: dateInputs[2]?.value || '',
            questionnaire: questionnaireDraft,
            images: {}
        };

        imagePrefixes.forEach(prefix => {
            const preview = document.getElementById(`${prefix}-img-preview`);
            if (preview) {
                draft.images[prefix] = {
                    html: preview.innerHTML,
                    zoom: document.querySelector(`#${prefix}-controls .zoom-slider`)?.value || '1',
                    tx: preview.dataset.tx || 0,
                    ty: preview.dataset.ty || 0
                };
            }
        });

        // Ensure legacy format remains untouched when serialized so older iterations don't break
        draft.mainImg = draft.images['main']?.html || '';
        draft.subImg = draft.images['sub']?.html || '';
        draft.mainZoom = draft.images['main']?.zoom || '1';
        draft.subZoom = draft.images['sub']?.zoom || '1';
        draft.mainTx = draft.images['main']?.tx || 0;
        draft.mainTy = draft.images['main']?.ty || 0;
        draft.subTx = draft.images['sub']?.tx || 0;
        draft.subTy = draft.images['sub']?.ty || 0;

        try {
            localStorage.setItem('babyBookDraft', JSON.stringify(draft));
        } catch (e) {
            console.error("Storage quota exceeded!", e);
            alert("Warning: Your images are taking up too much browser memory! The draft could not be saved. Try uploading smaller files.");
        }
    }

    function restoreDraft() {
        const saved = localStorage.getItem('babyBookDraft');
        if (saved) {
            isRestoring = true;
            try {
                const draft = JSON.parse(saved);
                if (draft.date1 && dateInputs[0]) dateInputs[0].value = draft.date1;
                if (draft.date2 && dateInputs[1]) dateInputs[1].value = draft.date2;
                if (draft.date3 && dateInputs[2]) dateInputs[2].value = draft.date3;

                if (draft.questionnaire) {
                    Object.keys(draft.questionnaire).forEach(id => {
                        const el = document.getElementById(id);
                        if (el) el.value = draft.questionnaire[id];
                    });
                }

                // Migrate legacy standard mapping dynamically
                const imgsToRestore = [];
                if (draft.images && Object.keys(draft.images).length > 0) {
                    Object.keys(draft.images).forEach(prefix => {
                        imgsToRestore.push({ prefix, ...draft.images[prefix] });
                    });
                } else {
                    if (draft.mainImg) imgsToRestore.push({ prefix: 'main', html: draft.mainImg, zoom: draft.mainZoom, tx: draft.mainTx, ty: draft.mainTy });
                    if (draft.subImg) imgsToRestore.push({ prefix: 'sub', html: draft.subImg, zoom: draft.subZoom, tx: draft.subTx, ty: draft.subTy });
                }

                imgsToRestore.forEach(imgData => {
                    if (!imgData.html) return;
                    const preview = document.getElementById(`${imgData.prefix}-img-preview`);
                    if (preview) {
                        let htmlStr = imgData.html;
                        if (htmlStr.startsWith('url(')) { // Support exceptionally old iterations
                            const url = htmlStr.slice(4, -1).replace(/"/g, '');
                            htmlStr = `<img src="${url}" style="width:100%; height:100%; object-fit:cover; display:block; pointer-events:none;" />`;
                        }
                        preview.innerHTML = htmlStr;
                        preview.dataset.scale = imgData.zoom || 1;
                        preview.dataset.tx = imgData.tx || 0;
                        preview.dataset.ty = imgData.ty || 0;
                        updateTransform(preview);

                        const controls = document.getElementById(`${imgData.prefix}-controls`);
                        if (controls) controls.style.display = 'block';
                        const slider = document.querySelector(`#${imgData.prefix}-controls .zoom-slider`);
                        if (slider && imgData.zoom) slider.value = imgData.zoom;
                    }
                });

            } catch (e) {
                console.error("Failed to restore baby book draft", e);
            } finally {
                isRestoring = false;
            }
        }
    }

    // Export PDF via window.print()
    if (pdfBtn) {
        pdfBtn.addEventListener('click', () => {
            window.print();
        });
    }

    // Reset Functionality
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to reset this document? This will remove all uploaded images and text.')) {
                localStorage.removeItem('babyBookDraft');
                dateInputs.forEach(input => input.value = '');
                qInputs.forEach(input => input.value = '');

                imagePrefixes.forEach(prefix => {
                    const preview = document.getElementById(`${prefix}-img-preview`);
                    if (preview) preview.innerHTML = '';
                    const controls = document.getElementById(`${prefix}-controls`);
                    if (controls) controls.style.display = 'none';
                });
            }
        });
    }

    // Load draft on init
    restoreDraft();
});
