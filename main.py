import os
import shutil
import zipfile
import flet as ft

PATH_WECHAT = r"/storage/emulated/0/Download/WeChat"
PATH_CHANGBA = r"/storage/emulated/0/唱吧本地作品备份"

def main(page: ft.Page):
    page.title = "唱吧音訊一鍵替換助手"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 480
    page.window_height = 750

    # 輸入框
    txt_wechat_path = ft.TextField(
        label="1. 來源：微信音訊檔案路徑",
        value=PATH_WECHAT,
        text_size=12
    )

    txt_changba_path = ft.TextField(
        label="2. 目標：唱吧備份資料夾路徑",
        value=PATH_CHANGBA,
        text_size=12
    )

    txt_status_text = ft.Text("等待操作...", size=16, weight="bold", color="grey")
    
    txt_status = ft.Container(
        content=txt_status_text,
        alignment=ft.Alignment(0, 0),
        padding=10,
        bgcolor="#1E1E1E",
        border_radius=8,
        border=ft.Border(
            top=ft.BorderSide(1, "#333333"),
            bottom=ft.BorderSide(1, "#333333"),
            left=ft.BorderSide(1, "#333333"),
            right=ft.BorderSide(1, "#333333")
        )
    )

    # 彈跳視窗：選擇微信 MP3 檔案
    def open_wechat_picker(e):
        folder_path = txt_wechat_path.value.strip()
        file_list_view = ft.ListView(expand=True, spacing=5, padding=10)
        
        def close_dlg():
            dlg.open = False
            page.update()

        try:
            target_dir = folder_path if os.path.isdir(folder_path) else os.path.dirname(folder_path)
            if os.path.exists(target_dir):
                files = os.listdir(target_dir)
                for f in files:
                    if f.endswith(('.mp3', '.m4a', '.aac', '.wav')):
                        full_path = os.path.join(target_dir, f)
                        def select_file(e, p=full_path):
                            txt_wechat_path.value = p
                            close_dlg()
                            page.update()
                        
                        file_list_view.controls.append(
                            ft.TextButton(text=f, on_click=select_file)
                        )
            else:
                file_list_view.controls.append(ft.Text("找不到指定的微信資料夾！"))
        except Exception as ex:
            file_list_view.controls.append(ft.Text(f"讀取錯誤: {str(ex)}"))

        dlg = ft.AlertDialog(
            title=ft.Text("1. 選擇微信音訊檔案"),
            content=ft.Container(content=file_list_view, width=350, height=280),
            actions=[ft.TextButton("關閉", on_click=lambda e: close_dlg())],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # 彈跳視窗：選擇唱吧備份資料夾
    def open_changba_picker(e):
        parent_path = os.path.dirname(txt_changba_path.value.strip())
        if not os.path.exists(parent_path):
            parent_path = "/storage/emulated/0/"
            
        folder_list_view = ft.ListView(expand=True, spacing=5, padding=10)
        
        def close_dlg():
            dlg.open = False
            page.update()

        try:
            if os.path.exists(parent_path):
                items = os.listdir(parent_path)
                for item in items:
                    full_path = os.path.join(parent_path, item)
                    if os.path.isdir(full_path):
                        def select_folder(e, p=full_path):
                            txt_changba_path.value = p
                            close_dlg()
                            page.update()
                        
                        folder_list_view.controls.append(
                            ft.TextButton(text=f"📁 {item}", on_click=select_folder)
                        )
            else:
                folder_list_view.controls.append(ft.Text("找不到上層目錄！"))
        except Exception as ex:
            folder_list_view.controls.append(ft.Text(f"讀取錯誤: {str(ex)}"))

        dlg = ft.AlertDialog(
            title=ft.Text("2. 選擇唱吧備份資料夾"),
            content=ft.Container(content=folder_list_view, width=350, height=280),
            actions=[ft.TextButton("關閉", on_click=lambda e: close_dlg())],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # 執行替換邏輯
    def btn_replace_click(e):
        source_audio = txt_wechat_path.value.strip()
        target_folder = txt_changba_path.value.strip()

        if not source_audio or not os.path.exists(source_audio):
            txt_status_text.value = "錯誤：找不到指定的微信音訊檔案！"
            txt_status_text.color = "red"
            page.update()
            return

        if not target_folder or not os.path.exists(target_folder):
            txt_status_text.value = "錯誤：找不到指定的唱吧資料夾！"
            txt_status_text.color = "red"
            page.update()
            return

        target_zip = os.path.join(target_folder, "record_files.zip")
        if not os.path.exists(target_zip):
            txt_status_text.value = "錯誤：找不到 record_files.zip！"
            txt_status_text.color = "red"
            page.update()
            return

        extract_dir = os.path.join(target_folder, "temp_extract_record")

        try:
            with zipfile.ZipFile(target_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            target_aac = os.path.join(extract_dir, "v_recording.aac")
            shutil.copyfile(source_audio, target_aac)

            os.remove(target_zip)
            zip_base_name = os.path.join(target_folder, "record_files")
            shutil.make_archive(zip_base_name, 'zip', extract_dir)
            shutil.rmtree(extract_dir)

            txt_status_text.value = "完美取代替換成功！！"
            txt_status_text.color = "green"
        except Exception as err:
            txt_status_text.value = f"替換失敗: {str(err)}"
            txt_status_text.color = "red"

        page.update()

    # 介面佈局
    page.add(
        ft.Text("唱吧音訊一鍵替換工具", size=20, weight="bold"),
        ft.Divider(),
        
        txt_wechat_path,
        ft.ElevatedButton("1. 選擇微信 MP3 檔案", on_click=open_wechat_picker, width=220),
        ft.Container(height=5),
        
        txt_changba_path,
        ft.ElevatedButton("2. 選擇唱吧備份資料夾", on_click=open_changba_picker, width=220),
        ft.Container(height=10),
        
        ft.ElevatedButton(
            "3: 執行取代替換", 
            on_click=btn_replace_click, 
            bgcolor="blue", 
            color="white", 
            height=50,
            width=450
        ),
        ft.Container(height=10),
        txt_status
    )

ft.app(target=main)