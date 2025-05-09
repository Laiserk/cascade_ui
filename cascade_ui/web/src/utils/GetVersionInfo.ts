import type {VersionInfo} from "@/models/VersionInfo";

export default async function GetVersionInfo(): Promise<VersionInfo> {
  return fetch('http://localhost:8000/v1/version', {
    method: "get",
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json"
    },
  })
    .then(res => res.json())
    .catch(function (error) {
      console.log(error);
    });
}
