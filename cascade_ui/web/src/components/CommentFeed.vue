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