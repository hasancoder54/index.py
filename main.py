from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# Kullanıcı adından ID alma
def get_user_id_from_username(username):
    url = "https://users.roblox.com/v1/usernames/users"
    headers = {"Content-Type": "application/json"}
    data = {"usernames": [username], "excludeBannedUsers": False}
    try:
        res = requests.post(url, json=data, headers=headers)
        res.raise_for_status()
        users = res.json().get("data", [])
        if users:
            return users[0]["id"]
    except Exception as e:
        print(f"[HATA] Kullanıcı ID alınamadı: {e}")
    return None

# ID'den grup bilgilerini alma
def get_user_groups_and_roles(user_id, retries=3, delay=2):
    url = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Encoding": "gzip, deflate"
    }

    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[Uyarı] Yeniden deneniyor: {e}")
            time.sleep(delay)
    return None

# API endpoint
@app.route("/api/roblox-groups", methods=["GET"])
def roblox_groups():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Lütfen ?username=kullaniciadi şeklinde sorgula."}), 400

    user_id = get_user_id_from_username(username)
    if not user_id:
        return jsonify({"error": "Kullanıcı bulunamadı."}), 404

    data = get_user_groups_and_roles(user_id)
    if not data or "data" not in data:
        return jsonify({"error": "Grup verisi bulunamadı."}), 404

    groups_list = []
    for item in data["data"]:
        group = item.get("group", {})
        role = item.get("role", {})

        groups_list.append({
            "group_name": group.get("name", "Bilinmiyor"),
            "role_name": role.get("name", "Bilinmiyor"),
            "is_banned": item.get("isBanned", False)
        })

    return jsonify({
        "user_id": user_id,
        "username": username,
        "profile_link": f"https://www.roblox.com/users/{user_id}/profile",
        "group_count": len(groups_list),
        "groups": groups_list
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
