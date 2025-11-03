"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# 1. ライブラリの読み込み
############################################################
# 「.env」ファイルから環境変数を読み込むための関数
from dotenv import load_dotenv
# ログ出力を行うためのモジュール
import logging
# streamlitアプリの表示を担当するモジュール
import streamlit as st
# （自作）画面表示以外の様々な関数が定義されているモジュール
import utils
# （自作）アプリ起動時に実行される初期化処理が記述された関数
from initialize import initialize
# （自作）画面表示系の関数が定義されているモジュール
import components as cn
# （自作）変数（定数）がまとめて定義・管理されているモジュール
import constants as ct

import traceback

############################################################
# 2. 設定関連
############################################################
# ブラウザタブの表示文言を設定
st.set_page_config(
    page_title=ct.APP_NAME
)

# ログ出力を行うためのロガーの設定
logger = logging.getLogger(ct.LOGGER_NAME)


############################################################
# 3. 初期化処理
############################################################
if "initialized" not in st.session_state:
    try:
        initialize()
        st.session_state.initialized = True
        logger.info(ct.APP_BOOT_MESSAGE)
    except Exception as e:
        # エラー特定用
        st.error("initialize()でエラーが発生しました。以下の内容を確認してください。")
        st.code(traceback.format_exc(), language="text")
        st.stop()

# try:
    # 初期化処理（「initialize.py」の「initialize」関数を実行）
    # initialize()
# except Exception as e:
    # エラー特定用
    # st.error("initialize()でエラーが発生しました。以下の内容を確認してください。")
    # st.code(traceback.format_exc(), language="text")
    
    # エラーログの出力
    # logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    # st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    # 後続の処理を中断
    
    # st.stop()

# アプリ起動時のログファイルへの出力
if not "initialized" in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)


############################################################
# 4. 初期表示
############################################################
# タイトル＋左右カラム構成の画面を表示
# 右カラム内の入力欄を表示し、その入力値と右カラム上部の一時表示用コンテナを受け取る
try:
    chat_message, response_container, conversation_container = cn.display_main_layout()
except Exception as e:
    # エラーログの出力
    logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    # 後続の処理を中断
    st.stop()


############################################################
# 7. チャット送信時の処理
############################################################
# 初期表示: 会話ログを会話用コンテナに描画（ここで最新のセッションを表示）
try:
    # 描画は conversation_container 内で行う
    with conversation_container:
        cn.display_conversation_log()
except Exception:
    # フォールバック: 直接呼ぶ
    cn.display_conversation_log()

