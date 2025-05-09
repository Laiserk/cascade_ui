import { LinePathSpec } from "@/models/PathSpecs";
import type { Router } from "vue-router";

export function openWorkspace(router: any) {
  router.push({ name: 'main'});
}

export function openRepo(router: Router, repoName: string) {
  router.push({ name: "repo", params: { repoName } });
}

export function openLine(router: Router, path: LinePathSpec) {
    if (path.lineType === "model_line") {
      router.push({ name: "model_line", params: {"repoName": path.repo, "lineName": path.line} });
    }
    else if (path.lineType === "data_line") {
      router.push({ name: "data_line", params: {"repoName": path.repo, "lineName": path.line} });
    }
    else {
      throw Error()
    }
  }
