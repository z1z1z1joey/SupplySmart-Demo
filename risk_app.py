import streamlit as st
import pandas as pd
import time
import gspread
from google.oauth2.service_account import Credentials
import feedparser
import google.generativeai as genai
import json

# ==========================================
# 網頁基本設定
# ==========================================
st.set_page_config(page_title="SupplySmart AI 整合系統", layout="wide")

# ==========================================
# 1. 驗證身分並連線至 Google Sheets (共用連線)
# ==========================================
@st.cache_resource
def init_connection():
    # 從 Streamlit Secrets 保險箱拿出金鑰
    skey = st.secrets["gcp_service_account"]
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(skey, scopes=scopes)
    client = gspread.authorize(credentials)
    return client

client = init_connection()

# ⚠️ 請把下面這行換成你真實的 Google Sheets 編輯網址
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Nc3WJ3vD7YvtY1s54pKwTMwZjNLDFMy1dh94Nu0BA9M/edit"

# ==========================================
# 左側側邊欄 (導覽選單)
# ==========================================
st.sidebar.title("SupplySmart AI")
st.sidebar.caption("v2.0 雲端資料庫完全體")
# ==========================================
# 模組 C：AI 即時情報雷達 (真實聯網分析)
# ==========================================
elif page == "📡 AI 即時情報雷達":
    st.title("📡 SupplySmart：即時 AI 情報雷達")
    st.write("點擊下方按鈕，系統將自動抓取 Yahoo 財經最新新聞，並交由 Gemini AI 逐條分析斷鏈風險。")

    # 讀取金鑰並設定 AI
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
    except Exception as e:
        st.error("請確認 Streamlit Secrets 中已設定 GEMINI_API_KEY")
        st.stop()

    def analyze_news_risk(title, summary):
        prompt = f"""
        你是一位專業的「全球供應鏈風險分析師」。
        請閱讀以下新聞標題與摘要，評估它是否對科技製造業、半導體或物流業造成斷鏈風險。
        
        新聞標題：{title}
        新聞摘要：{summary}
        
        請嚴格使用以下 JSON 格式輸出你的分析結果：
        {{
            "Risk_Level": "High" 或 "Medium" 或 "Low" 或 "None",
            "Location": "事件發生的國家或地區 (若無則填 Unknown)",
            "Keywords": ["受影響的產業", "材料", "或是零件名稱的陣列"],
            "Reason": "用一句話解釋為何有此風險"
        }}
        """
        try:
            response = model.generate_content(prompt)
            return json.loads(response.text) 
        except Exception as e:
            return {"Risk_Level": "Error", "Reason": str(e)}

    if st.button("🚀 啟動即時新聞掃描", type="primary"):
        rss_url = "https://tw.news.yahoo.com/rss/finance"
        
        with st.spinner("正在從網路抓取最新新聞..."):
            feed = feedparser.parse(rss_url)
            news_items = feed.entries[:3] # 取最新 3 篇
        
        st.success(f"✅ 成功抓取 {len(news_items)} 篇最新新聞！AI 正在進行語意分析...")
        cols = st.columns(3)
        
        for idx, entry in enumerate(news_items):
            with cols[idx]:
                st.markdown(f"**📰 {entry.title}**")
                with st.spinner("AI 判讀中..."):
                    analysis = analyze_news_risk(entry.title, entry.summary)
                    time.sleep(1.5) # 稍微暫停，避免打 API 太快
                
                risk_level = analysis.get("Risk_Level", "Unknown")
                if risk_level == "High":
                    st.error("🚨 判定：高風險 (High)")
                elif risk_level == "Medium":
                    st.warning("⚠️ 判定：中風險 (Medium)")
                elif risk_level == "Low":
                    st.info("🟢 判定：低風險 (Low)")
                else:
                    st.success("✅ 判定：無相關風險 (None)")
                    
                st.write(f"📍 **地區：** {analysis.get('Location')}")
                st.write(f"🔑 **關鍵字：** {', '.join(analysis.get('Keywords', []))}")
                st.caption(f"🧠 **理由：** {analysis.get('Reason')}")
                st.markdown(f"[閱讀原文]({entry.link})")
st.sidebar.divider()
st.sidebar.info("💡 提示：雙模組皆已串接 Google Sheets API，資料即時同步。")

