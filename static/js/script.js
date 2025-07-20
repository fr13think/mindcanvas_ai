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
    
    const outputs = {
        greeting: document.getElementById('greeting-output'),
        summary: document.getElementById('summary-output'),
        meter: document.getElementById('meter-output'),
        pattern: document.getElementById('pattern-output'),
        suggestion: document.getElementById('suggestion-output'),
        connection: document.getElementById('connection-output') // Ini sekarang untuk 'nugget'
    };

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

            outputs.greeting.textContent = result.greeting || '';
            outputs.summary.textContent = result.summary || 'N/A';
            outputs.meter.textContent = result.meter || 'N/A';
            outputs.pattern.textContent = result.pattern || 'N/A';
            outputs.suggestion.textContent = result.suggestion || 'N/A';
            outputs.connection.textContent = result.connection || 'N/A';
            
        } catch (error) {
            loader.classList.add('hidden');
            outputs.summary.textContent = `Gagal menganalisis: ${error.message}`;
            console.error('Error fetching analysis:', error);
        }
    });
});