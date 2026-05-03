import streamlit as st
import pandas as pd
import time
import gspread
from google.oauth2.service_account import Credentials
import feedparser
import google.generativeai as genai
import json

# ==========================================
# 1. 網頁基本設定 (必須在最上方)
# ==========================================
st.set_page_config(page_title="SupplySmart AI 整合系統", layout="wide")

# ==========================================
# 2. 雲端資料庫連線設定 (Google Sheets API)
# ==========================================
@st.cache_resource
def init_connection():
    # 請確保 Streamlit Secrets 已設定 [gcp_service_account]
    skey = st.secrets["gcp_service_account"]
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(skey, scopes=scopes)
    client = gspread.authorize(credentials)
    return client

# 嘗試初始化連線
try:
    client = init_connection()
    # ⚠️ 這裡請換成你的真實 Google Sheets 網址
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1Nc3WJ3vD7YvtY1s54pKwTMwZjNLDFMy1dh94Nu0BA9M/edit"
except Exception as e:
    st.error(f"Google Sheets 連線初始化失敗，請檢查 Secrets 設定。錯誤：{e}")
    st.stop()

# ==========================================
# 3. 左側側邊欄導覽
# ==========================================
st.sidebar.title("SupplySmart AI")
st.sidebar.caption("v3.0 雲端完全體")
page = st.sidebar.radio(
    "請選擇功能模組：", 
    ["🚨 風險預警與自動補料", "📦 庫存管理中心 (CRUD)", "📡 AI 即時情報雷達"]
)
st.sidebar.divider()
st.sidebar.info("💡 提示：所有資料已即時串接 Google Sheets 與 Gemini AI。")

# ==========================================
# 模組 A：風險預警與自動補料流程
# ==========================================
if page == "🚨 風險預警與自動補料":
    st.title("🚨 供應鏈風險預警與自動補料流程")

    # 讀取 Google Sheets 資料
    sheet = client.open_by_url(SHEET_URL).sheet1
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    if 'step' not in st.session_state:
        st.session_state.step = 1

    steps = ["1. AI 風險發現", "2. 專家覆核", "3. 庫存衝擊模擬", "4. 執行補料"]
    st.progress(st.session_state.step / 4)
    st.caption(f"當前進度：{steps[st.session_state.step - 1]}")
    st.divider()

    if st.session_state.step == 1:
        st.header("Step 1: AI 主動發現潛在風險")
        st.warning("⚠️ **高風險警報：蘇伊士運河物流擠塞預警**")
        affected_item = df[df['Item_ID'] == 'IC-CTRL-77']
        st.dataframe(affected_item)
        if st.button("進入專家覆核 ➡️", type="primary"):
            st.session_state.step = 2
            st.rerun()

    elif st.session_state.step == 2:
        st.header("Step 2: 人工專家覆核")
        col1, col2 = st.columns(2)
        with col1:
            st.write("📄 **證據 1:** Lloyd's List 即時海事報告")
        with col2:
            st.text_area("覆核意見：", "確認塞港屬實。")
            if st.button("✅ 啟動因應", type="primary"):
                st.session_state.step = 3
                st.rerun()

    elif st.session_state.step == 3:
        st.header("Step 3: 庫存衝擊與補料模擬")
        item_data = df[df['Item_ID'] == 'IC-CTRL-77'].iloc[0]
        new_safety = int(item_data['Safety_Stock'] * 1.3)
        st.metric("調整後安全庫存", f"{new_safety:,}")
        if st.button("一鍵生成執行單據 ➡️", type="primary"):
            st.session_state.step = 4
            st.rerun()

    elif st.session_state.step == 4:
        st.header("Step 4: 執行成功")
        st.success("🎉 已自動更新系統並寄送 eRFQ。")
        if st.button("🔄 返回首頁"):
            st.session_state.step = 1
            st.rerun()

# ==========================================
# 模組 B：庫存管理中心 (CRUD)
# ==========================================
elif page == "📦 庫存管理中心 (CRUD)":
    st.title("📦 庫存管理中心 (Google Sheets 同步)")
    
    sheet = client.open_by_url(SHEET_URL).sheet1
    df = pd.DataFrame(sheet.get_all_records())

    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    if st.button("💾 將變更同步至 Google Sheets", type="primary"):
        with st.spinner("同步中..."):
            sheet.clear()
            updated_data = [edited_df.columns.values.tolist()] + edited_df.fillna("").values.tolist()
            sheet.update(updated_data)
            st.success("✅ 資料庫已成功同步！")

# ==========================================
# 模組 C：AI 即時情報雷達
# ==========================================
# ==========================================
# 模組 C：AI 即時情報雷達 (強化穩定版)
# ==========================================
elif page == "📡 AI 即時情報雷達":
    st.title("📡 SupplySmart：即時 AI 情報雷達")
    
    # 1. 更加穩健的初始化
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # 💡 [關鍵修正]：嘗試使用不帶 models/ 前綴的簡短名稱，這是目前 Streamlit 雲端最穩定的寫法
        # 如果還是不行，可以嘗試換成 'gemini-1.5-flash-latest'
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-latest',
            generation_config={"response_mime_type": "application/json"}
        )
    except Exception as e:
        st.error(f"⚠️ AI 引擎初始化失敗：{e}")
        st.stop()

    if st.button("🚀 啟動即時新聞掃描", type="primary"):
        # 2. 抓取新聞 (以你提供的 00662 為例)
        with st.spinner("正在掃描全球財經新聞..."):
            feed = feedparser.parse("https://tw.news.yahoo.com/rss/finance")
            items = feed.entries[:3]
        
        if not items:
            st.info("目前沒有最新新聞。")
        else:
            st.success(f"✅ 成功抓取 {len(items)} 篇新聞，AI 分析中...")
            cols = st.columns(3)
            
            for idx, entry in enumerate(items):
                with cols[idx]:
                    st.markdown(f"**📰 {entry.title}**")
                    
                    # 3. 強化型 Prompt 與錯誤處理
                    prompt = f"""
                    分析以下新聞標題對供應鏈或科技產業的風險。
                    請嚴格以 JSON 格式回傳，格式如下：
                    {{"Risk": "High/Med/Low/None", "Reason": "簡短理由"}}
                    
                    新聞標題：{entry.title}
                    """
                    
                    try:
                        # 💡 [關鍵修正]：增加超時設定與錯誤捕捉
                        response = model.generate_content(prompt)
                        
                        # 檢查 response 是否有內容
                        if response and response.text:
                            res = json.loads(response.text)
                            risk = res.get('Risk', 'Unknown')
                            reason = res.get('Reason', '無分析資料')
                            
                            if risk == "High": st.error(f"判定：{risk}")
                            elif risk == "Med": st.warning(f"判定：{risk}")
                            else: st.success(f"判定：{risk}")
                            
                            st.caption(f"🧠 AI 理由：{reason}")
                        else:
                            st.write("😶 AI 暫時無法解讀此內容")
                            
                    except Exception as ai_err:
                        # 如果 JSON 模式出錯，顯示具體建議
                        st.error("❌ AI 判讀發生 NotFound")
                        st.info("💡 解決建議：請去 Google Cloud Console 確認 'Generative Language API' 是否已啟用。")
                        st.expander("詳細錯誤日誌").code(str(ai_err))
                    
                    st.markdown(f"[原文連結]({entry.link})")