<script setup lang="ts">
import { Traceable } from '@/models/Traceable';
const props = defineProps<{ tr: Traceable }>();
</script>

<template>
<div v-if="props.tr && (props.tr.python_version && props.tr.git_commit && props.tr.user && props.tr.host && props.tr.cwd)" style="height:24px">
    <v-subheader style="margin-top: 32px;">ENVIRONMENT</v-subheader>
    <v-table v-if="props.tr">
        <tbody>
            <tr>
            <td><b>Python version</b></td>
            <td>{{ props.tr.python_version }}</td>
            </tr>
            <tr>
            <td><b>Git commit</b></td>
            <td>{{ props.tr.git_commit }}</td>
            </tr>
            <tr>
            <td><b>Host</b></td>
            <td>{{ props.tr.user }}@{{ props.tr.host }}</td>
            </tr>
            <tr>
            <td><b>CWD</b></td>
            <td>{{ props.tr.cwd }}</td>
            </tr>
        </tbody>
    </v-table>
</div>
</template>