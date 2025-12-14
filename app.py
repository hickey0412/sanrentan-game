from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import random
import socket
import qrcode
import io
import base64
import string
import uuid

app = Flask(__name__)
app.secret_key = 'sanrentan_secret_key'

# --- お題データ（全40種） ---
THEME_DATA = [
    # --- 食べ物系 ---
    {"title": "お弁当のおかず", "choices": ["唐揚げ", "ハンバーグ", "卵焼き", "ウインナー", "エビフライ", "焼き鮭", "ミートボール"]},
    {"title": "好きなおにぎりの具", "choices": ["鮭", "梅", "ツナマヨ", "昆布", "明太子", "おかか", "高菜"]},
    {"title": "好きなお寿司のネタ", "choices": ["マグロ", "サーモン", "イクラ", "エビ", "イカ", "玉子", "ウニ"]},
    {"title": "最強のラーメンの味", "choices": ["醤油", "味噌", "塩", "豚骨", "担々麺", "つけ麺", "油そば"]},
    {"title": "味噌汁に入っていたら嬉しい具", "choices": ["豆腐", "わかめ", "なめこ", "あさり", "大根", "じゃがいも", "玉ねぎ"]},
    {"title": "カレーのトッピングといえば", "choices": ["カツ", "チーズ", "ゆで卵", "納豆", "ハンバーグ", "野菜", "エビフライ"]},
    {"title": "好きな鍋料理", "choices": ["すき焼き", "しゃぶしゃぶ", "キムチ鍋", "もつ鍋", "水炊き", "豆乳鍋", "おでん"]},
    {"title": "居酒屋の「とりあえず」一品", "choices": ["枝豆", "冷奴", "唐揚げ", "ポテトサラダ", "だし巻き卵", "軟骨の唐揚げ", "きゅうり"]},
    {"title": "コンビニのホットスナック", "choices": ["唐揚げくん", "ファミチキ", "アメリカンドッグ", "肉まん", "ピザまん", "焼き鳥", "コロッケ"]},
    {"title": "好きなパンの種類", "choices": ["食パン", "クロワッサン", "メロンパン", "カレーパン", "あんパン", "サンドイッチ", "フランスパン"]},
    {"title": "アイスクリームの味", "choices": ["バニラ", "チョコ", "抹茶", "ストロベリー", "クッキー＆クリーム", "ミント", "ソーダ"]},
    {"title": "ポテトチップスの味", "choices": ["うすしお", "コンソメ", "のり塩", "サワークリーム", "ブラックペッパー", "ピザポテト", "わさび"]},
    {"title": "卵料理といえば", "choices": ["目玉焼き", "スクランブルエッグ", "卵焼き", "オムライス", "親子丼", "ゆで卵", "茶碗蒸し"]},
    {"title": "人生最後の晩餐", "choices": ["母の料理", "高級ステーキ", "寿司", "ラーメン", "おにぎり", "水", "何も食べない"]},

    # --- ライフスタイル・趣味 ---
    {"title": "一番好きな季節・イベント", "choices": ["春（桜）", "夏（海・祭り）", "秋（紅葉・食）", "冬（雪・正月）", "クリスマス", "ハロウィン", "GW"]},
    {"title": "映画のジャンル", "choices": ["アクション", "コメディ", "ホラー", "SF", "恋愛", "ミステリー", "アニメ"]},
    {"title": "飼ってみたい動物", "choices": ["犬", "猫", "ハムスター", "ウサギ", "インコ", "爬虫類", "カワウソ"]},
    {"title": "今一番欲しい家電", "choices": ["ドラム式洗濯機", "ロボット掃除機", "食洗機", "大型テレビ", "高性能PC", "高級ドライヤー", "マッサージチェア"]},
    {"title": "1週間休みがあったら何する？", "choices": ["海外旅行", "国内旅行", "家でダラダラ", "ゲーム三昧", "部屋の片付け", "スキルアップ", "帰省"]},
    {"title": "ストレス発散方法", "choices": ["寝る", "食べる", "カラオケ", "買い物", "運動", "ゲーム", "友達と話す"]},

    # --- 恋愛・価値観 ---
    {"title": "初デートで行きたい場所", "choices": ["映画館", "水族館", "遊園地", "カフェ", "公園", "ショッピング", "居酒屋"]},
    {"title": "異性の好きな仕草・姿", "choices": ["笑顔", "真剣な顔", "髪をかきあげる", "袖まくり", "美味しそうに食べる", "香水の匂い", "スーツ/制服姿"]},
    {"title": "結婚相手に求める条件", "choices": ["性格", "顔", "経済力", "家事能力", "価値観", "ユーモア", "誠実さ"]},
    {"title": "一番やりたくない家事", "choices": ["皿洗い", "風呂掃除", "トイレ掃除", "ゴミ出し", "アイロンがけ", "草むしり", "料理"]},
    {"title": "学生時代に戻れるなら何する？", "choices": ["勉強する", "部活に打ち込む", "恋愛する", "もっと遊ぶ", "資格を取る", "友達を増やす", "今の知識で無双"]},

    # --- もしも・ファンタジー ---
    {"title": "欲しい特殊能力", "choices": ["空を飛ぶ", "透明人間", "時間停止", "テレポート", "心を読む", "怪力", "未来予知"]},
    {"title": "無人島に一つ持っていくなら", "choices": ["ナイフ", "ライター", "水", "スマホ", "テント", "親友", "布団"]},
    {"title": "宝くじで10億円当たったら", "choices": ["貯金する", "家を買う", "世界一周", "仕事辞める", "投資する", "寄付する", "豪遊する"]},
    {"title": "RPGの職業になるなら", "choices": ["勇者", "戦士", "魔法使い", "僧侶", "盗賊", "武闘家", "遊び人"]},
    {"title": "タイムマシンで行くなら", "choices": ["自分の過去", "自分の未来", "恐竜時代", "戦国時代", "100年後の未来", "親の若い頃", "江戸時代"]},

    # --- 追加お題（仕事・学校・サバイバル・その他） ---
    {"title": "一日だけ体験できるならこの職業", "choices": ["アイドル", "パイロット", "探偵", "外科医", "声優", "宇宙飛行士", "総理大臣"]},
    {"title": "学校行事で一番好きなのは", "choices": ["文化祭", "体育祭", "修学旅行", "合唱コンクール", "卒業式", "球技大会", "お昼休み"]},
    {"title": "ドラえもんの道具で欲しいのは", "choices": ["どこでもドア", "タケコプター", "タイムふろしき", "暗記パン", "人生やりなおし機", "スモールライト", "ほんやくコンニャク"]},
    {"title": "友達に一番求めること", "choices": ["優しさ", "面白さ(笑いのツボ)", "聞き上手", "趣味が合う", "金銭感覚", "フットワークの軽さ", "口が堅い"]},
    {"title": "ゾンビの世界で武器にするなら", "choices": ["日本刀", "ハンドガン", "チェーンソー", "金属バット", "弓矢", "火炎放射器", "素手(武術)"]},
    {"title": "スマホで一番使うアプリ", "choices": ["SNS (X/Insta)", "動画 (YouTube)", "連絡 (LINE)", "ゲーム", "地図・乗換案内", "カメラ・加工", "ニュース・天気"]},
    {"title": "ホテル選びで重視すること", "choices": ["朝食の美味しさ", "大浴場・サウナ", "部屋の広さ", "ベッドの寝心地", "Wi-Fi速度", "窓からの景色", "アメニティの質"]},
    {"title": "来世で生まれ変わるなら", "choices": ["大金持ちの人間", "愛される飼い猫", "大空を飛ぶ鳥", "深海の魚", "超イケメン/美女", "大樹(植物)", "今の自分"]},
    {"title": "実は一番怖いもの", "choices": ["お化け・心霊", "虫", "高い所", "失敗すること", "孤独", "人間", "将来"]},
    {"title": "部屋探しで譲れない条件", "choices": ["日当たり", "防音性", "駅近", "バストイレ別", "部屋の広さ", "築浅・綺麗さ", "家賃の安さ"]},
]

