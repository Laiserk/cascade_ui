import type {Model} from "@/models/Model";

export default async function GetModel(repo: string, line: string, num: number): Promise<Model> {
  console.log('Calling GetModel with:', repo, line, num);
  return fetch('http://localhost:8000/v1/model', {
    method: "post",
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({repo: repo, line: line, num: num})
  })
    .then(res => res.json())
    .catch(function (error) {
      console.log(error);
    });
}
