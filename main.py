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
    chat_message, response_container = cn.display_main_layout()
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
if chat_message:
    # ==========================================
    # 7-1. ユーザーメッセージのログ保存（まず追加して画面に即時反映）
    # ==========================================
    logger.info({"message": chat_message, "application_mode": st.session_state.mode})
    # 先に会話ログの永続データにユーザーメッセージを追加することで、
    # 右カラムの会話ログにタイムラグなくユーザ発言を表示できます。
    st.session_state.messages.append({"role": "user", "content": chat_message})

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
    # 7-3. LLMからの回答表示（画面上で一時表示）
    # - display_* 関数は表示と同時に画面表示用の content を返す仕様のため、
    #   ローカルに content を受け取った後、セッションデータへ追加します。
    # ==========================================
    # ここでは右カラム上部の一時表示コンテナ（response_container）を使って
    # LLM応答を右カラム内の入力欄の上に表示します。response_container がない場合は
    # 既存の st.chat_message を使って代替表示します。
    try:
        if response_container is not None:
            with response_container:
                # 一時表示も chat_message でラップしてアカウントアイコン／吹き出し背景を付与する
                with st.chat_message("assistant"):
                    if st.session_state.mode == ct.ANSWER_MODE_1:
                        content = cn.display_search_llm_response(llm_response)
                    elif st.session_state.mode == ct.ANSWER_MODE_2:
                        content = cn.display_contact_llm_response(llm_response)
        else:
            # フォールバック
            if st.session_state.mode == ct.ANSWER_MODE_1:
                content = cn.display_search_llm_response(llm_response)
            elif st.session_state.mode == ct.ANSWER_MODE_2:
                content = cn.display_contact_llm_response(llm_response)
        logger.info({"message": content, "application_mode": st.session_state.mode})
    except Exception as e:
        logger.error(f"{ct.DISP_ANSWER_ERROR_MESSAGE}\n{e}")
        st.error(utils.build_error_message(ct.DISP_ANSWER_ERROR_MESSAGE), icon=ct.ERROR_ICON)
        st.stop()

    # ==========================================
    # 7-4. 会話ログへの追加（回答をセッションに保存）
    # - すでにユーザメッセージは追加済みのため、ここでは assistant のみ追加する
    # - 追加後に再描画して右カラムの会話ログに反映させる
    # ==========================================
    st.session_state.messages.append({"role": "assistant", "content": content})
    # 可能であれば即時再描画を試みる（古い/新しい Streamlit で属性が無い場合に備える）
    try:
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
    except Exception:
        # rerun が利用できない環境では何もしない（次のユーザ操作で再描画されます）
        pass