if chat_message:
    # ==========================================
    # 7-1. ユーザーメッセージのログ保存（まず追加して画面に即時反映）
    # ==========================================
    logger.info({"message": chat_message, "application_mode": st.session_state.mode})
    # 先に会話ログの永続データにユーザーメッセージを追加することで、
    # 右カラムの会話ログにタイムラグなくユーザ発言を表示できます。
    st.session_state.messages.append({"role": "user", "content": chat_message})

    # ==========================================
    # 7-1-1. CSV（社員名簿）に関する構造化クエリのハンドリング
    # - 社員名簿のような構造化データはアプリ側で厳密に集計した方が正確
    # - st.session_state に保持されている csv_tables を参照して処理
    # ==========================================
    try:
        csv_tables = st.session_state.get("csv_tables", {})
        # 想定キー: '社員名簿.csv'
        roster_df = csv_tables.get("社員名簿.csv") if isinstance(csv_tables, dict) else None
        handled_by_app = False
        if roster_df is not None and isinstance(roster_df, (object,)):
            # 単純なキーワード判定（人事部、一覧、人数、社員名簿 など）
            q = chat_message.lower()
            keywords = ["社員名簿", "人事部", "部署", "一覧", "人数", "所属"]
            if any(k in q for k in keywords):
                # try to extract department name (e.g., '人事部')
                import re
                m = re.search(r"([\u4e00-\u9fff\w\-]{1,8}部)", chat_message)
                if m:
                    dept = m.group(1)
                    try:
                        filtered = roster_df[roster_df['部署'].astype(str).str.contains(dept, na=False)]
                    except Exception:
                        # カラム名が想定と異なる場合は日本語 '部署' を探す柔軟対応
                        col_candidates = [c for c in roster_df.columns if '部署' in c or '所属' in c]
                        if col_candidates:
                            col = col_candidates[0]
                            filtered = roster_df[roster_df[col].astype(str).str.contains(dept, na=False)]
                        else:
                            filtered = roster_df.iloc[0:0]
                else:
                    # 部署指定がなければ、もし '人数' を聞かれていれば全体の人数を返す
                    if '人数' in q or '何名' in q:
                        filtered = roster_df
                    else:
                        # '一覧' などの要求なら全件を返す
                        filtered = roster_df

                # 結果を組み立て（CSV 形式の表と要約）
                try:
                    row_count = len(filtered)
                    summary = f"該当レコード数: {row_count} 件。\n"
                    csv_text = filtered.to_csv(index=False)
                    # 表示用の回答は要約のみとし、表は conversation_container 内で DataFrame として表示する
                    final_answer = summary
                except Exception:
                    final_answer = "CSV の集計結果を生成できませんでした。"

                # content の形は display_conversation_log に合わせる
                content = {
                    "mode": ct.ANSWER_MODE_2,
                    "answer": final_answer,
                    "message": "情報源",
                    "file_info_list": [{"source": "社員名簿.csv"}]
                }

                # セッションに assistant の回答を追加して描画
                st.session_state.messages.append({"role": "assistant", "content": content})
                try:
                    with conversation_container:
                        cn.display_conversation_log()
                        # テーブル表示とダウンロードボタンを追加
                        try:
                            st.dataframe(filtered)
                            st.download_button("CSV をダウンロード", data=csv_text, file_name="社員名簿_filtered.csv", mime="text/csv")
                        except Exception:
                            # DataFrame 表示に失敗したら代替でテキストを表示
                            st.code(csv_text)
                except Exception:
                    cn.display_conversation_log()
                    # フォールバックで画面下部に生CSVを出す
                    try:
                        st.code(csv_text)
                    except Exception:
                        pass
                handled_by_app = True
        # もしアプリ側で処理できた場合は LLM 呼び出しをスキップ
        if handled_by_app:
            # skip LLM processing by jumping to next iteration of main loop
            # Streamlit scripts are re-run, so just return early from this flow
            # (we've already appended assistant response and re-rendered)
            pass_flag = True
        else:
            pass_flag = False
    except Exception as e:
        # 構造化処理で問題が発生したらログに残して通常パスへフォールバック
        logger.error(f"CSV handling error: {e}")
        pass_flag = False

    if pass_flag:
        # avoid calling LLM and continue app execution
        # we've already appended and rendered the assistant response, stop further execution
        st.stop()

    # ==========================================
    # 7-2. LLMからの回答取得（右カラム上部の response_container 内でスピナーを表示）
    # ==========================================
    try:
        if response_container is not None:
            with response_container:
                with st.spinner(ct.SPINNER_TEXT):
                    try:
                        llm_response = utils.get_llm_response(chat_message)
                    except Exception as e:
                        logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
                        st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
                        st.stop()
        else:
            with st.spinner(ct.SPINNER_TEXT):
                try:
                    llm_response = utils.get_llm_response(chat_message)
                except Exception as e:
                    logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
                    st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
                    st.stop()
    except Exception:
        # response_container の利用や表示中に想定外の例外が起きた場合はフォールバックして通常の取得処理を行う
        try:
            llm_response = utils.get_llm_response(chat_message)
        except Exception as e:
            logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
            st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            st.stop()

    # ==========================================
    # 7-3. LLMからの回答表示処理
    # ==========================================
    # - 取得済みの llm_response を表示用の content に変換（prepare_* に委譲）
    # - ユーザーが「全件表示」コマンドを送った場合は既存の会話ログを再描画して早期終了
    # - 通常は content を作成してセッションへ一度だけ追加し、会話ログを再描画する

    # 全件表示コマンド（例: 「すべて」「全件」）の判定
    show_all_trigger = any(keyword in chat_message for keyword in ["すべて", "全件", "全て表示", "全部見せて"])
    if show_all_trigger:
        st.session_state.show_all_related_docs = True
        st.success("📚 関連する全ての資料を表示します。")
        # 会話ログを再描画して処理を終了
        try:
            with conversation_container:
                cn.display_conversation_log()
            st.stop()
        except Exception:
            # 再描画に失敗した場合は通常処理にフォールバック
            pass

    # content の作成（描画は display_conversation_log に任せる）
    if st.session_state.mode == ct.ANSWER_MODE_1:
        content = cn.prepare_search_content(llm_response)
    else:
        content = cn.prepare_contact_content(llm_response)

    logger.info({"message": content, "application_mode": st.session_state.mode})

    # assistant の応答を一度だけ追加して会話ログを再描画
    st.session_state.messages.append({"role": "assistant", "content": content})
    try:
        with conversation_container:
            cn.display_conversation_log()
    except Exception:
        cn.display_conversation_log()


