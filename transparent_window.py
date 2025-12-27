import ctypes.wintypes, time, threading
import dearpygui.dearpygui as dpg


class TransparentViewport():
    """
    Makes the viewport completely transparent and click through-able but still allows you to interact with inner windows (no support for any of the built in tools, example dpg.show_style_editor)
    
    Args:
        ui (callable, optional): Function containing the ui within the viewport
        every_frame (callable, optional): Function containing code that gets ran on every dearpygui frame. Defaults to None.
        on_startup (callable, optional): Function that gets ran on viewport startup. Defaults to None.
        on_close (callable, optional): Function that runs on viewport close. Defaults to None.
        always_on_top (bool, optional): Should be topmost. Defaults to False.
        should_auto_refresh_windows (bool, optional): Checks every dearpygui frame for new windows that were created. Defaults to False.
        fps_limit (int, optional): Sets the framerate limit of the overlay. Defaults to None.
        overlay_name (str, optional): Window title. Defaults to 'Interactable Overlay'.
    """
    def __init__(self, ui=None, every_frame:callable=None, on_startup:callable=None, on_close:callable=None, always_on_top=False, should_auto_refresh_windows=False, fps_limit:int=None, overlay_name:str = 'Interactable Overlay'):
        self.overlay_name = overlay_name
        self.ui = ui
        self.overlay_hwnd = None
        self.always_on_top = always_on_top
        self.every_frame = every_frame
        self.on_startup = on_startup
        self.on_close = on_close
        self.in_any_window = False
        self.was_in_any_window = False
        self.should_auto_refresh_windows = should_auto_refresh_windows
        self.fps_limit = fps_limit
        

    def __set_transparent_window(self):
        class MARGINS(ctypes.Structure):
            _fields_ = [("cxLeftWidth", ctypes.c_int),
                        ("cxRightWidth", ctypes.c_int),
                        ("cyTopHeight", ctypes.c_int),
                        ("cyBottomHeight", ctypes.c_int)]

        margins = MARGINS(-1, -1, -1, -1)
        
        exstyle = ctypes.windll.user32.GetWindowLongW(self.overlay_hwnd, -20)
        exstyle |= 0x00080000 | 0x00000020
        ctypes.windll.user32.SetWindowLongW(self.overlay_hwnd, -20, exstyle)
        
        style = ctypes.windll.user32.GetWindowLongW(self.overlay_hwnd, -16)
        style |= 0x80000000
        ctypes.windll.user32.SetWindowLongW(self.overlay_hwnd, -16, style)

        ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(self.overlay_hwnd, margins)
        

    def start(self):
        """
        Starts up the overlay
        
        """
        dpg.create_context()
        dpg.create_viewport(title=self.overlay_name, y_pos=0, x_pos=0, decorated=False, always_on_top=self.always_on_top, clear_color=(0,0,0,0))
        dpg.setup_dearpygui()
        dpg.show_viewport()
        self.overlay_hwnd = ctypes.windll.user32.GetActiveWindow()
        self.__set_transparent_window()
        if self.on_startup:
            self.on_startup()
        if self.ui:
            self.ui()
        dpg.maximize_viewport()
        
        self.in_any_window = False

        GetCursorPos = ctypes.windll.user32.GetCursorPos
        GetCursorPos.argtypes = [ctypes.wintypes.LPPOINT]
        GetCursorPos.restype  = ctypes.wintypes.BOOL

        GetWindowLongW = ctypes.windll.user32.GetWindowLongW
        SetWindowLongW = ctypes.windll.user32.SetWindowLongW
        
        windows = dpg.get_windows()

        mouse_pos = ctypes.wintypes.POINT()

        last_time = time.perf_counter()

        if self.fps_limit:
            frame_time = 1 / self.fps_limit

        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            
            if self.fps_limit:
                current_time = time.perf_counter()

                delta_time = current_time - last_time

                if delta_time >= frame_time:
                    time.sleep(max(0, frame_time - delta_time))

            if self.every_frame:
                self.every_frame()

            if self.should_auto_refresh_windows:
                windows = dpg.get_windows()

            GetCursorPos(ctypes.byref(mouse_pos))
            self.in_any_window = False

            for i in windows:
                try:

                    if not dpg.is_item_visible(i):
                        continue

                    x0, y0 = dpg.get_item_pos(i)
                    width, height = dpg.get_item_rect_size(i)

                    inside = (dx := mouse_pos.x - x0) >= 0 and dx <= width and (dy := mouse_pos.y - y0) >= 0 and dy <= height

                    if inside:
                        self.in_any_window = True
                        break

                except:
                    pass


            if self.in_any_window != self.was_in_any_window: # Make it so that we only ever change the window properties when the users cursor moves in or out of the window rect

                style = GetWindowLongW(self.overlay_hwnd, -20)

                if self.in_any_window:
                    SetWindowLongW(self.overlay_hwnd, -20, style & ~0x20)
                else:
                    SetWindowLongW(self.overlay_hwnd, -20, style | 0x20)

                self.was_in_any_window = self.in_any_window # Update our variable so our first if statement will return True to then be run again
                
        
        if self.on_close:
            self.on_close()
        dpg.destroy_context()




