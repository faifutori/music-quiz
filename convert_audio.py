import os
from pydub import AudioSegment

# --- 設定 ---
# AIFFファイルが入っているフォルダ
SOURCE_FOLDER = 'aiff_source'
# 変換後のMP3を保存するフォルダ
DESTINATION_FOLDER = 'converted_mp3_output'

# --- メイン処理 ---
def convert_aiff_to_mp3():
    # 出力フォルダがなければ作成する
    if not os.path.exists(DESTINATION_FOLDER):
        os.makedirs(DESTINATION_FOLDER)
        print(f"'{DESTINATION_FOLDER}' フォルダを作成しました。")

    print(f"'{SOURCE_FOLDER}' 内のAIFFファイルをMP3に変換します...")

    # ソースフォルダ内のファイルを一つずつ処理
    for filename in os.listdir(SOURCE_FOLDER):
        if filename.lower().endswith('.aiff'):
            aiff_path = os.path.join(SOURCE_FOLDER, filename)
            # 出力するファイル名（拡張子を.mp3に変更）
            mp3_filename = os.path.splitext(filename)[0] + '.mp3'
            mp3_path = os.path.join(DESTINATION_FOLDER, mp3_filename)

            try:
                # AIFFファイルを読み込み
                print(f"変換中: {filename}")
                audio = AudioSegment.from_file(aiff_path, format='aiff')

                # MP3形式で書き出し（ビットレートを指定して品質を調整）
                audio.export(mp3_path, format='mp3', bitrate='192k')

            except Exception as e:
                print(f"エラー: {filename} の変換に失敗しました - {e}")
    
    print("\n✅ 全ての変換処理が完了しました！")
    print(f"変換されたファイルは '{DESTINATION_FOLDER}' フォルダに保存されています。")


# --- プログラムの実行 ---
if __name__ == '__main__':
    convert_aiff_to_mp3()

    # python convert_audio.py