GAMES = {}

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def generate_room_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def calculate_score(correct_list, user_guess):
    if not correct_list or not user_guess: return 0, "判定不能"
    top3_correct = correct_list[:3]
    top3_guess = user_guess[:3]
    correct_set = set(top3_correct)
    guess_set = set(top3_guess)
    match_count = len(correct_set & guess_set)

    if top3_correct == top3_guess: return 6, "サンレンタン"
    if match_count == 3: return 4, "サンレンプク"
    if top3_correct[0] == top3_guess[0] and top3_correct[1] == top3_guess[1]: return 3, "ニレンタン"
    if match_count == 2: return 2, "プクプク"
    if top3_correct[0] == top3_guess[0]: return 1, "タン"
    return 0, "ハズレ"

@app.route('/')
def index():
    return render_template('lobby.html', step="create")

@app.route('/create_room', methods=['POST'])
def create_room():
    host_name = request.form.get('player_name')
    if not host_name: return redirect(url_for('index'))

    room_id = generate_room_id()
    local_ip = get_local_ip()
    join_url = f"http://{local_ip}:5000/join/{room_id}"
    
    img = qrcode.make(join_url)
    data_io = io.BytesIO()
    img.save(data_io, 'PNG')
    qr_b64 = base64.b64encode(data_io.getvalue()).decode('utf-8')

    host_uid = str(uuid.uuid4())
    session['user_id'] = host_uid
    session['room_id'] = room_id

    GAMES[room_id] = {
        "room_id": room_id,
        "status": "lobby", 
        "players": [{"uid": host_uid, "name": host_name, "score": 0, "guess": []}],
        "read_rules_players": [],
        "submitted_uids": [], # 回答済みプレイヤーのリスト
        "current_parent_idx": 0, 
        "theme": "",
        "choices": [],
        "phase": "lobby", 
        "parent_rank": [],
        "history": [],
        "qr_code": qr_b64,
        "join_url": join_url,
        "current_parent_name": "",
        "current_parent_uid": ""
    }
    return redirect(url_for('lobby', room_id=room_id))

