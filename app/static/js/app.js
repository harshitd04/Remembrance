/**
 * Remembrance - Minimal JavaScript Implementation
 * Voice journaling application
 */

// ============================================================================
// 1. AUDIO RECORDER
// ============================================================================

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let recordingStartTime = null;

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    isRecording = true;
    recordingStartTime = Date.now();

    const micButton = document.querySelector('.btn-microphone');
    micButton.classList.add('recording');
    micButton.textContent = '⏹️';

    updateRecordingTimer();

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = handleRecordingStop;
    mediaRecorder.start();

    // Auto-stop after 15 minutes
    setTimeout(() => {
      if (isRecording) stopRecording();
    }, 900000);

  } catch (error) {
    showNotification('Microphone access denied', 'error');
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording) {
    mediaRecorder.stop();
    isRecording = false;

    const micButton = document.querySelector('.btn-microphone');
    micButton.classList.remove('recording');
    micButton.textContent = '🎤';

    mediaRecorder.stream.getTracks().forEach(track => track.stop());
  }
}

function handleRecordingStop() {
  const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

  console.log('Audio blob size:', audioBlob.size, 'bytes');
  console.log('Audio blob type:', audioBlob.type);

  if (audioBlob.size === 0) {
    showNotification('Recording is empty. Please try again.', 'error');
    return;
  }

  if (audioBlob.size > 26214400) {
    showNotification('Recording too large (max 25MB)', 'error');
    return;
  }

  sendAudioForTranscription(audioBlob);
}

function updateRecordingTimer() {
  if (!isRecording) return;

  const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;

  const timerDisplay = document.querySelector('.recording-time');
  if (timerDisplay) {
    timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }

  setTimeout(updateRecordingTimer, 1000);
}

async function sendAudioForTranscription(audioBlob) {
  showNotification('Transcribing audio...', 'info');

  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  formData.append('source', 'microphone'); // Mark as microphone input

  console.log('Sending audio for transcription...');

  try {
    const response = await fetch('/api/transcribe', {
      method: 'POST',
      body: formData
    });

    console.log('Response status:', response.status);

    const data = await response.json();
    console.log('Response data:', data);
    
    if (!response.ok) {
      throw new Error(data.message || 'Transcription failed');
    }

    const textOutput = document.querySelector('textarea[name="content"]');
    textOutput.value = data.text;

    showNotification('Transcription complete!', 'success');
  } catch (error) {
    console.error('Transcription error:', error);
    showNotification('Error: ' + error.message, 'error', 5000);
  }
}

// ============================================================================
// 2. FILE UPLOAD HANDLER
// ============================================================================

function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  if (file.size > 26214400) {
    showNotification('File too large (max 25MB)', 'error');
    return;
  }

  const formData = new FormData();
  formData.append('audio', file);
  formData.append('source', 'file'); // Mark as file upload

  showNotification('Uploading and transcribing...', 'info');

  fetch('/api/transcribe', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      document.querySelector('textarea[name="content"]').value = data.text;
      showNotification('Transcription complete!', 'success');
    })
    .catch(() => showNotification('Upload failed', 'error'));
}

// ============================================================================
// 3. FORM SUBMISSION
// ============================================================================

function handleFormSubmit(event) {
  event.preventDefault();

  const content = document.querySelector('textarea[name="content"]').value.trim();
  const date = document.querySelector('input[name="date"]').value;
  const entryType = document.querySelector('input[name="type"]')?.value || 'text';

  if (!content) {
    showNotification('Please enter journal content', 'error');
    return;
  }

  fetch('/journal/new-entry', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      content: content,
      date: date,
      type: entryType
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.appended) {
        showNotification('📝 Entry appended to existing date', 'soft-notification');
      } else {
        showNotification('Journal entry saved!', 'success');
      }

      document.querySelector('form').reset();
      
      // Set date back to today
      const dateInput = document.querySelector('input[name="date"]');
      if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
      }
    })
    .catch(() => showNotification('Save failed', 'error'));
}

// ============================================================================
// 4. SEARCH FUNCTIONALITY
// ============================================================================

function handleSearchSubmit(event) {
  event.preventDefault();

  const query = document.querySelector('input[name="query"]').value.trim();
  const searchType = document.querySelector('[name="search_type"]:checked')?.value || 'keyword';

  if (!query) {
    showNotification('Enter search query', 'error');
    return;
  }

  const endpoint = searchType === 'semantic' ? '/search/semantic' : '/search/keyword';

  fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: query, top_k: 10 })
  })
    .then(res => res.json())
    .then(data => {
      displaySearchResults(data);
      if (data.results.length === 0) {
        showNotification('No results found', 'info');
      }
    })
    .catch(() => showNotification('Search failed', 'error'));
}

function displaySearchResults(data) {
  const resultsContainer = document.querySelector('.search-results');
  resultsContainer.innerHTML = '';

  if (data.results.length === 0) {
    resultsContainer.innerHTML = '<p>No results found.</p>';
    return;
  }

  // Display AI summary if available
  if (data.ai_summary) {
    const summaryDiv = document.createElement('div');
    summaryDiv.className = 'card';
    summaryDiv.innerHTML = `
      <h3>AI Insights</h3>
      <p>${data.ai_summary}</p>
    `;
    resultsContainer.appendChild(summaryDiv);
  }

  // Display results
  data.results.forEach(result => {
    const resultDiv = document.createElement('div');
    resultDiv.className = 'result-item';
    
    let relevanceHTML = '';
    if (result.relevance_score) {
      const percentage = Math.round(result.relevance_score * 100);
      relevanceHTML = `<span class="result-relevance">${percentage}% match</span>`;
    }

    resultDiv.innerHTML = `
      <div class="result-date">${result.date}</div>
      <p class="result-excerpt">${result.excerpt || result.text}</p>
      ${relevanceHTML}
    `;

    resultsContainer.appendChild(resultDiv);
  });
}

// ============================================================================
// 5. NOTIFICATIONS
// ============================================================================

function showNotification(message, type = 'info', duration = 3000) {
  const notification = document.createElement('div');
  notification.className = `alert alert-${type}`;
  notification.textContent = message;
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.remove();
  }, duration);
}

// ============================================================================
// 6. PAGE INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  // Set default date to today
  const dateInput = document.querySelector('input[name="date"]');
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
  }

  // Attach event listeners
  const micButton = document.querySelector('.btn-microphone');
  if (micButton) {
    micButton.addEventListener('click', () => {
      isRecording ? stopRecording() : startRecording();
    });
  }

  const fileInput = document.querySelector('input[type="file"]');
  if (fileInput) {
    fileInput.addEventListener('change', handleFileUpload);
  }

  const journalForm = document.querySelector('form[data-form="journal"]');
  if (journalForm) {
    journalForm.addEventListener('submit', handleFormSubmit);
  }

  const searchForm = document.querySelector('form[data-form="search"]');
  if (searchForm) {
    searchForm.addEventListener('submit', handleSearchSubmit);
  }
});
