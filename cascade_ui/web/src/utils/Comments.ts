export function commentAdd(comment: string, pathParts: string[]) {
  return fetch('/v1/add_comment', {
    method: "post",
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({comment: comment, path_parts: pathParts})
  })
    .then(res => res.json())
    .catch(function (error) {
      console.log(error);
    });
}