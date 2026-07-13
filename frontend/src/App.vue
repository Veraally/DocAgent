<template>
  <div id="app">
    <header class="app-header">
      <router-link to="/" class="app-logo">DocAgent</router-link>
      <nav class="app-nav">
        <router-link to="/">Home</router-link>
        <router-link to="/chat">Chat</router-link>
      </nav>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>
