"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import streamlit as st
import utils
import constants as ct



############################################################
# 共通サブ関数定義
############################################################
def show_mode_info(title: str, description: str, example: str):
    """
    モード別の説明表示を共通化した関数

    Parameters
    ----------
    title : str
        モード名（例：社内文書検索）
    description : str
        モードの概要説明
    example : str
        入力例を表示するサンプルテキスト
    """
    st.markdown(f"**「{title}」を選択中**")
    st.info(description)
    st.markdown(f"##### 💡入力例")
    st.code(example, wrap_lines=True)


############################################################
# メインレイアウト構成関数
############################################################
def display_main_layout():
    """
    アプリ全体のレイアウト構成
    左カラム：モード設定
    右カラム：メイン画面（チャット表示）
    """

    # ======== CSSでデザイン調整 ========
    st.markdown(
        """
        <style>
        /* 🌐 ページ全体のレイアウト幅調整 */
        .block-container {
            max-width: 100% !important;
            padding: 0;
        }

        /* ✅ 左カラムを固定表示にしてスクロールしても残る */
        [data-testid="column"]:first-of-type {
            position: fixed;
            /* Streamlit のヘッダー分だけ下にずらして上部の見切れを防止 */
            top: 3.5rem;
            left: 0;
            width: 25%; /* 左カラムの幅 */
            /* ヘッダー分を差し引いた高さにして内部でスクロールさせる */
            height: calc(100vh - 3.5rem);
            background-color: #e0e0e0 !important;
            padding: 2rem 1.5rem !important;
            border-right: 2px solid #cccccc;
            overflow-y: auto;
            z-index: 10;
        }

        /* ✅ 右カラムは左カラム分だけ右に寄せ、右カラム内部をスクロール可能にする */
        [data-testid="column"]:last-of-type {
            margin-left: 27%; /* 左カラムの幅より少し広め */
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            text-align: center;
            padding: 2rem 3rem !important;
            width: 73%;
            /* 右カラム自体をビューポート高さに合わせ、内部でスクロール */
            height: calc(100vh - 3.5rem);
            overflow-y: auto;
        }

        /* ✅ チャットエリア（右カラム内で中央配置） */
        .chat-area {
            width: 85%;
            max-width: 950px;
            text-align: left;
            /* 上に余白を取りつつ左右中央寄せにする */
            margin: 1rem auto 0 auto;
        }

        /* ✅ 入力欄の重複エラー対策と中央配置 */
        section[data-testid="stChatInput"] {
            max-width: 75%;
            margin: 2rem auto 0 auto;
            position: relative;
            z-index: 5;
        }

        /* ✅ スクロールバーのデザイン（グレーに） */
        [data-testid="column"]:first-of-type::-webkit-scrollbar {
            width: 6px;
        }
        [data-testid="column"]:first-of-type::-webkit-scrollbar-thumb {
            background-color: #bdbdbd;
            border-radius: 10px;
        }
        [data-testid="column"]:first-of-type::-webkit-scrollbar-track {
            background: #e0e0e0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ======== 左右カラム構成 ========
    left_col, right_col = st.columns([1.2, 3], gap="medium")

    # ==============
    # 左カラム: 利用目的設定欄
    # ==============
    with left_col:
        st.markdown('<div id="left-col">', unsafe_allow_html=True)

        st.markdown("### 利用目的")
        st.session_state.mode = st.radio(
            "利用目的を選択してください",
            [ct.ANSWER_MODE_1, ct.ANSWER_MODE_2],
            index=0,
            label_visibility="collapsed"
        )
        st.markdown("----")
        # 「社内文書検索」の機能説明
        st.markdown("**【「社内文書検索」を選択した場合】**")
        # 「st.info()」を使うと青枠で表示される
        st.info("入力内容と関連性が高い社内文書のありかを検索できます。")
        # 「st.code()」を使うとコードブロックの装飾で表示される
        # 「wrap_lines=True」で折り返し設定、「language=None」で非装飾とする
        st.code("【入力例】\n社員の育成方針に関するMTGの議事録", wrap_lines=True, language=None)

        # 「社内問い合わせ」の機能説明
        st.markdown("**【「社内問い合わせ」を選択した場合】**")
        st.info("質問・要望に対して、社内文書の情報をもとに回答を得られます。")
        st.code("【入力例】\n人事部に所属している従業員情報を一覧化して", wrap_lines=True, language=None)
        st.markdown("</div>", unsafe_allow_html=True)

    # ==============
    # 右カラム: メイン表示部分
    # ==============
    with right_col:
        st.markdown('<div id="right-col">', unsafe_allow_html=True)
        # 🟩チャット領域全体をラップ
        st.markdown('<div class="chat-area">', unsafe_allow_html=True)

        # --- 外部関数が存在する場合のみ実行 ---
        if "display_app_title" in globals():
            display_app_title()
        else:
            st.warning("⚠️ display_app_title() が未定義です。")

        if "display_initial_ai_message" in globals():
            display_initial_ai_message()

        if "display_conversation_log" in globals():
            display_conversation_log()

        st.markdown("</div>", unsafe_allow_html=True)

        # 🟩 ③ チャット入力欄（右カラム内に配置）
        # Streamlit の組み込みチャット入力はページ下部に常に表示されることがあるため、
        # ここではフォーム（st.form + st.text_input）を使って右カラム内にのみ入力欄を配置します。
        # 右カラムの入力欄の「上」に一時表示用のコンテナを用意する
        response_container = st.container()

        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input("", placeholder=ct.CHAT_INPUT_HELPER_TEXT, key="main_chat_text")
            submitted = st.form_submit_button("送信")

        st.markdown("</div>", unsafe_allow_html=True)

        # フォームが送信された場合のみ文字列を返す（未送信時は None）
        if submitted and user_input:
            return user_input, response_container
        return None, response_container


def display_app_title():
    """
    タイトル表示
    """
    st.markdown(f"## {ct.APP_NAME}")

def display_select_mode():
    """
    回答モードのラジオボタンを表示
    """
    # 回答モードを選択する用のラジオボタンを表示
    col1, col2 = st.columns([100, 1])
    with col1:
        # 「label_visibility="collapsed"」とすることで、ラジオボタンを非表示にする
        st.session_state.mode = st.radio(
            label="",
            options=[ct.ANSWER_MODE_1, ct.ANSWER_MODE_2],
            label_visibility="collapsed"
        )


def display_initial_ai_message():
    """
    AIメッセージの初期表示
    """
    with st.chat_message("assistant"):
        # 「st.success()」とすると緑枠で表示される
        st.success("こんにちは。私は社内文書の情報をもとに回答する生成AIチャットボットです。上記で利用目的を選択し、画面下部のチャット欄からメッセージを送信してください。")

        # 「st.warning()」を使うと黄色枠で表示される
        st.warning("⚠️具体的に入力したほうが期待通りの回答を得やすいです。")


def display_conversation_log():
    """
    会話ログの一覧表示
    """
    # 会話ログのループ処理
    for message in st.session_state.messages:
        # 「message」辞書の中の「role」キーには「user」か「assistant」が入っている
        with st.chat_message(message["role"]):

            # ユーザー入力値の場合、そのままテキストを表示するだけ
            if message["role"] == "user":
                st.markdown(message["content"])
            
            # LLMからの回答の場合
            else:
                # 「社内文書検索」の場合、テキストの種類に応じて表示形式を分岐処理
                if message["content"]["mode"] == ct.ANSWER_MODE_1:
                    
                    # ファイルのありかの情報が取得できた場合（通常時）の表示処理
                    if "no_file_path_flg" not in message["content"]:
                        # ==========================================
                        # ユーザー入力値と最も関連性が高いメインドキュメントのありかを表示
                        # ==========================================
                        # 補足文の表示
                        st.markdown(message["content"]["main_message"])

                        # 参照元のありかに応じて、適したアイコンを取得
                        icon = utils.get_source_icon(message['content']['main_file_path'])
                        # ページ番号があれば表示に含める
                        if "main_page_number" in message['content']:
                            st.success(f"{message['content']['main_file_path']} (ページNo.{message['content']['main_page_number']})", icon=icon)
                        else:
                            st.success(f"{message['content']['main_file_path']}", icon=icon)
                        
                        # ==========================================
                        # ユーザー入力値と関連性が高いサブドキュメントのありかを表示
                        # ==========================================
                        if "sub_message" in message["content"]:
                            # 補足メッセージの表示
                            st.markdown(message["content"]["sub_message"])

                            # サブドキュメントのありかを一覧表示
                            for sub_choice in message["content"]["sub_choices"]:
                                # 参照元のありかに応じて、適したアイコンを取得
                                icon = utils.get_source_icon(sub_choice['source'])
                                # 参照元ドキュメントのページ番号が取得できた場合にのみ、ページ番号を表示
                                if "page_number" in sub_choice:
                                    st.info(f"{sub_choice['source']} (ページNo.{sub_choice['page_number']})", icon=icon)
                                else:
                                    st.info(f"{sub_choice['source']}", icon=icon)
                
                # 「社内問い合わせ」の場合の表示処理
                else:
                    # LLMからの回答を表示
                    st.markdown(message["content"]["answer"])

                    # 参照元のありかを一覧表示
                    if "file_info_list" in message["content"]:
                        # 区切り線の表示
                        st.divider()
                        # 「情報源」の文字を太字で表示
                        st.markdown(f"##### {message['content']['message']}")
                        # ドキュメントのありかを一覧表示
                        for file_info in message["content"]["file_info_list"]:
                            # file_info は辞書（source, optional page_number）
                            source = file_info.get("source") if isinstance(file_info, dict) else str(file_info)
                            icon = utils.get_source_icon(source)
                            if isinstance(file_info, dict) and "page_number" in file_info:
                                st.info(f"{source} (ページNo.{file_info['page_number']})", icon=icon)
                            else:
                                st.info(source, icon=icon)


def display_search_llm_response(llm_response):
    """
    「社内文書検索」モードにおけるLLMレスポンスを表示

    Args:
        llm_response: LLMからの回答

    Returns:
        LLMからの回答を画面表示用に整形した辞書データ
    """
    # LLMからのレスポンスに参照元情報が入っており、かつ「該当資料なし」が回答として返された場合
    if llm_response["context"] and llm_response["answer"] != ct.NO_DOC_MATCH_ANSWER:

        # ==========================================
        # ユーザー入力値と最も関連性が高いメインドキュメントのありかを表示
        # ==========================================
        # LLMからのレスポンス（辞書）の「context」属性の中の「0」に、最も関連性が高いドキュメント情報が入っている
        main_file_path = llm_response["context"][0].metadata["source"]

        # 補足メッセージの表示
        main_message = "入力内容に関する情報は、以下のファイルに含まれている可能性があります。"
        st.markdown(main_message)
        
        # 参照元のありかに応じて、適したアイコンを取得
        icon = utils.get_source_icon(main_file_path)
        # content 作成（表示用データ）
        content = {
            "mode": ct.ANSWER_MODE_1,
            "answer": llm_response.get("answer", ""),
            "main_message": main_message,
            "main_file_path": main_file_path,
        }
        # ページ番号が取得できた場合のみ、ページ番号を追加
        if "page" in llm_response["context"][0].metadata:
            raw_page = llm_response["context"][0].metadata["page"]
            try:
                # 多くのローダーは0起点のページ番号を返すため表示時は+1する
                main_page_number = int(raw_page) + 1
            except Exception:
                main_page_number = raw_page
            content["main_page_number"] = main_page_number
            st.success(f"{main_file_path} (ページNo.{main_page_number})", icon=icon)
        else:
            st.success(f"{main_file_path}", icon=icon)
        # ==========================================
        # メインドキュメント以外で、関連性が高いサブドキュメントを格納する用のリストを用意
        sub_choices = []
        # 重複チェック用のリストを用意
        duplicate_check_list = []

        # ドキュメントが2件以上検索できた場合（サブドキュメントが存在する場合）のみ、サブドキュメントのありかを一覧表示
        # 「source_documents」内のリストの2番目以降をスライスで参照（2番目以降がなければfor文内の処理は実行されない）
        for document in llm_response["context"][1:]:
            # ドキュメントのファイルパスを取得
            sub_file_path = document.metadata["source"]

            # メインドキュメントのファイルパスと重複している場合、処理をスキップ（表示しない）
            if sub_file_path == main_file_path:
                continue
            
            # 同じファイル内の異なる箇所を参照した場合、2件目以降のファイルパスに重複が発生する可能性があるため、重複を除去
            if sub_file_path in duplicate_check_list:
                continue

            # 重複チェック用のリストにファイルパスを順次追加
            duplicate_check_list.append(sub_file_path)
            
            # ページ番号が取得できない場合のための分岐処理
            if "page" in document.metadata:
                # ページ番号を取得（表示は +1 する）
                try:
                    sub_page_number = int(document.metadata["page"]) + 1
                except Exception:
                    sub_page_number = document.metadata["page"]
                # 「サブドキュメントのファイルパス」と「ページ番号」の辞書を作成
                sub_choice = {"source": sub_file_path, "page_number": sub_page_number}
            else:
                # 「サブドキュメントのファイルパス」の辞書を作成
                sub_choice = {"source": sub_file_path}
            
            # 後ほど一覧表示するため、サブドキュメントに関する情報を順次リストに追加
            sub_choices.append(sub_choice)
        
        # サブドキュメントが存在する場合のみの処理
        if sub_choices:
            # 補足メッセージの表示
            sub_message = "その他、ファイルありかの候補を提示します。"
            st.markdown(sub_message)

            # サブドキュメントに対してのループ処理
            for sub_choice in sub_choices:
                # 参照元のありかに応じて、適したアイコンを取得
                icon = utils.get_source_icon(sub_choice['source'])
                # ページ番号が取得できない場合のための分岐処理
                if "page_number" in sub_choice:
                    # 「サブドキュメントのファイルパス」と「ページ番号」を表示
                    st.info(f"{sub_choice['source']}", icon=icon)
                else:
                # 参照元のありかに応じて、適したアイコンを取得
                    icon = utils.get_source_icon(sub_choice['source'])
                    st.info(f"{sub_choice['source']}", icon=icon)
                # ページ番号が取得できない場合のための分岐処理
                if "page_number" in sub_choice:
                    # 「サブドキュメントのファイルパス」と「ページ番号」を表示
                    st.info(f"{sub_choice['source']}", icon=icon)
                else:
                    st.info(f"{sub_choice['source']}", icon=icon)
        # サブドキュメントの情報は、取得できた場合にのみ追加
        if sub_choices:
            content["sub_message"] = sub_message
            content["sub_choices"] = sub_choices
    
    # LLMからのレスポンスに、ユーザー入力値と関連性の高いドキュメント情報が入って「いない」場合
    else:
        # 関連ドキュメントが取得できなかった場合のメッセージ表示
        st.markdown(ct.NO_DOC_MATCH_MESSAGE)

        # 表示用の会話ログに格納するためのデータを用意
        # - 「mode」: モード（「社内文書検索」or「社内問い合わせ」）
        # - 「answer」: LLMからの回答
        # - 「no_file_path_flg」: ファイルパスが取得できなかったことを示すフラグ（画面を再描画時の分岐に使用）
        content = {}
        content["mode"] = ct.ANSWER_MODE_1
        content["answer"] = ct.NO_DOC_MATCH_MESSAGE
        content["no_file_path_flg"] = True
    
    return content


def display_contact_llm_response(llm_response):
    """
    「社内問い合わせ」モードにおけるLLMレスポンスを表示

    Args:
        llm_response: LLMからの回答

    Returns:
        LLMからの回答を画面表示用に整形した辞書データ
    """
    # LLMからの回答を表示
    st.markdown(llm_response["answer"])

    # ユーザーの質問・要望に適切な回答を行うための情報が、社内文書のデータベースに存在しなかった場合
    if llm_response["answer"] != ct.INQUIRY_NO_MATCH_ANSWER:
        # 区切り線を表示
        st.divider()

        # 補足メッセージを表示
        message = "情報源"
        st.markdown(f"##### {message}")

        # 参照元のファイルパスの一覧を格納するためのリストを用意
        file_path_list = []
        file_info_list = []

        # LLMが回答生成の参照元として使ったドキュメントの一覧が「context」内のリストの中に入っているため、ループ処理
        for document in llm_response["context"]:
            # ファイルパスを取得
            file_path = document.metadata["source"]
            # ファイルパスの重複は除去
            if file_path in file_path_list:
                continue

            # ページ番号が取得できた場合のみ取得
            page_number_raw = document.metadata.get("page") if document.metadata else None
            # file_info は辞書で保持（ページ番号があれば表示用に +1 して含める）
            if page_number_raw is not None:
                try:
                    page_number = int(page_number_raw) + 1
                except Exception:
                    page_number = page_number_raw
                file_info_list.append({"source": file_path, "page_number": page_number})
            else:
                file_info_list.append({"source": file_path})
            # ファイル情報リストと重複チェックリストに追加
            file_path_list.append(file_path)

    # 表示用の会話ログに格納するためのデータを用意
    # - 「mode」: モード（「社内文書検索」or「社内問い合わせ」）
    # - 「answer」: LLMからの回答
    # - 「message」: 補足メッセージ
    # - 「file_info_list」: ファイル情報の一覧リスト
    content = {}
    content["mode"] = ct.ANSWER_MODE_2
    content["answer"] = llm_response["answer"]
    # 参照元のドキュメントが取得できた場合のみ
    if llm_response["answer"] != ct.INQUIRY_NO_MATCH_ANSWER:
        content["message"] = message
        content["file_info_list"] = file_info_list

    return content