@app.route('/lobby/<room_id>')
def lobby(room_id):
    if room_id not in GAMES: return redirect(url_for('index'))
    return render_template('lobby.html', step="wait", room=GAMES[room_id])

@app.route('/join/<room_id>', methods=['GET', 'POST'])
def join_room(room_id):
    if room_id not in GAMES: return "部屋がありません", 404
    
    if request.method == 'POST':
        name = request.form.get('player_name')
        if name:
            uid = str(uuid.uuid4())
            session['user_id'] = uid
            session['room_id'] = room_id
            GAMES[room_id]["players"].append({"uid": uid, "name": name, "score": 0, "guess": []})
            return redirect(url_for('game_wait', room_id=room_id))
    
    return render_template('join.html', room_id=room_id)

@app.route('/game_wait/<room_id>')
def game_wait(room_id):
    if room_id not in GAMES: return redirect(url_for('index'))
    return render_template('lobby.html', step="joined_wait", room=GAMES[room_id])

@app.route('/start_game/<room_id>')
def start_game(room_id):
    if room_id in GAMES:
        GAMES[room_id]["status"] = "playing"
        GAMES[room_id]["phase"] = "rules"
        GAMES[room_id]["read_rules_players"] = []
    return redirect(url_for('game', room_id=room_id))

@app.route('/finish_reading/<room_id>')
def finish_reading(room_id):
    if room_id not in GAMES: return redirect(url_for('index'))
    uid = session.get('user_id')
    game = GAMES[room_id]
    if uid and uid not in game["read_rules_players"]:
        game["read_rules_players"].append(uid)
    if len(game["read_rules_players"]) >= len(game["players"]):
        setup_new_round(room_id)
    return redirect(url_for('game', room_id=room_id))

