
activity_log = []

@app.get("/activity")
def get_activity():
    return {"activity": activity_log[-20:]}

@app.post("/activity")
def post_activity(data: dict):
    from datetime import datetime
    activity_log.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": data.get("message", "")
    })
    return {"ok": True}
