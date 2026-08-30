import os
import shutil
import zipfile
import flet as ft

# ==================== 固定預設路徑設定 ====================
PATH_WECHAT = r"/storage/emulated/0/Download/WeChat"
PATH_CHANGBA = r"/storage/emulated/0/唱吧本地作品备份"
# =========================================================

def main(page: ft.Page):
    page.title = "唱吧音訊一鍵替換助手"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 25
    page.window_width = 480
    page.window_height = 680

    # UI 元件定義
    txt_wechat_path = ft.TextField(
        label="1. 來源：微信音訊",
        hint_text="請點擊下方【1: 選擇微信音訊mp3】",
        read_only=True
    )

    txt_changba_path = ft.TextField(
        label="2. 目標：唱吧備份資料夾",
        hint_text="請點擊下方【2: 選擇唱吧備份資料】",
        read_only=True
    )

    txt_status_text = ft.Text("等待操作...", size=18, weight="bold", color="grey")
    
    txt_status = ft.Container(
        content=txt_status_text,
        alignment=ft.Alignment(0, 0),
        padding=15,
        bgcolor="#1E1E1E",
        border_radius=8,
        border=ft.Border(
            top=ft.BorderSide(1, "#333333"),
            bottom=ft.BorderSide(1, "#333333"),
            left=ft.BorderSide(1, "#333333"),
            right=ft.BorderSide(1, "#333333")
        )
    )

    # ---------------- Flet Native File Pickers ----------------
    # 1. 微信音訊檔案選擇器
    def on_wechat_file_result(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            txt_wechat_path.value = e.files[0].path
            txt_status_text.value = "已選擇微信音訊"
            txt_status_text.color = "blue"
            page.update()

    file_picker_wechat = ft.FilePicker(on_result=on_wechat_file_result)
    page.overlay.append(file_picker_wechat)

    # 2. 唱吧資料夾選擇器
    def on_changba_dir_result(e: ft.FilePickerResultEvent):
        if e.path:
            # 使用者選取了資料夾
            txt_changba_path.value = e.path
            txt_status_text.value = "已選擇唱吧資料夾"
            txt_status_text.color = "blue"
            page.update()
        elif e.files and len(e.files) > 0:
            # 備用邏輯：若使用者點進資料夾選擇了裡面任一檔案，自動抓取該目錄
            txt_changba_path.value = os.path.dirname(e.files[0].path)
            txt_status_text.value = "已選擇唱吧資料夾"
            txt_status_text.color = "blue"
            page.update()

    file_picker_changba = ft.FilePicker(on_result=on_changba_dir_result)
    page.overlay.append(file_picker_changba)
    # ---------------------------------------------------------

    # 按鈕 1: 選擇微信音訊 mp3
    def btn_wechat_click(e):
        initial_dir = PATH_WECHAT if os.path.exists(PATH_WECHAT) else None
        file_picker_wechat.pick_files(
            dialog_title="選擇微信下載的 MP3 檔案",
            initial_directory=initial_dir,
            allowed_extensions=["mp3", "wav", "m4a", "aac"],
            file_type=ft.FilePickerFileType.AUDIO
        )

    # 按鈕 2: 選擇唱吧備份資料夾
    def btn_changba_click(e):
        initial_dir = PATH_CHANGBA if os.path.exists(PATH_CHANGBA) else None
        file_picker_changba.get_directory_path(
            dialog_title="選擇有編號的唱吧備份資料夾",
            initial_directory=initial_dir
        )

    # 按鈕 3: 執行解壓、自動改名替換與重新打包
    def btn_replace_click(e):
        source_audio = txt_wechat_path.value
        target_folder = txt_changba_path.value

        if not source_audio or not os.path.exists(source_audio):
            txt_status_text.value = "錯誤：請先選擇微信音訊！"
            txt_status_text.color = "red"
            page.update()
            return

        if not target_folder or not os.path.exists(target_folder):
            txt_status_text.value = "錯誤：請先選擇唱吧資料夾！"
            txt_status_text.color = "red"
            page.update()
            return

        target_zip = os.path.join(target_folder, "record_files.zip")
        if not os.path.exists(target_zip):
            txt_status_text.value = "錯誤：在該資料夾找不到 record_files.zip！"
            txt_status_text.color = "red"
            page.update()
            return

        extract_dir = os.path.join(target_folder, "temp_extract_record")

        try:
            # 1. 解壓縮 ZIP
            with zipfile.ZipFile(target_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # 2. 複製微信音訊進去，並自動改名為 v_recording.aac
            target_aac = os.path.join(extract_dir, "v_recording.aac")
            shutil.copyfile(source_audio, target_aac)

            # 3. 刪除舊的 ZIP，並將替換後的資料夾重新打包回 record_files.zip
            os.remove(target_zip)
            zip_base_name = os.path.join(target_folder, "record_files")
            shutil.make_archive(zip_base_name, 'zip', extract_dir)

            # 4. 清理暫存解壓資料夾
            shutil.rmtree(extract_dir)

            txt_status_text.value = "完美取代替換成功！！"
            txt_status_text.color = "green"
        except Exception as err:
            txt_status_text.value = f"替換失敗: {str(err)}"
            txt_status_text.color = "red"

        page.update()

    # 平行雙按鈕
    action_buttons_row = ft.Row(
        controls=[
            ft.ElevatedButton("1: 選擇微信音訊mp3", on_click=btn_wechat_click, expand=True, height=45),
            ft.ElevatedButton("2: 選擇唱吧備份資料", on_click=btn_changba_click, expand=True, height=45),
        ],
        spacing=12
    )

    # 頁面佈局組裝
    page.add(
        ft.Text("唱吧音訊一鍵替換工具", size=22, weight="bold"),
        ft.Divider(),
        
        txt_wechat_path,
        txt_changba_path,
        ft.Container(height=5),
        
        action_buttons_row,
        ft.Divider(),
        
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