from flask import Flask, request, jsonify
import sqlite3
import traceback


# Database
db = sqlite3.connect("minecraft.db", check_same_thread=False)
cur = db.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='register';")

if not cur.fetchall():
    cur.execute("""CREATE TABLE register (
        twitch_id INTEGER not null
            constraint register_pk
            primary key,
        twitch_nick VARCHAR(128) not null,
        minecraft_nick VARCHAR(128) not null
    );""")
    db.commit()
    print("Successfully created database")

del cur

# App
app = Flask(__name__)


@app.route("/register")
def register():
    args = request.args
    twitch_id = args.get('id')
    twitch_nick = args.get('nick')
    minecraft_nick = args.get('minecraft', '').lower()

    if not (twitch_id and twitch_nick and minecraft_nick):
        return jsonify({
            'status': False,
        }), 200

    try:
        cur = db.cursor()
        cur.execute(u"DELETE FROM register WHERE twitch_id = %s;" % twitch_id)
        cur.execute(u"INSERT INTO register VALUES (%s, '%s', '%s');" % (twitch_id, twitch_nick, minecraft_nick))
        db.commit()

        return jsonify({
            'status': True,
        }), 200
    except:
        print(traceback.format_exc())
        return jsonify({
            'status': False,
        }), 200


@app.route("/check")
def check():
    args = request.args
    nick = args.get('nick', '').lower()

    cur = db.cursor()
    cur.execute(u"SELECT twitch_id, twitch_nick FROM register WHERE minecraft_nick = '%s';" % nick)
    data = cur.fetchall()

    if data:
        twitch_id, twitch_nick = data[0]

        return jsonify({
            'status': True,
            'id': twitch_id,
            'nick': twitch_nick,
        }), 200
    else:
        return jsonify({
            'status': False,
        }), 200


if __name__ == "__main__":
    app.run('0.0.0.0', 8080, threaded=True)
