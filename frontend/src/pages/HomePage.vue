<template>
  <div class="page upload-page">
    <div class="upload-header">
      <h1>Knowledge Base</h1>
      <p>Upload PDF documents to start asking questions.</p>
    </div>

    <!-- State: Knowledge base exists -->
    <div v-if="kbStatus" class="kb-status card">
      <div class="kb-info">
        <div class="kb-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
        </div>
        <div>
          <span class="kb-label">Indexed document</span>
          <span class="kb-uploaded-file">{{ kbStatus.filename }}</span>
          <span class="kb-meta">{{ kbStatus.chunks_indexed }} chunk{{ kbStatus.chunks_indexed !== 1 ? 's' : '' }} indexed</span>
        </div>
      </div>
      <div class="kb-actions">
        <router-link to="/chat" class="btn btn-primary">Ask Questions</router-link>
        <button class="btn btn-danger" :disabled="resetting" @click="handleReset">
          {{ resetting ? 'Resetting...' : 'Reset' }}
        </button>
      </div>
    </div>

    <!-- State: Upload zone -->
    <div
      v-if="!kbStatus"
      class="drop-zone card"
      :class="{ 'drop-zone--active': dragging, 'drop-zone--error': uploadError }"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf,application/pdf"
        class="drop-zone__input"
        @change="onFileChange"
      />

      <div v-if="!uploading" class="drop-zone__content">
        <div class="drop-zone__icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        </div>
        <p class="drop-zone__title">Drop your PDF here</p>
        <p class="drop-zone__hint">or click to browse &mdash; up to 50 MB</p>
      </div>

      <div v-else class="drop-zone__content">
        <div class="spinner"></div>
        <p class="drop-zone__title">Uploading &amp; indexing...</p>
        <p class="drop-zone__hint">{{ uploadingFilename }}</p>
      </div>
    </div>

    <!-- Upload error -->
    <div v-if="uploadError" class="error-banner">
      <span>{{ uploadError }}</span>
      <button class="error-dismiss" @click="uploadError = ''">&times;</button>
    </div>

    <!-- Upload success (no KB yet, second upload) -->
    <div v-if="uploadSuccess && !kbStatus" class="success-banner card">
      <div class="success-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      </div>
      <span>{{ uploadSuccess }}</span>
      <router-link to="/chat" class="btn btn-primary">Go to Chat</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// --- State ---
const fileInput = ref(null)
const dragging = ref(false)
const uploading = ref(false)
const uploadingFilename = ref('')
const uploadError = ref('')
const uploadSuccess = ref('')
const resetting = ref(false)
const kbStatus = ref(null)

// --- Lifecycle ---
onMounted(() => {
  checkKBStatus()
})

// --- Knowledge Base status ---
async function checkKBStatus() {
  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: '__status_check__' }),
    })
    // 503 = no KB; anything else means KB exists even if the question is odd
    if (resp.status === 503) {
      kbStatus.value = null
      return
    }
    // Try upload to probe (the upload endpoint returns KB info)
    probeUploadStatus()
  } catch {
    // Backend not running — ignore
  }
}

async function probeUploadStatus() {
  // A minimal probe: we can't query KB directly, so we infer from the
  // fact that /api/chat didn't 503.  In a real app we'd add GET /api/status.
  // For now, set a generic "knowledge base active" state.
  try {
    // Attempt a lightweight check — if chat didn't 503, KB exists
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: 'test' }),
    })
    if (resp.status !== 503 && resp.status !== 502) {
      const data = await resp.json()
      if (data.sources && data.sources.length > 0) {
        kbStatus.value = {
          filename: data.sources[0].filename || 'Unknown document',
          chunks_indexed: data.sources.length,
        }
      }
    }
  } catch {
    // ignore
  }
}

// --- Upload ---
function triggerFileInput() {
  if (uploading.value) return
  fileInput.value?.click()
}

function onDrop(e) {
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) processFile(file)
}

function onFileChange(e) {
  const file = e.target?.files?.[0]
  if (file) processFile(file)
}

async function processFile(file) {
  uploadError.value = ''
  uploadSuccess.value = ''

  // Validate
  if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
    uploadError.value = 'Only PDF files are accepted.'
    return
  }
  if (file.size > 50 * 1024 * 1024) {
    uploadError.value = 'File size exceeds the 50 MB limit.'
    return
  }

  uploading.value = true
  uploadingFilename.value = file.name

  try {
    const form = new FormData()
    form.append('file', file)

    const resp = await fetch('/api/upload', { method: 'POST', body: form })
    const data = await resp.json()

    if (!resp.ok || !data.success) {
      throw new Error(data.message || data.detail?.message || 'Upload failed.')
    }

    uploadSuccess.value = `"${data.data.original_name}" uploaded — ${data.data.chunks_indexed} chunk(s) indexed.`
    kbStatus.value = {
      filename: data.data.filename,
      chunks_indexed: data.data.chunks_indexed,
    }
  } catch (err) {
    uploadError.value = err.message || 'Upload failed. Please try again.'
  } finally {
    uploading.value = false
    uploadingFilename.value = ''

    // Reset file input so the same file can be re-selected
    if (fileInput.value) fileInput.value.value = ''
  }
}

// --- Reset ---
async function handleReset() {
  if (!confirm('Delete the current knowledge base? This cannot be undone.')) return

  resetting.value = true
  try {
    const resp = await fetch('/api/reset', { method: 'POST' })
    const data = await resp.json()

    if (!resp.ok || !data.success) {
      throw new Error(data.message || data.detail?.message || 'Reset failed.')
    }

    kbStatus.value = null
    uploadSuccess.value = ''
    uploadError.value = ''
  } catch (err) {
    alert(err.message || 'Reset failed.')
  } finally {
    resetting.value = false
  }
}
</script>
