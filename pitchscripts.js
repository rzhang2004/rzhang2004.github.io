document.getElementById('noteForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const lowerNote = document.getElementById('lowerNote').value.trim();
    const higherNote = document.getElementById('higherNote').value.trim();

    const lowerFrequency = getFrequency(lowerNote);
    const higherEqualFrequency = getFrequency(higherNote);
    const higherJustFrequency = getJustIntonationFrequency(lowerNote, higherNote);
    const pitchDifference = Math.abs(higherEqualFrequency - higherJustFrequency);

    document.getElementById('lowerFrequency').innerText = `Lower Note Frequency (Hz): ${lowerFrequency.toFixed(2)}`;
    document.getElementById('higherEqualFrequency').innerText = `Higher Note Frequency (Equal Temperament) (Hz): ${higherEqualFrequency.toFixed(2)}`;
    document.getElementById('higherJustFrequency').innerText = `Higher Note Frequency (Just Intonation) (Hz): ${higherJustFrequency ? higherJustFrequency.toFixed(2) : 'N/A'}`;
    document.getElementById('pitchDifference').innerText = `Tuning Discrepancy (Hz): ${pitchDifference.toFixed(2)}`;
});

const noteFrequencies = {
    'C': 16.35,
    'C#': 17.32,
    'D': 18.35,
    'D#': 19.45,
    'E': 20.60,
    'F': 21.83,
    'F#': 23.12,
    'G': 24.50,
    'G#': 25.96,
    'A': 27.50,
    'A#': 29.14,
    'B': 30.87
};

function getFrequency(note) {
    const noteName = note.slice(0, -1);
    const octave = parseInt(note.slice(-1), 10);
    const baseFrequency = noteFrequencies[noteName.toUpperCase()];
    return baseFrequency * Math.pow(2, octave);
}

function getJustIntonationFrequency(lowerNote, higherNote) {
    const ratioMap = {
        'C': {'C': 1, 'D': 9/8, 'Eb': 6/5, 'E': 5/4, 'F': 4/3, 'G': 3/2, 'Ab': 8/5, 'A': 5/3, 'B': 15/8},
        'D': {'D': 1, 'E': 9/8, 'F': 6/5, 'F#': 5/4, 'G': 4/3, 'A': 3/2, 'Bb': 8/5, 'B': 5/3, 'C#': 15/8},
        'E': {'E': 1, 'F#': 9/8, 'G': 6/5, 'G#': 5/4, 'A': 4/3, 'B': 3/2, 'C': 8/5, 'C#': 5/3, 'D#': 15/8},
        'F': {'F': 1, 'G': 9/8, 'Ab': 6/5, 'A': 5/4, 'Bb': 4/3, 'C': 3/2, 'Db': 8/5, 'D': 5/3, 'E': 15/8},
        'G': {'G': 1, 'A': 9/8, 'Bb': 6/5, 'B': 5/4, 'C': 4/3, 'D': 3/2, 'Eb': 8/5, 'E': 5/3, 'F#': 15/8},
        'A': {'A': 1, 'B': 9/8, 'C': 6/5, 'C#': 5/4, 'D': 4/3, 'E': 3/2, 'F': 8/5, 'F#': 5/3, 'G#': 15/8},
        'B': {'B': 1, 'C#': 9/8, 'D': 6/5, 'D#': 5/4, 'E': 4/3, 'F#': 3/2, 'G': 8/5, 'G#': 5/3, 'A#': 15/8}
    };

    const noteMap = {'C': 1, 'D': 2, 'E': 3, 'F': 4, 'G': 5, 'A': 6, 'B': 7};

    const lowerNoteName = lowerNote.slice(0, -1).toUpperCase();
    const higherNoteName = higherNote.slice(0, -1).toUpperCase();
    const lowerOctave = parseInt(lowerNote.slice(-1), 10);
    const higherOctave = parseInt(higherNote.slice(-1), 10);
    
    if (ratioMap[lowerNoteName] && ratioMap[lowerNoteName][higherNoteName]) {
        const ratio = ratioMap[lowerNoteName][higherNoteName];
        const lowerFrequency = getFrequency(lowerNote);
        let octaveDifference = higherOctave - lowerOctave;
        if (noteMap[lowerNoteName] > noteMap[higherNoteName]) {
            octaveDifference -= 1;
        }
        return lowerFrequency * ratio * Math.pow(2, octaveDifference);
    }

    return null;
}
