import type {Repo} from "@/models/Repo";

export default async function GetRepo(path: string): Promise<Repo> {
  return fetch('http://localhost:8000/v1/repo', {
    method: "post",
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({repo: path})
  })
    .then(res => res.json())
    .catch(function (error) {
      console.log(error);
    });
}
