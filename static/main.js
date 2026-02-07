/**
 * File Converter — Frontend
 * Vanilla JS, Drag & Drop, Progress, Fetch API
 */

(function () {
    'use strict';

    const DROP_ZONE = document.getElementById('dropZone');
    const FILE_INPUT = document.getElementById('fileInput');
    const DROP_CONTENT = document.getElementById('dropContent');
    const CHOOSE_BTN = document.getElementById('chooseBtn');
    const CONVERSION_PANEL = document.getElementById('conversionPanel');
    const FILE_INFO = document.getElementById('fileInfo');
    const FILE_NAME = document.getElementById('fileName');
    const FILE_FORMAT = document.getElementById('fileFormat');
    const REMOVE_BTN = document.getElementById('removeBtn');
    const TARGET_SELECT = document.getElementById('targetSelect');
    const TARGET_FORMAT = document.getElementById('targetFormat');
    const PROGRESS_WRAP = document.getElementById('progressWrap');
    const PROGRESS_FILL = document.getElementById('progressFill');
    const PROGRESS_TEXT = document.getElementById('progressText');
    const CONVERT_BTN = document.getElementById('convertBtn');
    const RESULT_WRAP = document.getElementById('resultWrap');
    const DOWNLOAD_BTN = document.getElementById('downloadBtn');
    const ERROR_TOAST = document.getElementById('errorToast');
    const ERROR_TEXT = document.getElementById('errorText');

    let currentFile = null;
    let detectedFormat = null;
    let availableTargets = [];
    let convertedBlob = null;
    let convertedFileName = null;

    // ----- Helpers -----
    function show(el) {
        el.classList.remove('hidden');
    }

    function hide(el) {
        el.classList.add('hidden');
    }

    function showError(msg) {
        ERROR_TEXT.textContent = msg;
        ERROR_TOAST.classList.remove('hidden');
        ERROR_TOAST.classList.add('visible');
        setTimeout(() => {
            ERROR_TOAST.classList.remove('visible');
            setTimeout(() => hide(ERROR_TOAST), 300);
        }, 4000);
    }

    function showLimitModal(msg) {
        const modal = document.getElementById('limitModal');
        const textEl = document.getElementById('limitModalText');
        if (modal && textEl) {
            textEl.textContent = msg;
            modal.classList.remove('hidden');
        }
    }

    function hideLimitModal() {
        const modal = document.getElementById('limitModal');
        if (modal) modal.classList.add('hidden');
    }

    function resetState() {
        currentFile = null;
        detectedFormat = null;
        availableTargets = [];
        convertedBlob = null;
        convertedFileName = null;
        FILE_INPUT.value = '';
        TARGET_FORMAT.innerHTML = '<option value="">Выберите формат</option>';
        CONVERT_BTN.disabled = true;
        hide(PROGRESS_WRAP);
        hide(RESULT_WRAP);
        CONVERT_BTN.classList.remove('loading');
    }

    // ----- Drag & Drop -----
    function preventDefault(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleDragOver(e) {
        preventDefault(e);
        DROP_ZONE.classList.add('drag-over');
    }

    function handleDragLeave(e) {
        preventDefault(e);
        DROP_ZONE.classList.remove('drag-over');
    }

    function handleDrop(e) {
        preventDefault(e);
        DROP_ZONE.classList.remove('drag-over');
        const files = e.dataTransfer?.files;
        if (files && files.length) {
            handleFile(files[0]);
        }
    }

    DROP_ZONE.addEventListener('dragenter', handleDragOver);
    DROP_ZONE.addEventListener('dragover', handleDragOver);
    DROP_ZONE.addEventListener('dragleave', handleDragLeave);
    DROP_ZONE.addEventListener('drop', handleDrop);

    // ----- File input -----
    CHOOSE_BTN.addEventListener('click', (e) => {
        e.stopPropagation();
        FILE_INPUT.click();
    });

    FILE_INPUT.addEventListener('change', () => {
        const file = FILE_INPUT.files[0];
        if (file) handleFile(file);
    });

    // ----- Detect format -----
    async function detectFormat(filename) {
        const resp = await fetch(`/api/detect/?filename=${encodeURIComponent(filename)}`);
        const data = await resp.json();
        if (data.error) {
            showError(data.error);
            return null;
        }
        return data;
    }

    // ----- Handle selected file -----
    async function handleFile(file) {
        resetState();
        currentFile = file;

        const detectData = await detectFormat(file.name);
        if (!detectData || !detectData.detected) {
            showError('Формат файла не поддерживается');
            return;
        }

        detectedFormat = detectData.detected;
        availableTargets = detectData.targets || [];

        FILE_NAME.textContent = file.name;
        FILE_FORMAT.textContent = detectedFormat.toUpperCase();

        TARGET_FORMAT.innerHTML = '<option value="">Выберите формат</option>';
        availableTargets.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t;
            opt.textContent = t.toUpperCase();
            TARGET_FORMAT.appendChild(opt);
        });

        show(CONVERSION_PANEL);
        hide(DROP_ZONE);
    }

    // ----- Remove file -----
    REMOVE_BTN.addEventListener('click', () => {
        resetState();
        show(DROP_ZONE);
        hide(CONVERSION_PANEL);
    });

    // ----- Target format change -----
    TARGET_FORMAT.addEventListener('change', () => {
        CONVERT_BTN.disabled = !TARGET_FORMAT.value;
    });

    // ----- Convert -----
    CONVERT_BTN.addEventListener('click', doConvert);

    async function doConvert() {
        if (!currentFile || !TARGET_FORMAT.value) return;

        const target = TARGET_FORMAT.value;
        show(PROGRESS_WRAP);
        PROGRESS_FILL.style.width = '0%';
        PROGRESS_TEXT.textContent = 'Загрузка...';
        CONVERT_BTN.classList.add('loading');
        CONVERT_BTN.disabled = true;

        const formData = new FormData();
        formData.append('file', currentFile);
        formData.append('target', target);
        formData.append('csrfmiddlewaretoken', getCsrfToken());

        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const pct = Math.round((e.loaded / e.total) * 50);
                PROGRESS_FILL.style.width = pct + '%';
                PROGRESS_TEXT.textContent = `Загрузка ${pct}%`;
            }
        });

        xhr.addEventListener('load', () => {
            PROGRESS_FILL.style.width = '100%';
            PROGRESS_TEXT.textContent = 'Готово!';

            if (xhr.status >= 400) {
                try {
                    const text = new TextDecoder().decode(xhr.response);
                    const data = JSON.parse(text);
                    if (data.limit_exceeded) {
                        showLimitModal(data.error || 'Достигнут лимит');
                    } else {
                        showError(data.error || 'Ошибка конвертации');
                    }
                } catch {
                    showError('Ошибка конвертации');
                }
                hide(PROGRESS_WRAP);
                CONVERT_BTN.classList.remove('loading');
                CONVERT_BTN.disabled = false;
                return;
            }

            {
                const blob = new Blob([xhr.response], { type: 'application/octet-stream' });
                const disp = xhr.getResponseHeader('Content-Disposition');
                let fname = currentFile.name.replace(/\.[^.]+$/, '') + '.' + target;
                if (disp) {
                    const m = disp.match(/filename="?([^";\n]+)"?/);
                    if (m) fname = m[1];
                }
                convertedBlob = blob;
                convertedFileName = fname;
                show(RESULT_WRAP);
            }

            hide(PROGRESS_WRAP);
            CONVERT_BTN.classList.remove('loading');
            CONVERT_BTN.disabled = false;
        });

        xhr.addEventListener('error', () => {
            showError('Ошибка сети');
            hide(PROGRESS_WRAP);
            CONVERT_BTN.classList.remove('loading');
            CONVERT_BTN.disabled = false;
        });

        xhr.open('POST', '/api/convert/');
        xhr.setRequestHeader('X-CSRFToken', getCsrfToken());
        xhr.responseType = 'arraybuffer';

        // Simulate conversion progress (50-95%) while waiting
        let fakeProgress = 50;
        const iv = setInterval(() => {
            if (fakeProgress < 95) {
                fakeProgress += 5;
                PROGRESS_FILL.style.width = fakeProgress + '%';
                PROGRESS_TEXT.textContent = 'Конвертация...';
            }
        }, 200);

        xhr.onloadend = () => clearInterval(iv);

        xhr.send(formData);
    }

    // ----- Limit modal close -----
    const LIMIT_MODAL_CLOSE = document.getElementById('limitModalClose');
    if (LIMIT_MODAL_CLOSE) {
        LIMIT_MODAL_CLOSE.addEventListener('click', hideLimitModal);
    }

    // ----- Download -----
    DOWNLOAD_BTN.addEventListener('click', () => {
        if (!convertedBlob || !convertedFileName) return;
        const a = document.createElement('a');
        a.href = URL.createObjectURL(convertedBlob);
        a.download = convertedFileName;
        a.click();
        URL.revokeObjectURL(a.href);
    });

})();
