<template>
  <div class="page chat-page">
    <div class="chat-header">
      <h1>Ask a Question</h1>
      <p>Ask questions about your uploaded documents.</p>
    </div>

    <!-- No KB warning -->
    <div v-if="noKB" class="warning-banner">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <span>No knowledge base found.</span>
      <router-link to="/" class="btn btn-primary">Upload a PDF first</router-link>
    </div>

    <!-- KB status bar -->
    <div v-if="kbFile" class="kb-status-bar">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
      </svg>
      <span>{{ kbFile }}</span>
    </div>

    <!-- Chat area: empty state -->
    <div v-if="!answer && !loading && !error" class="chat-empty">
      <div class="chat-empty__icon">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
      </div>
      <p>Type a question below to get started.</p>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-banner">
      <span>{{ error }}</span>
      <button class="error-dismiss" @click="error = ''">&times;</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-area card">
      <div class="spinner"></div>
      <p class="loading-text">Searching documents &amp; generating answer...</p>
    </div>

    <!-- Answer -->
    <div v-if="answer" class="answer-area">
      <div class="answer-card card">
        <div class="answer-label">Answer</div>
        <div class="answer-text" v-html="renderedAnswer"></div>
      </div>

      <!-- Sources -->
      <div v-if="sources.length > 0" class="sources-section">
        <h3 class="sources-title">Sources</h3>
        <div
          v-for="(src, i) in sources"
          :key="i"
          class="source-card card"
        >
          <div class="source-header">
            <div class="source-file">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              <span>{{ src.filename }}</span>
            </div>
            <span class="source-page">Page {{ src.page }}</span>
          </div>
          <p class="source-content">{{ src.content }}</p>
        </div>
      </div>
    </div>

    <!-- Question input -->
    <form v-if="!noKB" class="chat-input-area" @submit.prevent="askQuestion">
      <textarea
        ref="questionInput"
        v-model="question"
        class="chat-input"
        :disabled="loading"
        placeholder="Ask a question about your document..."
        rows="2"
        @keydown.enter.exact.prevent="askQuestion"
      ></textarea>
      <button
        type="submit"
        class="btn btn-primary chat-submit"
        :disabled="loading || !question.trim()"
      >
        <svg v-if="!loading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
        <span>Send</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'

// --- State ---
const question = ref('')
const questionInput = ref(null)
const loading = ref(false)
const error = ref('')
const answer = ref('')
const sources = ref([])
const noKB = ref(false)
const kbFile = ref('')

// --- Lifecycle ---
onMounted(async () => {
  await checkKB()
})

// --- KB detection ---
async function checkKB() {
  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: 'test' }),
    })
    if (resp.status === 503) {
      noKB.value = true
      return
    }
    const data = await resp.json()
    if (data.sources && data.sources.length > 0) {
      kbFile.value = data.sources[0].filename || ''
    }
  } catch {
    // Backend not running — show the warning
    noKB.value = true
  }
}

// --- Ask question ---
async function askQuestion() {
  const q = question.value.trim()
  if (!q || loading.value) return

  error.value = ''
  answer.value = ''
  sources.value = []
  loading.value = true
  question.value = ''

  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q }),
    })

    if (resp.status === 503) {
      noKB.value = true
      error.value = 'No knowledge base found. Please upload a PDF first.'
      return
    }

    const data = await resp.json()

    if (!resp.ok) {
      throw new Error(data.detail?.message || data.message || 'Request failed.')
    }

    answer.value = data.answer || 'No answer returned.'
    sources.value = data.sources || []

    await nextTick()
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
  } catch (err) {
    error.value = err.message || 'Failed to get an answer. Please try again.'
  } finally {
    loading.value = false
  }
}

// --- Render answer with highlighted citations ---
const renderedAnswer = computed(() => {
  if (!answer.value) return ''
  let html = answer.value
    // Escape HTML
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Highlight citation markers 【第N页】
    .replace(/【第(\d+)页】/g, '<mark class="citation-mark">【第$1页】</mark>')
    // Convert newlines to <br>
    .replace(/\n/g, '<br>')
  return html
})
</script>
