import type {Dataset} from "@/models/Dataset";

export default async function GetDataset(repo: string, line: string, ver: string): Promise<Dataset> {
  return fetch('http://localhost:8000/v1/dataset', {
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
