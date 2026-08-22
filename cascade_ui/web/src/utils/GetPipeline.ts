import type {Pipeline} from "@/models/Pipeline";

export default async function GetPipeline(repo: string, line: string, ver: string): Promise<Pipeline> {
  return fetch('/v1/dataset_pipeline', {
    method: "post",
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({repo: repo, line: line, ver: ver})
  })
    .then(res => res.json())
    .catch(function (error) {
      console.log(error);
    });
}
