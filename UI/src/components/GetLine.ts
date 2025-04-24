import type {Line} from "@/models/Line";

export default async function GetLine(repo: string, line: string): Promise<Line> {
  return fetch('http://localhost:8000/v1/line', {
    method: "post",
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({repo: repo, line: line})
  })
    .then(res => res.json())
    .catch(function (error) {
      console.log(error);
    });
}
