# HƯỚNG DẪN

Website kết nối vào cơ sở dữ liệu và thực hiện 4 thao tác cơ bản: thêm xóa sửa xem với các bản dữ liệu. Ngoài ra còn có vẽ đồ thị số liệu

## Cài đặt các thư viện cần thiết 

```bash
pip install -r requirements.txt
```

## Chạy chương trình và sử dụng nhanh

Chạy lệnh sau để khởi chạy website trên máy cá nhân

```shell
streamlit run app.py
```

Trường hợp chạy trên máy chủ linux, muốn duy trì phiên làm việc liên tục

```shell
  nohup streamlit run app.py &
```

## Cấu trúc thư mục

File __.env__ có dạng

```yaml
SQLSERVER_USER=demo
SQLSERVER_PASSWORD=.........
SQLSERVER_SERVER=sqlserver.toolhub.app
SQLSERVER_DATABASE=demo
SQLSERVER_DRIVER=SQL Server
SQLSERVER_TRUST=yes
```