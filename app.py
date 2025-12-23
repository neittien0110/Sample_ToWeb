import os
import urllib
import subprocess
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ==========================================
# 1. LỚP QUẢN LÝ TIẾN TRÌNH (CGI Manager)
# ==========================================
class CGIProcessManager:
    def __init__(self, folder_name="cgi-bin"):
        self.folder_name = folder_name
        # Đảm bảo thư mục tồn tại
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

    def run_process(self, script_name, type):
        """Thực thi script trong thư mục cgi-bin"""
        script_path = os.path.join(self.folder_name, script_name)
        
        if not os.path.exists(script_path):
            st.error(f"❌ Không tìm thấy tệp: {script_path}")
            return

        st.info(f"⏳ Đang thực thi: {script_name}...")
        try:
            # Gọi tiến trình hệ thống
            if type == True:
                result = subprocess.run(["python ", script_path], capture_output=True, text=True, check=True)
            else:
                result = subprocess.run([script_path], capture_output=True, text=True, check=True)
            st.success(f"✅ Hoàn thành: {script_name}")
            with st.expander("Xem kết quả (Output)"):
                st.code(result.stdout)
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Lỗi thực thi {script_name}: {e.stderr}")

    def render_sidebar_menus(self):
        """Hiển thị 2 Listbox với 5 menu-item mỗi cái"""
        st.sidebar.divider()
        st.sidebar.subheader("🛠️ Công cụ Hệ thống")

        # Listbox 1: Nhóm tiến trình A
        list_a = ["--- Chọn tiến trình ---", "task1.py", "send_email.py --to tiennd@soict.hust.edu.vn --subject \"Gui lan 1\" --body \"Chao ban\"", "task3.py", "task4.py", "task5.py"]
        selected_a = st.sidebar.selectbox("🚀 Nhóm tác vụ Xử lý:", list_a, key="list_a")
        if selected_a != "--- Chọn tiến trình ---":
            if st.sidebar.button(f"Chạy {selected_a}"):
                self.run_process(selected_a, True)

        st.sidebar.divider()
        
        # Listbox 2: Nhóm tiến trình B
        list_b = ["--- Chọn tiến trình ---", "dir.bat", "report2.py", "report3.py", "report4.py", "report5.py"]
        selected_b = st.sidebar.selectbox("📊 Nhóm tác vụ Báo cáo:", list_b, key="list_b")
        if selected_b != "--- Chọn tiến trình ---":
            if st.sidebar.button(f"Chạy {selected_b}"):
                self.run_process(selected_b, False)

# ==========================================
# 2. LỚP QUẢN LÝ DATABASE & MODULE BẢNG (Giữ nguyên từ bài trước)
# ==========================================
class DatabaseManager:
    def __init__(self):
        load_dotenv()
        self.engine = self._create_engine()

    def _create_engine(self):
        user, pw, srv = os.getenv("SQLSERVER_USER"), os.getenv("SQLSERVER_PASSWORD"), os.getenv("SQLSERVER_SERVER")
        db, drv, trust = os.getenv("SQLSERVER_DATABASE"), os.getenv("SQLSERVER_DRIVER"), os.getenv("SQLSERVER_TRUST")
        conn_str = f"DRIVER={{{drv}}};SERVER={srv};DATABASE={db};UID={user};PWD={pw};TrustServerCertificate={trust};"
        return create_engine(f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(conn_str)}")

    def fetch_data(self, table_name):
        return pd.read_sql(f"SELECT * FROM {table_name}", self.engine)

    def save_data(self, df, table_name):
        with self.engine.begin() as conn:
            conn.execute(text(f"DELETE FROM {table_name}"))
            df.to_sql(table_name, conn, if_exists='append', index=False)

class DataTableModule:
    def __init__(self, db_manager, table_name, display_name):
        self.db, self.table_name, self.display_name = db_manager, table_name, display_name

    def render_page(self):
        st.title(f"Quản lý {self.display_name}")
        df = self.db.fetch_data(self.table_name)
        df['time'] = pd.to_datetime(df['time'])

        # Filter & Editor
        search = st.text_input("🔍 Tìm kiếm theo tên:", key=f"s_{self.table_name}")
        filtered_df = df[df['name'].str.contains(search, case=False)] if search else df
        
        edited_df = st.data_editor(filtered_df, use_container_width=True, num_rows="dynamic")
        
        if st.button(f"💾 Lưu thay đổi {self.display_name}"):
            self.db.save_data(edited_df, self.table_name)
            st.success("Đã cập nhật!")

        # Plotly chart
        fig = px.line(edited_df.sort_values('time'), x='time', y='value', color='name', markers=True)
        st.plotly_chart(fig, use_container_width=True)

# --- 3. ĐỊNH NGHĨA CÁC CLASS CỤ THỂ ---
class LoaiHinhModule(DataTableModule):
    def __init__(self, db_manager): super().__init__(db_manager, "sx_loaihinh", "Loại hình")

class PhuTaiModule(DataTableModule):
    def __init__(self, db_manager): super().__init__(db_manager, "sx_phutai", "Phụ tải")

class MatTroiModule(DataTableModule):
    def __init__(self, db_manager): super().__init__(db_manager, "nltt_mtmn", "Mặt trời mái nhà")

## TODO New Class
# Thêm các bảng mới tại đây kế thừa từ DataTableModule

# ==========================================
# 4. BỘ ĐIỀU KHIỂN CHÍNH (WebApp)
# ==========================================
class WebApp:
    def __init__(self):
        st.set_page_config(page_title="Hệ thống Quản trị & Điều hành", layout="wide")
        self.db_manager = DatabaseManager()
        self.cgi_manager = CGIProcessManager() # Khởi tạo quản lý tiến trình
        
        self.modules = {
            "🏠 Trang chủ Dashboard": self.render_dashboard,
            "⚡ Loại hình Sản xuất": LoaiHinhModule(self.db_manager).render_page,
            "📊 Thông số Phụ tải": PhuTaiModule(self.db_manager).render_page,
            "📊 Mặt trời mái nhà": MatTroiModule(self.db_manager).render_page,
            ## TODO New Class (Add menu items here)
        }

    def render_dashboard(self):
        st.title("🚀 Hệ thống Giám sát Tổng quan")
        st.write("Sử dụng Menu bên trái để truy cập dữ liệu hoặc thực thi các tiến trình CGI.")

    def run(self):
        # 1. Hiển thị Navigation điều hướng bảng dữ liệu
        st.sidebar.title("🎮 Menu Dữ liệu")
        selection = st.sidebar.radio("Chọn bảng:", list(self.modules.keys()))
        
        # 2. Hiển thị 2 Listbox tiến trình (CGI) phía dưới sidebar
        self.cgi_manager.render_sidebar_menus()
        
        # 3. Thực thi nội dung trang chính
        self.modules[selection]()

if __name__ == "__main__":
    app = WebApp()
    app.run()