class TransparentViewportV2():
    """
    Makes the viewport completely transparent and click through-able but still allows you to interact with inner windows while still allowing you to interact with the built in tools

    Side effects: Causes everything to be roughly half of your monitors hz (may be different per windows version)

    Args:
        ui (_type_): Function containing the ui within the viewport
        on_startup (callable, optional): Function that gets ran on viewport startup. Defaults to None.
        on_close (callable, optional): Function that runs on viewport close. Defaults to None.
        always_on_top (bool, optional): Should be topmost. Defaults to False.
        overlay_name (str, optional): Window title. Defaults to 'Interactable Overlay'.

    """
    def __init__(self, ui, on_startup:callable=None, on_close:callable=None, always_on_top=False, overlay_name:str = 'Interactable Overlay'):
        self.overlay_name = overlay_name
        self.ui = ui
        self.overlay_hwnd = None
        self.always_on_top = always_on_top
        self.on_startup = on_startup
        self.on_close = on_close

    def __set_transparent_window(self):
        exstyle = ctypes.windll.user32.GetWindowLongW(self.overlay_hwnd, -20)
        exstyle |= 0x00080000
        ctypes.windll.user32.SetWindowLongW(self.overlay_hwnd, -20, exstyle)
        ctypes.windll.user32.SetLayeredWindowAttributes(self.overlay_hwnd, 0, 0, 1)

        

    def start(self):
        """
        Starts up the overlay
        
        """
        dpg.create_context()
        dpg.create_viewport(title=self.overlay_name, y_pos=0, x_pos=0, decorated=False, always_on_top=self.always_on_top, clear_color=(0,0,0))
        dpg.setup_dearpygui()
        dpg.show_viewport()
        self.overlay_hwnd = ctypes.windll.user32.GetActiveWindow()
        self.__set_transparent_window()
        if self.on_startup:
            self.on_startup()
        self.ui()
        dpg.maximize_viewport()
        dpg.start_dearpygui()
        if self.on_close:
            self.on_close()
        dpg.destroy_context()




class Overlay():
    """
    Creates a click through-able overlay in the specified parent window, if no parent window is specified then it just runs as a topmost window
    
    Args:
        target_window (str, optional): Target windows title. Defaults to None.
        ui (_type_, optional): Function containing the ui within the viewport. Defaults to None.
        overlay_name (str, optional): Title of the overlay window. Defaults to 'Generic overlay'.

    """
    def __init__(self, target_window:str=None, ui=None, overlay_name:str = 'Generic overlay'):
        self.target_window = target_window
        self.overlay_name = overlay_name
        self.ui = ui
        self.target_window_hwnd = None
        self.overlay_hwnd = None
        self.initialized = False

    def start(self, threaded=True):
        """
        Starts up the overlay

        Args:
            threaded (bool, optional): Specifies to start dpg in a seperate daemon thread. Defaults to True.
        """
        if threaded:
            ui_thread = threading.Thread(target=self.__initialize_ui)
            ui_thread.daemon = True
            ui_thread.start()
        else:
            self.__initialize_ui()
        
        while not self.initialized:
            time.sleep(0.001)
        
        if self.target_window and not (self.target_window_hwnd or not self.overlay_hwnd):
            raise Exception("Failed to initialize handles")
        

    def __set_transparent_window(self):
        class MARGINS(ctypes.Structure):
            _fields_ = [("cxLeftWidth", ctypes.c_int),
                        ("cxRightWidth", ctypes.c_int),
                        ("cyTopHeight", ctypes.c_int),
                        ("cyBottomHeight", ctypes.c_int)]

        margins = MARGINS(-1, -1, -1, -1)
        exstyle = ctypes.windll.user32.GetWindowLongW(self.overlay_hwnd, -20)
        exstyle |= 0x00080000 | 0x00000020 | 0x00000080
        exstyle &= ~(0x00040000)
        ctypes.windll.user32.SetWindowLongW(self.overlay_hwnd, -20, exstyle)

        ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(self.overlay_hwnd, margins)

        if self.target_window_hwnd:
            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(self.target_window_hwnd, ctypes.byref(rect))

            ctypes.windll.user32.SetParent(self.overlay_hwnd, self.target_window_hwnd)
            
            dpg.set_viewport_width(rect.right - rect.left)
            dpg.set_viewport_height(rect.bottom - rect.top)
        else:
            dpg.set_viewport_width(ctypes.windll.user32.GetSystemMetrics(0))
            dpg.set_viewport_height(ctypes.windll.user32.GetSystemMetrics(1))
        


    def __initialize_ui(self):
        dpg.create_context()
        dpg.create_viewport(title=self.overlay_name, y_pos=0, x_pos=0, decorated=False, always_on_top=True, clear_color=(0,0,0,0))
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.render_dearpygui_frame() # if we dont render it before hand then we cant get its hwnd even after doing dpg.show_viewport()
        
        self.overlay_hwnd = ctypes.windll.user32.FindWindowW(None, self.overlay_name)
        if self.target_window:
            self.target_window_hwnd = ctypes.windll.user32.FindWindowW(None, self.target_window)

        self.__set_transparent_window()
        self.initialized = True
        self.ui()
        dpg.maximize_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()