# ==========================================
# 模組 A：風險預警與自動補料流程
# ==========================================
if page == "🚨 風險預警與自動補料":
    st.title("🚨 供應鏈風險預警與自動補料流程")

    # 即時讀取 Google Sheets 資料
    try:
        sheet = client.open_by_url(SHEET_URL).sheet1
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
    except Exception as e:
        st.error("無法連線至 Google Sheets，請檢查網址或 API 金鑰設定。")
        df = pd.DataFrame()

    # 狀態記憶
    if 'step' not in st.session_state:
        st.session_state.step = 1

    # 頂部進度條
    steps = ["1. AI 風險發現", "2. 專家覆核", "3. 庫存衝擊模擬", "4. 執行補料"]
    st.progress(st.session_state.step / 4)
    st.caption(f"當前進度：{steps[st.session_state.step - 1]}")
    st.divider()

    # 流程 1：AI 風險發現
    if st.session_state.step == 1:
        st.header("Step 1: AI 主動發現潛在風險")
        st.warning("⚠️ **高風險警報：蘇伊士運河物流擠塞預警 (AI 信心指數: 92.5%)**")
        st.write("最新衛星影像顯示排隊船隻數量異常增加。系統初步分析將影響以下料號的在途運輸：")
        
        if not df.empty and 'Item_ID' in df.columns:
            # 篩選受影響料號
            affected_item = df[df['Item_ID'] == 'IC-CTRL-77']
            if not affected_item.empty:
                st.dataframe(affected_item)
            else:
                st.warning("資料庫中目前找不到 'IC-CTRL-77' 這個料號。")
        else:
            st.error("Google Sheets 讀取失敗或資料為空。")
        
        if st.button("進入專家覆核 ➡️", type="primary"):
            st.session_state.step = 2
            st.rerun()

    # 流程 2：人工專家覆核
    elif st.session_state.step == 2:
        st.header("Step 2: 人工專家覆核")
        st.info("請根據 AI 提供的情報，判斷此風險是否具備真實性。")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("📄 **證據 1:**  Lloyd's List 即時海事報告")
            st.write("🛰️ **證據 2:** 蘇伊士運河入口衛星圖 (Live)")
        with col2:
            reason = st.text_area("請輸入覆核意見 (選填)：", "確認塞港屬實，需啟動緊急因應。")
            
            if st.button("✅ 允許並啟動因應 (計算庫存)", type="primary"):
                st.session_state.step = 3
                st.rerun()
            if st.button("❌ 忽略此風險 (誤報)"):
                st.success("已標記為誤報，系統將持續監控。")
                st.session_state.step = 1
                time.sleep(2)
                st.rerun()

    # 流程 3：庫存衝擊模擬與補料建議
    elif st.session_state.step == 3:
        st.header("Step 3: 庫存衝擊與補料模擬")
        st.write("風險已確認！系統正動態調整安全庫存參數...")
        
        try:
            item_data = df[df['Item_ID'] == 'IC-CTRL-77'].iloc[0]
            original_safety = int(item_data['Safety_Stock'])
            new_safety = int(original_safety * 1.3)
            current_stock = int(item_data['Current_Stock'])
            shortage = new_safety - current_stock
            
            col1, col2, col3 = st.columns(3)
            col1.metric("原安全庫存", f"{original_safety:,}")
            col2.metric("調整後安全庫存 (+30%)", f"{new_safety:,}", "風險緩衝")
            col3.metric("預估缺料缺口", f"{shortage:,}", "- 緊急", delta_color="inverse")
            
            supplier = item_data.get('Supplier', '備援供應商')
            st.write(f"💡 **AI 建議：** 建議立即向 **{supplier}** 採購至少 **{shortage:,} PCS**。")
        except Exception as e:
            st.error(f"計算失敗，請確認 Google Sheets 中包含 Safety_Stock 且數值正確。錯誤資訊：{e}")
        
        if st.button("一鍵生成執行單據 ➡️", type="primary"):
            st.session_state.step = 4
            st.rerun()

    # 流程 4：聯動補料執行
    elif st.session_state.step == 4:
        st.header("Step 4: 庫存調整機制已發送")
        with st.spinner('正在透過 API 拋轉至 ERP 系統...'):
            time.sleep(2)
        st.success("🎉 **執行成功！**")
        st.write("✅ 系統已自動更新 WMS (倉儲系統) 安全庫存參數。")
        st.write("✅ 已生成採購草稿：**PO-2024-URG-01** 並寄送 eRFQ 進行詢價。")
        
        if st.button("🔄 完成並返回首頁"):
            st.session_state.step = 1
            st.rerun()

# ==========================================
# 模組 B：庫存管理中心 (CRUD 雲端寫入版)
# ==========================================
elif page == "📦 庫存管理中心 (CRUD)":
    st.title("📦 庫存管理中心 (Google Sheets 同步版)")
    
    # 開啟試算表並讀取
    try:
        sheet = client.open_by_url(SHEET_URL).sheet1
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
    except Exception as e:
        st.error("讀取資料失敗，請確認 API 權限或網址正確。")
        st.stop()

    st.write("📝 **操作指南：** 表格內的修改將會直接同步到 Google Sheets！")

    # 互動編輯器
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True
    )

    # 寫回 Google Sheets
    if st.button("💾 將變更同步至 Google Sheets", type="primary"):
        with st.spinner("正在將資料寫回雲端，請稍候..."):
            try:
                # 為了避免格式跑掉，先清空舊資料
                sheet.clear()
                
                # 準備要寫入的新資料 (包含標題與內容)
                # 處理可能的 NaN 值為空字串，避免寫入出錯
                edited_df = edited_df.fillna("") 
                updated_data = [edited_df.columns.values.tolist()] + edited_df.values.tolist()
                
                # 更新試算表
                sheet.update(updated_data)
                st.success("✅ 資料庫已成功同步！你可以打開 Google Sheets 檢查看看。")
            except Exception as e:
                st.error(f"寫入失敗，請檢查設定：{e}")