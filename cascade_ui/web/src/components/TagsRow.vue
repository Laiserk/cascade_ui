<script setup lang="ts">
const props = defineProps<{ tags: Array<string> }>();
</script>

<template>
    <div class="tags-row" v-if="props?.tags && props.tags.length">
        <v-chip
        v-for="tag in props.tags"
        :key="tag"
        class="tag-chip"
        :style="{ height: '20px', 'font-size': '13px', 'margin-right': '8px', 'margin-bottom': '8px' }"
        background="#D9D7DD"
        text-color="#555"
        outlined
        >
        {{ tag }}
        </v-chip>
    </div>
</template>

<style scoped>
.tags-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
</style>
