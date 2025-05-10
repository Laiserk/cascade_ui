<script setup lang="ts">
import { ref } from "vue";
import {ItemComment} from "@/models/ItemComment";
import { commentAdd } from "@/utils/Comments";

const newComment = ref("");
const sendingComment = ref(false);

const props = defineProps<{
  comments: Array<ItemComment>,
  pathParts: string[],
  onCommentSent?: () => void
}>();

async function sendComment() {
  if (!newComment.value.trim() || sendingComment.value) return;
  sendingComment.value = true;
  try {
    await commentAdd(
      newComment.value,
      props.pathParts
    );
    // Reload model data to update comments
    newComment.value = "";
    if (typeof props.onCommentSent === 'function') {
      props.onCommentSent();
    }
  } finally {
    sendingComment.value = false;
  }
}
</script>

<template>
  <div class="comments-section">
    <div
        v-for="comment in props.comments"
        :key="comment.id"
        class="comment-bubble"
    >
        <div class="comment-header">
        <span class="comment-user">{{ comment.user }}@{{ comment.host }}</span>
        <span class="comment-timestamp">{{ comment.timestamp }}</span>
        </div>
        <div class="comment-message">
        {{ comment.message }}
        </div>
    </div>
    <div class="comment-input-row">
        <input
        v-model="newComment"
        :disabled="sendingComment"
        class="comment-input"
        placeholder="Add a comment..."
        @keyup.enter="sendComment"
        />
        <button
        class="comment-send-btn"
        :disabled="sendingComment || !newComment.trim()"
        @click="sendComment"
        >
        <span v-if="!sendingComment">Send</span>
        <span v-else>...</span>
        </button>
    </div>
  </div>
</template>

<style scoped>
.comments-section {
  flex: 0 1 30%;
  min-width: 220px;
  margin-top: 20px;
  margin-left: 40px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 1000px;
  overflow-y: auto;
}
.comment-bubble {
  background: #f4f4f4;
  border-radius: 12px;
  padding: 16px;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  font-size: 14px;
  color: #888;
}
.comment-user {
  font-weight: bold;
}
.comment-timestamp {
  font-size: 13px;
  color: #aaa;
}
.comment-message {
  font-size: 16px;
  color: #222;
  word-break: break-word;
}
.comment-input-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}
.comment-input {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 15px;
  font-family: Roboto;
  outline: none;
  background: #fff;
}
.comment-send-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  background: #deb841;
  color: #ffffff;
  font-weight: bold;
  font-size: 15px;
  cursor: pointer;
  transition: background 1s;
}
.comment-send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>