from fastapi import APIRouter, HTTPException, Response
from app.auth import supabase

router = APIRouter(tags=["delivery"])


@router.get("/widgets/{widget_id}/config")
def get_widget_config(widget_id: str, response: Response):
    res = supabase.table("widgets").select(
        "id, type, title, description, fields, button_text"
    ).eq("id", widget_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Widget not found")

    # short cache — config can change often, browsers should re-check soon
    response.headers["Cache-Control"] = "public, max-age=60"
    return res.data[0]


@router.get("/widget.js")
def get_widget_script(response: Response):
    js = """
(function () {
  var script = document.currentScript;
  var widgetId = new URL(script.src).searchParams.get("id");
  if (!widgetId) return;

  var apiBase = script.src.split("/widget.js")[0];

  fetch(apiBase + "/widgets/" + widgetId + "/config")
    .then(function (r) { return r.json(); })
    .then(function (config) {
      var container = document.createElement("div");
      container.innerHTML =
        '<form id="widget-form-' + widgetId + '">' +
        '<h3>' + config.title + '</h3>' +
        (config.description ? '<p>' + config.description + '</p>' : '') +
        '<input type="text" name="value" placeholder="Your info" required />' +
        '<input type="text" name="hp_field" style="display:none" tabindex="-1" autocomplete="off" />' +
        '<button type="submit">' + config.button_text + '</button>' +
        '</form>';
      script.parentNode.insertBefore(container, script.nextSibling);

      var form = container.querySelector("form");
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var data = Object.fromEntries(new FormData(form));
        fetch(apiBase + "/submissions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ widget_id: widgetId, data: data })
        })
          .then(function (r) { return r.json(); })
          .then(function () {
            container.innerHTML = "<p>Thanks!</p>";
          });
      });
    });
})();
"""
    # long cache — this file only changes on a version bump (new URL), so browsers can cache it forever
    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    response.media_type = "application/javascript"
    return Response(content=js, media_type="application/javascript", headers=response.headers)