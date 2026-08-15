import type {Workspace} from "@/models/Workspace";

export default async function GetWorkspace(): Promise<Workspace> {
  return fetch('/v1/workspace', {
    method: "post",
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json"
    }
  })
    .then(res => res.json())
    .catch(function (error) {
      console.log(error);
    });
}
