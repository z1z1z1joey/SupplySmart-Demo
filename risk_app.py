import streamlit as st
import pandas as pd
import time
import os

# ==========================================
# 網頁基本設定
# ==========================================
st.set_page_config(page_title="SupplySmart AI 整合系統", layout="wide")

# ==========================================
# 左側側邊欄 (導覽選單)
# ==========================================
st.sidebar.title("SupplySmart AI")
st.sidebar.caption("v1.2 整合測試版")
page = st.sidebar.radio(
    "請選擇功能模組：", 
    ["🚨 風險預警與自動補料", "📦 庫存管理中心 (CRUD)"]
)
st.sidebar.divider()
st.sidebar.info("💡 提示：風險預警讀取自 Google Sheets；庫存管理編輯本地 CSV。")

# ==========================================
# 模組 A：風險預警與自動補料流程 (來自你的程式碼)
# ==========================================
if page == "🚨 風險預警與自動補料":
    st.title("🚨 供應鏈風險預警與自動補料流程")

    # 讀取線上 Google Sheets
    @st.cache_data(ttl=60)
    def load_google_data():
        sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQoxb_vbiOKkp-a229cpLDFXZl5G5VEO6nqnvSFwpK-l21CvCIY_wAfUfBGvAgu-MDGL4u0iYixAity/pub?gid=0&single=true&output=csv"
        try:
            df = pd.read_csv(sheet_url)
            return df
        except Exception as e:
            st.error("無法連線至 Google Sheets，請檢查網址或網路設定。")
            return pd.DataFrame()

    df = load_google_data()

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
            affected_item = df[df['Item_ID'] == 'IC-CTRL-77']
            st.dataframe(affected_item)
        else:
            st.error("Google Sheets 中找不到 Item_ID 欄位或資料為空。")
        
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
            original_safety = item_data['Safety_Stock']
            new_safety = int(original_safety * 1.3)
            current_stock = item_data['Current_Stock']
            shortage = new_safety - current_stock
            
            col1, col2, col3 = st.columns(3)
            col1.metric("原安全庫存", f"{original_safety:,}")
            col2.metric("調整後安全庫存 (+30%)", f"{new_safety:,}", "風險緩衝")
            col3.metric("預估缺料缺口", f"{shortage:,}", "- 緊急", delta_color="inverse")
            
            st.write(f"💡 **AI 建議：** 建議立即向備援供應商 **{item_data['Supplier']}** 採購至少 **{shortage:,} PCS**。")
        except:
            st.error("讀取 Google Sheets 資料計算失敗，請確認欄位名稱正確。")
        
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
        st.write("✅ 已生成採購草稿：**PO-2024-URG-01** 並寄送 eRFQ 給供應商 TechSource。")
        
        if st.button("🔄 完成並返回首頁"):
            st.session_state.step = 1
            st.rerun()

# ==========================================
# 模組 B：庫存管理中心 (CRUD 本地版)
# ==========================================
elif page == "📦 庫存管理中心 (CRUD)":
    st.title("📦 庫存管理中心 (CRUD 實作)")
    
    csv_file = "inventory_local.csv"

    # 如果沒有檔案，自動生一個預設的
    if not os.path.exists(csv_file):
        default_data = pd.DataFrame({
            "Item_ID": ["IC-CTRL-77", "PM-99", "CBL-001"],
            "Item_Name": ["控制器模組", "電源管理 IC", "連接線套件"],
            "Current_Stock": [50000, 15000, 8000],
            "Safety_Stock": [45000, 20000, 10000],
            "Supplier": ["TechSource", "EuroConnect", "AsiaChip"]
        })
        default_data.to_csv(csv_file, index=False)
        st.info("💡 系統已自動建立本地資料庫 inventory_local.csv")

    # 讀取本地 CSV
    local_df = pd.read_csv(csv_file)

    st.markdown("📝 **操作指南：** 點擊數字直接修改、按表格下方 `+` 新增行、選取整行按 `Delete` 刪除。")

    # 互動式資料編輯器
    edited_df = st.data_editor(
        local_df,
        num_rows="dynamic",
        use_container_width=True,
        height=300
    )

    # 存檔按鈕
    if st.button("💾 將變更存回實體 CSV 檔案", type="primary"):
        edited_df.to_csv(csv_file, index=False)
        st.success("✅ 資料已成功寫入 `inventory_local.csv`！你可以打開該檔案檢查看看。")


    # ... (前面是原本的 CRUD 表格與儲存按鈕) ...
    # if st.button("💾 將變更存回實體 CSV 檔案", type="primary"):
    #     edited_df.to_csv(csv_file, index=False)
    #     st.success("✅ 資料已成功寫入 `inventory_local.csv`！你可以打開該檔案檢查看看。")

    st.divider() # 畫一條分隔線
    
    # ==========================================
    # 開發者後台：查看雲端生成的 CSV 檔案
    # ==========================================
    st.subheader("🛠️ 開發者後台：雲端檔案檢視")
    st.write("在 Streamlit 雲端環境中，雖然你看不到實體資料夾，但可以透過這裡確認檔案是否真的生成，並將其下載。")

    # 檢查檔案到底存不存在雲端主機上
    if os.path.exists(csv_file):
        st.success(f"檔案狀態：系統確認雲端主機上確實存在 `{csv_file}`")
        
        # 讀取剛剛存好的檔案內容
        with open(csv_file, "rb") as file:
            csv_data = file.read()
            
            # 建立一個下載按鈕
            st.download_button(
                label="📥 點我下載雲端上的 inventory_local.csv",
                data=csv_data,
                file_name="inventory_local_cloud_backup.csv",
                mime="text/csv",
            )
            
        # 在網頁上直接把 CSV 檔案的「原始碼」印出來給你看
        with st.expander("👀 點擊偷看 CSV 檔案內的原始純文字 (Raw Data)"):
            with open(csv_file, "r", encoding="utf-8") as f:
                raw_text = f.read()
                st.code(raw_text, language="csv")
    else:
        st.error(f"檔案狀態：目前雲端主機上找不到 `{csv_file}`。請先在上方表格隨便改個數字並按下儲存！")