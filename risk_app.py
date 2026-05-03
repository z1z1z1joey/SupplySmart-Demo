import streamlit as st
import pandas as pd
import time

# 網頁基本設定
st.set_page_config(page_title="SupplySmart AI 風險聯動系統", layout="wide")
st.title("🚨 SupplySmart AI：風險預警與自動補料流程")

# --- 讀取資料庫 (Excel/CSV) ---
# 升級：讀取線上 Google Sheets 的寫法
@st.cache_data(ttl=60) # 設定每 60 秒強制重新抓取一次最新資料
def load_data():
    # 請把下面的網址換成你在步驟 1 複製的 Google Sheets CSV 網址
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQoxb_vbiOKkp-a229cpLDFXZl5G5VEO6nqnvSFwpK-l21CvCIY_wAfUfBGvAgu-MDGL4u0iYixAity/pub?gid=0&single=true&output=csv"
    
    # 加上 try-except 以防網路連線問題
    try:
        df = pd.read_csv(sheet_url)
        return df
    except Exception as e:
        st.error("無法連線至 Google Sheets，請檢查網址或網路設定。")
        return pd.DataFrame() # 回傳空表以防程式崩潰

df = load_data()

# --- 核心魔法：記住使用者走到哪一步 ---
if 'step' not in st.session_state:
    st.session_state.step = 1  # 預設從第 1 步開始

# 建立頂部進度條
steps = ["1. AI 風險發現", "2. 專家覆核", "3. 庫存衝擊模擬", "4. 執行補料"]
st.progress(st.session_state.step / 4)
st.caption(f"當前進度：{steps[st.session_state.step - 1]}")
st.divider()

# ==========================================
# 流程 1：AI 風險發現
# ==========================================
if st.session_state.step == 1:
    st.header("Step 1: AI 主動發現潛在風險")
    st.warning("⚠️ **高風險警報：蘇伊士運河物流擠塞預警 (AI 信心指數: 92.5%)**")
    st.write("最新衛星影像顯示排隊船隻數量異常增加。系統初步分析將影響以下料號的在途運輸：")
    
    # 篩選出受影響的料號 (假設是 IC-CTRL-77)
    affected_item = df[df['Item_ID'] == 'IC-CTRL-77']
    st.dataframe(affected_item)
    
    if st.button("進入專家覆核 ➡️"):
        st.session_state.step = 2
        st.rerun()

# ==========================================
# 流程 2：人工專家覆核
# ==========================================
elif st.session_state.step == 2:
    st.header("Step 2: 人工專家覆核")
    st.info("請根據 AI 提供的情報，判斷此風險是否具備真實性。")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("📄 **證據 1:**  Lloyd's List 即時海事報告")
        st.write("🛰️ **證據 2:** 蘇伊士運河入口衛星圖 (Live)")
    with col2:
        reason = st.text_area("請輸入覆核意見 (選填)：", "確認塞港屬實，需啟動緊急因應。")
        
        # 兩個按鈕代表不同決策
        if st.button("✅ 允許並啟動因應 (計算庫存)", type="primary"):
            st.session_state.step = 3
            st.rerun()
        if st.button("❌ 忽略此風險 (誤報)"):
            st.success("已標記為誤報，系統將持續監控。")
            st.session_state.step = 1 # 退回第一步
            time.sleep(2)
            st.rerun()

# ==========================================
# 流程 3：庫存衝擊模擬與補料建議
# ==========================================
elif st.session_state.step == 3:
    st.header("Step 3: 庫存衝擊與補料模擬")
    st.write("風險已確認！系統正動態調整安全庫存參數...")
    
    # 抓取原始資料
    item_data = df[df['Item_ID'] == 'IC-CTRL-77'].iloc[0]
    original_safety = item_data['Safety_Stock']
    
    # AI 模擬邏輯：因為塞港，安全庫存需要拉高 30%
    new_safety = int(original_safety * 1.3)
    current_stock = item_data['Current_Stock']
    shortage = new_safety - current_stock # 計算缺口
    
    col1, col2, col3 = st.columns(3)
    col1.metric("原安全庫存", f"{original_safety:,}")
    col2.metric("調整後安全庫存 (+30%)", f"{new_safety:,}", "風險緩衝")
    col3.metric("預估缺料缺口", f"{shortage:,}", "- 緊急", delta_color="inverse")
    
    st.write(f"💡 **AI 建議：** 建議立即向備援供應商 **{item_data['Supplier']}** 採購至少 **{shortage:,} PCS**。")
    
    if st.button("一鍵生成執行單據 ➡️", type="primary"):
        st.session_state.step = 4
        st.rerun()

# ==========================================
# 流程 4：聯動補料執行
# ==========================================
elif st.session_state.step == 4:
    st.header("Step 4: 庫存調整機制已發送")
    
    with st.spinner('正在透過 API 拋轉至 ERP 系統...'):
        time.sleep(2) # 模擬系統運算時間
        
    st.success("🎉 **執行成功！**")
    st.write("✅ 系統已自動更新 WMS (倉儲系統) 安全庫存參數。")
    st.write("✅ 已生成採購草稿：**PO-2024-URG-01** 並寄送 eRFQ 給供應商 TechSource。")
    
    if st.button("🔄 完成並返回首頁"):
        st.session_state.step = 1
        st.rerun()