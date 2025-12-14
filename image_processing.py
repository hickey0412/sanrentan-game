from PIL import Image
import os

# 設定
input_path = 'static/image_0.png'      # 元画像のパス
output_path = 'static/bg_mosaic.jpg'   # 生成するモザイク画像のパス
block_size = 2                        # モザイクの目の粗さ（大きいほど粗い）

def create_mosaic_background():
    # staticフォルダがない場合は作成
    if not os.path.exists('static'):
        os.makedirs('static')
        print("エラー: staticフォルダに image_0.png を置いてください。")
        return

    try:
        # 画像を開く
        img = Image.open(input_path)
        print(f"画像を読み込みました: {input_path}")

        # --- 【修正点】RGBA(透明度あり)の場合、RGB(白背景)に変換する ---
        if img.mode == 'RGBA':
            # 元の画像と同じサイズの真っ白な画像を作成
            white_bg = Image.new('RGB', img.size, (255, 255, 255))
            # 透明部分の情報をマスクとして使い、元の画像を白背景に貼り付け
            white_bg.paste(img, mask=img.split()[3]) 
            img = white_bg
            print("透明情報を削除してRGBに変換しました。")
        # ---------------------------------------------------------

        # 元のサイズを取得
        orig_size = img.size
        width, height = orig_size

        # モザイクの目の粗さに合わせて縮小するサイズを計算
        # 少なくとも1x1ピクセルになるように調整
        small_width = max(1, width // block_size)
        small_height = max(1, height // block_size)

        # 画像を縮小（ニアレストネイバー法でピクセル感を出す）
        small_img = img.resize((small_width, small_height), Image.NEAREST)

        # 元のサイズに引き伸ばす（これでモザイクになる）
        mosaic_img = small_img.resize(orig_size, Image.NEAREST)

        # JPEGで保存（少し容量を軽くする）
        mosaic_img.save(output_path, 'JPEG', quality=85)
        print(f"モザイク画像を生成しました: {output_path}")

    except FileNotFoundError:
        print(f"エラー: {input_path} が見つかりません。staticフォルダに配置してください。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 実行
if __name__ == '__main__':
    create_mosaic_background()