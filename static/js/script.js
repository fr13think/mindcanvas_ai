document.addEventListener('DOMContentLoaded', () => {
    let userId = localStorage.getItem('mindCanvasUserId');
    if (!userId) {
        userId = 'user-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('mindCanvasUserId', userId);
    }

    let selectedTimeframe = 'random';
    const timeframeButtons = document.querySelectorAll('.timeframe-btn');
    timeframeButtons.forEach(button => {
        button.addEventListener('click', () => {
            timeframeButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            selectedTimeframe = button.dataset.timeframe;
        });
    });

    const analyzeButton = document.getElementById('analyze-button');
    const journalInput = document.getElementById('journal-input');
    const resultsArea = document.getElementById('results-area');
    const loader = document.getElementById('loader');
    
    // DIUBAH: Kunci di sini sekarang 100% cocok dengan backend
    const outputs = {
        greeting: document.getElementById('greeting-output'),
        summary: document.getElementById('summary-output'),
        meter: document.getElementById('meter-output'),
        pattern: document.getElementById('pattern-output'),
        suggestion: document.getElementById('suggestion-output'),
        nugget: document.getElementById('nugget-output'),
        sentiment: document.getElementById('sentiment-output'),
        topics: document.getElementById('topics-output'),
        connection: document.getElementById('connection-output')
    };

    function renderMeter(meterText) {
        const meterContainer = outputs.meter;
        meterContainer.innerHTML = '';

        if (!meterText || typeof meterText !== 'string') {
            meterContainer.textContent = 'N/A';
            return;
        }

        const lines = meterText.split('\n').filter(line => line.trim() !== '');
        lines.forEach(line => {
            const match = line.match(/(.+?):\s*(\d)\/(\d)/);
            if (match) {
                const label = match[1].trim();
                const score = parseInt(match[2], 10);
                const max = parseInt(match[3], 10);
                const percentage = (score / max) * 100;

                const item = document.createElement('div');
                item.className = 'meter-item';
                item.innerHTML = `
                    <div class="meter-label">${label} <span>${score}/${max}</span></div>
                    <div class="meter-bar">
                        <div class="meter-bar-fill" style="width: 0;"></div>
                    </div>
                `;
                meterContainer.appendChild(item);

                setTimeout(() => {
                    item.querySelector('.meter-bar-fill').style.width = `${percentage}%`;
                }, 100);
            }
        });
    }

    analyzeButton.addEventListener('click', async () => {
        const entry = journalInput.value;
        if (!entry.trim()) {
            alert('Silakan tulis entri jurnal Anda terlebih dahulu.');
            return;
        }

        resultsArea.classList.remove('hidden');
        loader.classList.remove('hidden');
        document.querySelector('.result-grid').style.display = 'none';
        document.querySelector('.disclaimer').style.display = 'none';
        if (outputs.greeting) outputs.greeting.style.display = 'none';

        try {
            const response = await fetch('/api/analyze_journal', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ entry: entry, userId: userId, timeframe: selectedTimeframe }),
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const result = await response.json();

            loader.classList.add('hidden');
            document.querySelector('.result-grid').style.display = 'grid';
            document.querySelector('.disclaimer').style.display = 'block';
            if (outputs.greeting) outputs.greeting.style.display = 'block';
            
            // Mengisi semua elemen output
            for (const key in outputs) {
                if (outputs.hasOwnProperty(key)) {
                    if (key === 'meter') {
                        renderMeter(result[key]);
                    } else if (outputs[key] && result[key]) {
                        outputs[key].textContent = result[key];
                    } else if (outputs[key]) {
                        outputs[key].textContent = 'N/A';
                    }
                }
            }

        } catch (error) {
            loader.classList.add('hidden');
            outputs.summary.textContent = `Gagal menganalisis: ${error.message}`;
            console.error('Error fetching analysis:', error);
        }
    });
});