def setup_new_round(room_id):
    if not THEME_DATA: return
    data = random.choice(THEME_DATA)
    game = GAMES[room_id]
    game["theme"] = data["title"]
    game["choices"] = data["choices"]
    game["phase"] = "parent_wait"
    game["parent_rank"] = []
    game["submitted_uids"] = [] # リセット
    
    players = game["players"]
    for p in players:
        p["guess"] = [] # 予想もリセット

    if not players: return
    idx = game["current_parent_idx"] % len(players)
    parent_player = players[idx]
    game["current_parent_name"] = parent_player["name"]
    game["current_parent_uid"] = parent_player["uid"]

@app.route('/game/<room_id>')
def game(room_id):
    if room_id not in GAMES: return redirect(url_for('index'))
    game_data = GAMES[room_id]
    current_parent_uid = game_data.get("current_parent_uid")
    my_uid = session.get('user_id')
    is_parent = (my_uid == current_parent_uid) if current_parent_uid else False
    has_read_rules = (my_uid in game_data.get("read_rules_players", []))
    
    # 自分がすでに回答済みかどうかのフラグ
    has_submitted = (my_uid in game_data.get("submitted_uids", []))

    return render_template('game_multi.html', state=game_data, is_parent=is_parent, my_uid=my_uid, has_read_rules=has_read_rules, has_submitted=has_submitted)

@app.route('/action/<room_id>', methods=['POST'])
def action(room_id):
    if room_id not in GAMES: return redirect(url_for('index'))
    game = GAMES[room_id]
    order_str = request.form.get("sorted_order")
    if not order_str: return redirect(url_for('game', room_id=room_id))
    
    order_list = order_str.split(",")
    action_type = request.form.get("type")
    
    my_uid = session.get('user_id')

    if action_type == 'parent':
        game["parent_rank"] = order_list
        game["phase"] = "child_wait"
    
    elif action_type == 'child':
        # 個人の予想を保存
        for p in game["players"]:
            if p["uid"] == my_uid:
                p["guess"] = order_list
                break
        
        # 回答済みリストに追加
        if my_uid not in game["submitted_uids"]:
            game["submitted_uids"].append(my_uid)
        
        # 全員(親以外)が回答したかチェック
        # プレイヤー総数 - 1(親)
        children_count = len(game["players"]) - 1
        if len(game["submitted_uids"]) >= children_count:
            # === 全員回答完了！集計処理 ===
            
            round_results = [] # 履歴表示用
            
            for p in game["players"]:
                if p["uid"] != game["current_parent_uid"]:
                    # 個別に採点
                    s, t = calculate_score(game["parent_rank"], p.get("guess", []))
                    p["score"] += s
                    p["last_result"] = t # 今回の結果を保存
                    p["last_points"] = s
                    
                    if s > 0:
                        round_results.append(f"{p['name']}: {t}(+{s})")
            
            # 履歴に追加
            log_entry = {
                "round": len(game["history"]) + 1,
                "theme": game["theme"],
                "parent": game["current_parent_name"],
                "details": ", ".join(round_results) if round_results else "全員ハズレ"
            }
            game["history"].append(log_entry)
            
            # 結果画面へ
            game["phase"] = "result"
            
        else:
            # まだ全員終わっていないので、画面遷移はしない（JSのリロード待ち）
            pass

    return redirect(url_for('game', room_id=room_id))

@app.route('/next_round/<room_id>')
def next_round(room_id):
    if room_id in GAMES:
        game = GAMES[room_id]
        total_players = len(game["players"])
        if total_players > 0:
            game["current_parent_idx"] = (game["current_parent_idx"] + 1) % total_players
            setup_new_round(room_id)
    return redirect(url_for('game', room_id=room_id))

@app.route('/api/status/<room_id>')
def api_status(room_id):
    if room_id not in GAMES: return jsonify({"error": "not found"})
    return jsonify(GAMES[room_id])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)