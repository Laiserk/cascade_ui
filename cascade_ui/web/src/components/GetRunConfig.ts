import type {ConfigResponse} from "@/models/ConfigResponse";
import type { ModelPathSpec } from "@/models/PathSpecs";

export default async function GetRunConfig(path: ModelPathSpec): Promise<ConfigResponse> {
  return fetch('http://localhost:8000/v1/run_config', {
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
