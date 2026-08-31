import os
import shutil
import zipfile
import platform
import subprocess
import flet as ft

PATH_WECHAT = r"/storage/emulated/0/Download/WeChat"
PATH_CHANGBA = r"/storage/emulated/0/唱吧本地作品备份"

def main(page: ft.Page):
    page.title = "唱吧音訊一鍵替換助手"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 480
    page.window_height = 750

    # 狀態提示文字（100% 還原您最原始的無事件、無報錯純文字）
    txt_status_text = ft.Text(
        "提示：Android 13 請先長按 App 圖示 -> 應用程式資訊 -> 權限 -> 勾選「允許管理所有檔案」才能正常運作。", 
        size=13, 
        weight="normal", 
        color="amber"
    )

    txt_status = ft.Container(
        content=txt_status_text,
        alignment=ft.Alignment(0, 0),
        padding=12,
        bgcolor="#1E1E1E",
        border_radius=8,
        border=ft.Border(
            top=ft.BorderSide(1, "#333333"),
            bottom=ft.BorderSide(1, "#333333"),
            left=ft.BorderSide(1, "#333333"),
            right=ft.BorderSide(1, "#333333")
        )
    )

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

    # 彈跳視窗：選擇微信 MP3 檔案
    def open_wechat_picker(e):
        file_list_view = ft.ListView(expand=True, spacing=5, padding=10)
        
        def close_dlg():
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("1. 選擇微信音訊檔案"),
            content=ft.Container(content=file_list_view, width=350, height=280),
            actions=[ft.TextButton("關閉", on_click=lambda e: close_dlg())],
        )

        try:
            folder_path = txt_wechat_path.value.strip()
            target_dir = folder_path if os.path.isdir(folder_path) else os.path.dirname(folder_path)
            
            if os.path.exists(target_dir):
                files = os.listdir(target_dir)
                audio_files = [f for f in files if f.endswith(('.mp3', '.m4a', '.aac', '.wav'))]
                
                if not audio_files:
                    file_list_view.controls.append(ft.Text("該目錄下目前沒有找到音訊檔案。"))
                else:
                    for f in audio_files:
                        full_path = os.path.join(target_dir, f)
                        def create_select_file_cb(p):
                            return lambda e: [txt_wechat_path.__setattr__('value', p), close_dlg(), page.update()]
                        
                        file_list_view.controls.append(
                            ft.TextButton(content=ft.Text(f"🎵 {f}"), on_click=create_select_file_cb(full_path))
                        )
            else:
                file_list_view.controls.append(ft.Text(f"❌ 找不到目錄！\n原因：路徑不存在，或手機未開啟「管理所有檔案」權限。"))
                txt_status_text.value = "❌ 讀取失敗！請確認是否已點擊執行按鈕進行權限跳轉。"
                txt_status_text.color = "red"
        
        except Exception as ex:
            file_list_view.controls.append(ft.Text(f"💥 系統阻擋或讀取錯誤:\n{str(ex)}"))
            txt_status_text.value = f"❌ 錯誤: {str(ex)}"
            txt_status_text.color = "red"

        page.dialog = dlg
        dlg.open = True
        page.update()

    # 彈跳視窗：選擇唱吧備份資料夾
    def open_changba_picker(e):
        folder_list_view = ft.ListView(expand=True, spacing=5, padding=10)
        
        def close_dlg():
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("2. 選擇唱吧備份資料夾"),
            content=ft.Container(content=folder_list_view, width=350, height=280),
            actions=[ft.TextButton("關閉", on_click=lambda e: close_dlg())],
        )

        try:
            parent_path = os.path.dirname(txt_changba_path.value.strip())
            if not os.path.exists(parent_path):
                parent_path = "/storage/emulated/0/"
                
            if os.path.exists(parent_path):
                items = os.listdir(parent_path)
                folders = [item for item in items if os.path.isdir(os.path.join(parent_path, item))]
                
                if not folders:
                    folder_list_view.controls.append(ft.Text("根目錄下沒有可顯示的資料夾。"))
                else:
                    for item in folders:
                        full_path = os.path.join(parent_path, item)
                        def create_select_folder_cb(p):
                            return lambda e: [txt_changba_path.__setattr__('value', p), close_dlg(), page.update()]
                        
                        folder_list_view.controls.append(
                            ft.TextButton(content=ft.Text(f"📁 {item}"), on_click=create_select_folder_cb(full_path))
                        )
            else:
                folder_list_view.controls.append(ft.Text("❌ 無法存取外部儲存根目錄，請確認已勾選檔案管理權限。"))
                txt_status_text.value = "❌ 讀取根目錄失敗！請確認權限是否開啟。"
                txt_status_text.color = "red"
        except Exception as ex:
            folder_list_view.controls.append(ft.Text(f"💥 讀取錯誤: {str(ex)}"))
            txt_status_text.value = f"❌ 錯誤: {str(ex)}"
            txt_status_text.color = "red"

        page.dialog = dlg
        dlg.open = True
        page.update()

    # 執行替換邏輯
    def btn_replace_click(e):
        # 💥【超安全原生對接點】：當在 Android 且無權限時，直接引導跳轉
        if page.platform == ft.PagePlatform.ANDROID and not os.path.exists("/storage/emulated/0/Download"):
            try:
                pkg = page.client_package_name if hasattr(page, "client_package_name") else "com.example.changbaapp"
                subprocess.Popen(["am", "start", "-a", "android.settings.MANAGE_APP_ALL_FILES_ACCESS_PERMISSION", "-d", f"package:{pkg}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                txt_status_text.value = "⏳ 偵測到無權限，已為您自動跳轉，請開啟後返回 App。"
                txt_status_text.color = "orange"
                page.update()
                return
            except:
                pass

        source_audio = txt_wechat_path.value.strip()
        target_folder = txt_changba_path.value.strip()

        if not source_audio or not os.path.exists(source_audio):
            txt_status_text.value = "錯誤：找不到指定的微信音訊檔案！或權限未開。"
            txt_status_text.color = "red"
            page.update()
            return

        if not target_folder or not os.path.exists(target_folder):
            txt_status_text.value = "錯誤：找不到指定的唱吧資料夾！或權限未開。"
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
        if os.path.exists(extract_dir):
            try:
                shutil.rmtree(extract_dir)
            except:
                pass

        try:
            txt_status_text.value = "正在處理中，請稍候..."
            txt_status_text.color = "orange"
            page.update()

            with zipfile.ZipFile(target_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            target_aac = os.path.join(extract_dir, "v_recording.aac")
            shutil.copyfile(source_audio, target_aac)

            os.remove(target_zip)
            
            zip_base_name = os.path.join(target_folder, "record_files")
            shutil.make_archive(zip_base_name, 'zip', extract_dir)
            
            shutil.rmtree(extract_dir)

            txt_status_text.value = "✨ 完美取代替換成功！！"
            txt_status_text.color = "green"
        except Exception as err:
            txt_status_text.value = f"❌ 替換失敗，原因: {str(err)}"
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