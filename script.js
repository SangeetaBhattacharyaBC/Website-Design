const form = document.getElementById('entryForm');
const nameInput = document.getElementById('name');
const messageInput = document.getElementById('message');
const entriesList = document.getElementById('entriesList');

async function loadEntries() {
  const res = await fetch('/api/entries');
  const entries = await res.json();
  renderEntries(entries);
}

function renderEntries(entries) {
  entriesList.innerHTML = '';
  if (!entries.length) {
    entriesList.innerHTML = '<li>No entries yet — be the first!</li>';
    return;
  }
  
  entries.forEach(e => {
    const li = document.createElement('li');
    li.className = 'entry';
    li.innerHTML = `
      <small>${escapeHtml(e.name)} · ${new Date(e.createdAt).toLocaleString()}</small>
      <div>${escapeHtml(e.message)}</div>
    `;
    entriesList.appendChild(li);
  });
}

form.addEventListener('submit', async e => {
  e.preventDefault();
  const payload = {
    name: nameInput.value.trim(),
    message: messageInput.value.trim()
  };
  if (!payload.message) return alert('Message cannot be empty');

  const res = await fetch('/api/entries', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  if (res.ok) {
    messageInput.value = '';
    nameInput.value = '';
    loadEntries();
  } else {
    const err = await res.json();
    alert(err.error || 'Failed to post');
  }
});

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

window.addEventListener('load', loadEntries);
