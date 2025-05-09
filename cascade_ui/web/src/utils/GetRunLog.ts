import type {LogResponse} from "@/models/LogResponse";
import type { ModelPathSpec } from "@/models/PathSpecs";

export default async function GetRunLog(path: ModelPathSpec): Promise<LogResponse> {
  return fetch('http://localhost:8000/v1/run_log', {
    method: "post",
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json"
    },
    body: JSON.stringify(path)
  })
    .then(res => res.json())
    .catch(function (error) {
      console.log(error);
    });
}
