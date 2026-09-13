/*
 * script.js
 * ---------
 * The missing piece. This file does four things:
 *   1. Switches between views (Home / Crop Advisor / Irrigation / Pest / Chat)
 *      whenever a button with a `data-view` attribute is clicked.
 *   2. Loads soil types + crop names from /api/crops and fills the <select>
 *      dropdowns, so the frontend never has a stale copy of the backend's data.
 *   3. Submits each form to its matching /api/... route and renders the
 *      JSON response into "note-card" panels (the styling already exists
 *      in style.css — this just builds the matching HTML).
 *   4. Handles the chat box: sends each message to /api/chat and appends
 *      the reply as a bot bubble.
 */

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  // ---------------------------------------------------------------
  // Small shared helpers
  // ---------------------------------------------------------------
  function escapeHtml(str) {
    if (str === undefined || str === null) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function setStatus(id, message, isError) {
    const el = document.getElementById(id);
    if (!el) return;
    if (!message) {
      el.classList.add('hidden');
      el.textContent = '';
      return;
    }
    el.textContent = message;
    el.classList.remove('hidden');
    el.classList.toggle('error', !!isError);
  }

  function populateSelect(id, items, placeholder) {
    const select = document.getElementById(id);
    if (!select) return;
    select.innerHTML = '';
    const placeholderOpt = document.createElement('option');
    placeholderOpt.value = '';
    placeholderOpt.disabled = true;
    placeholderOpt.selected = true;
    placeholderOpt.textContent = placeholder;
    select.appendChild(placeholderOpt);
    items.forEach((item) => {
      const opt = document.createElement('option');
      opt.value = item;
      opt.textContent = item;
      select.appendChild(opt);
    });
  }

  // ---------------------------------------------------------------
  // 1. VIEW SWITCHING (nav links + home tool-row buttons)
  // ---------------------------------------------------------------
  function switchView(viewName) {
    document.querySelectorAll('.view').forEach((v) => v.classList.remove('active'));
    const target = document.getElementById('view-' + viewName);
    if (target) target.classList.add('active');

    document.querySelectorAll('.nav-link').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.view === viewName);
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  document.querySelectorAll('[data-view]').forEach((el) => {
    el.addEventListener('click', () => switchView(el.dataset.view));
  });

  // ---------------------------------------------------------------
  // 2. LOAD DROPDOWN OPTIONS FROM THE BACKEND
  // ---------------------------------------------------------------
  async function loadOptions() {
    try {
      const res = await fetch('/api/crops');
      const data = await res.json();
      populateSelect('crop-soil', data.soil_types, 'Select soil type');
      populateSelect('irrigation-crop', data.crops, 'Select crop');
      populateSelect('pest-crop', data.crops, 'Select crop');
    } catch (err) {
      console.error('Failed to load crop/soil options:', err);
    }
  }
  loadOptions();

  // ---------------------------------------------------------------
  // 3a. CROP ADVISOR
  // ---------------------------------------------------------------
  const cropForm = document.getElementById('crop-form');
  cropForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = cropForm.querySelector('button[type="submit"]');
    const resultsEl = document.getElementById('crop-results');
    resultsEl.classList.add('hidden');
    resultsEl.innerHTML = '';
    setStatus('crop-status', 'Finding crops that fit…');
    submitBtn.disabled = true;

    const payload = {
      soil_type: document.getElementById('crop-soil').value,
      location: document.getElementById('crop-location').value.trim(),
      farm_size: parseFloat(document.getElementById('crop-size').value),
      budget: parseFloat(document.getElementById('crop-budget').value),
    };

    try {
      const res = await fetch('/api/crop-advisor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.error) {
        setStatus('crop-status', data.error, true);
        return;
      }
      if (!data.recommendations || data.recommendations.length === 0) {
        setStatus('crop-status', data.message || 'No matching crops found.', true);
        return;
      }

      setStatus('crop-status', '');
      resultsEl.innerHTML = data.recommendations
        .map(
          (rec) => `
        <div class="note-card">
          <div class="note-title">${escapeHtml(rec.crop)}</div>
          <div class="note-meta">
            <span>${escapeHtml(rec.season)}</span>
            <span>${escapeHtml(rec.duration)}</span>
            <span>${escapeHtml(rec.water_needs)} water need</span>
          </div>
          <div class="note-body">
            <p>${escapeHtml(rec.reason)}</p>
            <p><strong>Fertilizer tip:</strong> ${escapeHtml(rec.fertilizer_tip)}</p>
            <p><strong>Expected yield:</strong> ${escapeHtml(rec.expected_yield)}</p>
            <p><strong>Estimated total cost:</strong> ₹${Number(rec.estimated_total_cost).toLocaleString('en-IN')}</p>
          </div>
        </div>`
        )
        .join('');
      resultsEl.classList.remove('hidden');
    } catch (err) {
      console.error(err);
      setStatus('crop-status', 'Could not reach the server. Please try again.', true);
    } finally {
      submitBtn.disabled = false;
    }
  });

  // ---------------------------------------------------------------
  // 3b. SMART IRRIGATION
  // ---------------------------------------------------------------
  const irrigationForm = document.getElementById('irrigation-form');
  irrigationForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = irrigationForm.querySelector('button[type="submit"]');
    const resultsEl = document.getElementById('irrigation-results');
    resultsEl.classList.add('hidden');
    resultsEl.innerHTML = '';
    setStatus('irrigation-status', 'Working out the best irrigation plan…');
    submitBtn.disabled = true;

    const payload = {
      location: document.getElementById('irrigation-location').value.trim(),
      crop: document.getElementById('irrigation-crop').value,
    };

    try {
      const res = await fetch('/api/irrigation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.error) {
        setStatus('irrigation-status', data.error, true);
        return;
      }

      setStatus('irrigation-status', '');
      resultsEl.innerHTML = `
        <div class="note-card accent-water">
          <div class="note-title">${escapeHtml(data.recommended_method)}</div>
          <div class="note-meta">
            <span>${escapeHtml(data.crop)}</span>
            <span>${escapeHtml(data.rainfall_zone)} rainfall zone</span>
          </div>
          <div class="note-body">
            <p>${escapeHtml(data.reason)}</p>
            <p><strong>Frequency:</strong> ${escapeHtml(data.frequency)}</p>
            <p>${escapeHtml(data.rainfall_tip)}</p>
          </div>
        </div>`;
      resultsEl.classList.remove('hidden');
    } catch (err) {
      console.error(err);
      setStatus('irrigation-status', 'Could not reach the server. Please try again.', true);
    } finally {
      submitBtn.disabled = false;
    }
  });

  // ---------------------------------------------------------------
  // 3c. PEST & DISEASE ASSISTANT (with optional photo preview)
  // ---------------------------------------------------------------
  const pestImageInput = document.getElementById('pest-image');
  const pestPreview = document.getElementById('pest-preview');

  pestImageInput.addEventListener('change', () => {
    const file = pestImageInput.files[0];
    if (!file) {
      pestPreview.classList.add('hidden');
      pestPreview.src = '';
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      pestPreview.src = e.target.result;
      pestPreview.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
  });

  const pestForm = document.getElementById('pest-form');
  pestForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = pestForm.querySelector('button[type="submit"]');
    const resultsEl = document.getElementById('pest-results');
    resultsEl.classList.add('hidden');
    resultsEl.innerHTML = '';
    setStatus('pest-status', 'Looking at what you described…');
    submitBtn.disabled = true;

    const formData = new FormData();
    formData.append('crop', document.getElementById('pest-crop').value);
    formData.append('description', document.getElementById('pest-description').value.trim());
    const file = pestImageInput.files[0];
    if (file) formData.append('image', file);

    try {
      // No Content-Type header here on purpose — the browser sets the
      // correct multipart boundary automatically for FormData bodies.
      const res = await fetch('/api/pest-assistant', { method: 'POST', body: formData });
      const data = await res.json();

      if (data.error) {
        setStatus('pest-status', data.error, true);
        return;
      }

      setStatus('pest-status', '');
      const riskLevel = data.risk_level || 'Unknown';
      const riskLower = riskLevel.toLowerCase();
      const riskClass = 'risk-' + riskLower;
      const accentClass = riskLower === 'high' ? 'accent-danger' : riskLower === 'medium' ? 'accent-gold' : '';

      resultsEl.innerHTML = `
        <div class="note-card ${accentClass}">
          <span class="risk-tag ${riskClass}">${escapeHtml(riskLevel)} risk</span>
          <div class="note-title">${escapeHtml(data.problem)}</div>
          <div class="note-body">
            <ul>${(data.actions || []).map((a) => `<li>${escapeHtml(a)}</li>`).join('')}</ul>
            ${data.image_note ? `<p>${escapeHtml(data.image_note)}</p>` : ''}
          </div>
        </div>`;
      resultsEl.classList.remove('hidden');
    } catch (err) {
      console.error(err);
      setStatus('pest-status', 'Could not reach the server. Please try again.', true);
    } finally {
      submitBtn.disabled = false;
    }
  });

  // ---------------------------------------------------------------
  // 3d. KRISHI AI CHAT
  // ---------------------------------------------------------------
  const chatForm = document.getElementById('chat-form');
  const chatWindow = document.getElementById('chat-window');
  const chatInput = document.getElementById('chat-input');

  function addChatMessage(text, sender) {
    const msg = document.createElement('div');
    msg.className = 'chat-msg ' + sender;
    const label = document.createElement('span');
    label.className = 'chat-msg-label';
    label.textContent = sender === 'user' ? 'You' : 'Krishi AI';
    const body = document.createElement('span');
    body.textContent = text;
    msg.appendChild(label);
    msg.appendChild(body);
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  // Friendly opener so the chat panel isn't empty on first visit.
  addChatMessage("Namaste! Ask me about fertilizers, irrigation, soil health, schemes, or general farming.", 'bot');

  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;

    addChatMessage(message, 'user');
    chatInput.value = '';
    chatInput.focus();

    const submitBtn = chatForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();
      addChatMessage(data.reply, 'bot');
    } catch (err) {
      console.error(err);
      addChatMessage("Sorry, I couldn't reach the server just now. Please try again.", 'bot');
    } finally {
      submitBtn.disabled = false;
    }
  });
});