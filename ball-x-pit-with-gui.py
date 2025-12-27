import ctypes.wintypes, time, re, colorama, cyminhook, transparent_window, pylocalmem
import dearpygui.dearpygui as dpg
from typing import Callable, TypeVar, Protocol, Any, ParamSpec
from pymousekey import VK_KEYS
from unity_helper import Il2cpp

# Wait 2 seconds for methods to be initialized
time.sleep(2)
colorama.just_fix_windows_console()

class MODULEINFO(ctypes.Structure):
    _fields_ = [("lpBaseOfDll", ctypes.c_void_p),
                ("SizeOfImage", ctypes.c_ulong),
                ("EntryPoint", ctypes.c_void_p)]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", ctypes.wintypes.HWND),
        ("message", ctypes.wintypes.UINT),
        ("wParam", ctypes.wintypes.WPARAM),
        ("lParam", ctypes.wintypes.LPARAM),
        ("time", ctypes.wintypes.DWORD),
        ("pt_x", ctypes.c_long),
        ("pt_y", ctypes.c_long),
    ]

CURRENT_PROCESS = ctypes.windll.kernel32.GetCurrentProcess()
P = ParamSpec("P")
R = TypeVar("R")
__ACTIVE_HOOKS = []
TOGGLE_AI = False
TOGGLE_AUTO_UPGRADE = False
TOGGLE_INSTA_KILL = False
TOGGLE_MULTIPLY_DAMAGE = False
TOGGLE_GODMODE = False
TOGGLE_UNLIMITED_REROLLS = False
TOGGLE_UNLIMITED_BANISHES = False
TOGGLE_MULTIPLY_XP = False
TOGGLE_ALLOW_FASTER_SPEEDS = False
TOGGLE_AUTO_RESTART = False
TOGGLE_NO_RESOURCE_COST = False
TOGGLE_ALWAYS_ALLOW_HARVEST = False
TOGGLE_ALL_PICKUPS = False
TOGGLE_MULTIPLY_SPEED = False
TOGGLE_SHOOT_ALL_BALLS = False

LOCAL_PROCESS = pylocalmem.Process()

GAME_HWND = False
multiply_damage = 1
multiply_xp = 1
multiply_speed = 1
speedhack_speed = 10.0


SPEEDHACK_HOTKEY = VK_KEYS['f4']
HIDE_MENU_HOTKEY = VK_KEYS['\\']
CLOSE_MENU_HOTKEY = VK_KEYS['end']
RESTART_RUN_HOTKEY = VK_KEYS['r']

TICK_RATE = 1 / 60
WM_KEYDOWN = 0x0100


BaseCheatType = {
    "kAddResources": 0,
    "kPassFiveMinutes": 1,
    "kGainAllBlueprints": 2,
    "kBuildAllScaffolds": 3,
    "kSkipAllTutorials": 4,
    "kUnlockAllCharacters": 5,
    "kResetCharacterProgress": 6,
    "kAddHarvestUpgrade": 7,
    "kResetLevelProgress": 8,
    "kUnlockAllLevels": 9,
    "kResetElevator": 10,
    "kClearExpansion": 11,
    "kClearResources": 12,
    "kUnlockAllEncyclopediaEntries": 13,
    "kResetAllBlueprints": 14,
    "kToggleTest": 15,
    "kCreateEndGameBase": 16,
    "kClearAchievements": 17,
    "kResetBaseTutorials": 18,
    "kForceSwitchButtonPrompts": 19,
    "kCompletePlaythrough": 20,
}


CharType = {
    "kAll": 100,
    "kDefault": 0,
    "kRecaller": 1,
    "kItchyFinger": 2,
    "kX2": 3,
    "kX1": 4,
    "kCogitator": 5,
    "kTactician": 6,
    "kSpendthrift": 7,
    "kEmbedded": 8,
    "kRadicalAI": 9,
    "kEmptyNester": 10,
    "kShade": 11,
    "kCohabitants": 12,
    "kPhysicist": 13,
    "kBrickHead": 14,
    "kSisyphus": 15,
    "kFlagellant": 16,
    "kWimp": 17,
    "kX3": 18,
    "kX4": 19,
    "kX5": 20,
    "kX6": 21,
    "kInfluencer": 22,
}


il2cpp = Il2cpp()

ctypes.windll.kernel32.GetModuleHandleW.restype = ctypes.c_void_p
ctypes.windll.psapi.GetModuleInformation.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.HMODULE, ctypes.POINTER(MODULEINFO), ctypes.wintypes.DWORD]



class HookedFunction(Protocol[P, R]):
    original: Callable[P, R]
    close: None
    def __call__(self, *args, **kwargs) -> Any: ...

def hook(sig, target) -> Callable[[Callable[P, R]], HookedFunction[P, R]]:
    def decorator(func: Callable[P, R]) -> HookedFunction[P, R]:
        if not target or type(target) == str:
            print('\033[31m' + f"Invalid target for func: {func} hook" + '\033[0m')
            return None
        h = cyminhook.MinHook(signature=sig, target=target, detour=func)
        h.enable()
        __ACTIVE_HOOKS.append(h)

        func.original = h.original
        func.close = h.close

        return func
    return decorator


def aob_scan_module(module, pattern):
    lpmodinfo = MODULEINFO()
    module_handle = ctypes.windll.kernel32.GetModuleHandleW(module)
    ctypes.windll.psapi.GetModuleInformation(CURRENT_PROCESS, ctypes.c_void_p(module_handle), ctypes.byref(lpmodinfo), ctypes.sizeof(lpmodinfo))
    
    if lpmodinfo.lpBaseOfDll:
        
        found_bytes = LOCAL_PROCESS.read_bytes(lpmodinfo.lpBaseOfDll, lpmodinfo.SizeOfImage)
        
        if found_bytes:
            match = re.search(pattern, found_bytes)
            if match:
                found_address = lpmodinfo.lpBaseOfDll + match.start()
                print(colorama.Fore.CYAN + f'Found aob match of {pattern} at address: {found_address}' + colorama.Fore.WHITE)
                
                return found_address
    print(colorama.Fore.RED + f'Unable to find aob matching {pattern}' + colorama.Fore.WHITE)
    
    return None



def key_handler(key, modifiers=None):
    if key == SPEEDHACK_HOTKEY:
        if get_timeScale() != speedhack_speed:
            set_timeScale(speedhack_speed)
        else:
            set_timeScale(1.0)
    elif key == HIDE_MENU_HOTKEY:
        if dpg.is_item_visible("mod_manager_window"):
            dpg.hide_item("mod_manager_window")
            ctypes.windll.user32.SetForegroundWindow(GAME_HWND)
        else:
            dpg.show_item("mod_manager_window")
    
    elif key == RESTART_RUN_HOTKEY:
        restart_run()
    
    elif key == CLOSE_MENU_HOTKEY:
        dpg.stop_dearpygui()


set_timeScale = ctypes.CFUNCTYPE(ctypes.POINTER(ctypes.c_void_p), ctypes.c_float)(il2cpp.find_method("UnityEngine.CoreModule.dll", "UnityEngine", "Time", "set_timeScale", actualAddress=True))
get_timeScale = ctypes.CFUNCTYPE(ctypes.c_float)(il2cpp.find_method("UnityEngine.CoreModule.dll", "UnityEngine", "Time", "get_timeScale", actualAddress=True))
GetKeyDown = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_int32)(il2cpp.find_method("UnityEngine.InputLegacyModule.dll", "UnityEngine", "Input", "GetKeyDown", actualAddress=True))
EnterEndless = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.POINTER(ctypes.wintypes.DWORD), ctypes.POINTER(ctypes.wintypes.DWORD))(il2cpp.find_method('Assembly-CSharp.dll', '', 'GameMgr', 'EnterEndless', actualAddress=True))
Die = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool, ctypes.c_void_p)(il2cpp.find_method('Assembly-CSharp.dll', '', 'GridPieceObj', 'Die', actualAddress=True))
KillPiece = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(il2cpp.find_method('Assembly-CSharp.dll', '', 'GridMgr', 'KillPiece', actualAddress=True))
DropDeathStuff = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(il2cpp.find_method('Assembly-CSharp.dll', '', 'GridPieceObj', 'DropDeathStuff', actualAddress=True))
StartPlayerPickUp = il2cpp.find_method('Assembly-CSharp.dll', '', 'PickupObj', 'StartPlayerPickUp', actualAddress=False)


@hook(ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'Player', 'IsAIActive', actualAddress=True))
def IsAIActiveHook(__this, method):
    if TOGGLE_AI:
        return True
    return IsAIActiveHook.original(__this, method)

@hook(ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'LevelUpUI', 'ShouldAutopick', actualAddress=True))
def ShouldAutopickHook(__this, method):
    if TOGGLE_AUTO_UPGRADE:
        return True
    return ShouldAutopickHook.original(__this, method)
    

@hook(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.POINTER(ctypes.wintypes.DWORD), ctypes.c_int32, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'GameMgr', '_EnterGameOver', actualAddress=True))
def EnterGameOverHook(__this, __1__state, method):
    if dpg.get_value('toggle_endless'):
        return EnterEndless(__this, method)
    return EnterGameOverHook.original(__this, __1__state, method)


@hook(ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'GridPieceObj', 'Damage', actualAddress=True))
def DamageHook(__this, amt, dt, hitType, method):
    if TOGGLE_MULTIPLY_DAMAGE:
        amt = round(amt * multiply_damage)
    elif TOGGLE_INSTA_KILL:
        KillPiece(__this, __this, method)
        return True
    
    return DamageHook.original(__this, amt, dt, hitType, method)


@hook(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int32, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'Player', 'CanBeDamaged', actualAddress=True))
def CanBeDamagedHook(__this, dmgType, method):
    if TOGGLE_GODMODE:
        return False
    return CanBeDamagedHook.original(__this, dmgType, method)


@hook(ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'BattleSaveData', 'GetNumResources', actualAddress=True))
def GetNumResourcesHook(__this, dt, method):
    if TOGGLE_UNLIMITED_REROLLS:
        LOCAL_PROCESS.write_int(__this + 0x100, 4)
    elif TOGGLE_UNLIMITED_BANISHES:
        LOCAL_PROCESS.write_int(__this + 0x6C, 4)
    return GetNumResourcesHook.original(__this, dt, method)


@hook(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_float, ctypes.c_float, ctypes.c_int32, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'PickupMgr', '_SpawnGem', actualAddress=True))
def SpawnGemHook(__this, pos, width, height, xpVal, method):
    if TOGGLE_MULTIPLY_XP:
        xpVal = round(xpVal * multiply_xp)

    return SpawnGemHook.original(__this, pos, width, height, xpVal, method)


@hook(ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'LevelData', 'IsUnlocked', actualAddress=True))
def IsUnlockedHook(__this, method):
    Unlocked = IsUnlockedHook.original(__this, method)

    if Unlocked and TOGGLE_ALLOW_FASTER_SPEEDS:
        if not LOCAL_PROCESS.read_bool(__this + 0x18):
            LOCAL_PROCESS.write_bool(__this + 0x18, True)
        

    return Unlocked


@hook(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'Player', 'MyFixedUpdate', actualAddress=True))
def MyFixedUpdateHook(__this, method):
    if TOGGLE_MULTIPLY_SPEED:
        LOCAL_PROCESS.write_float(__this + 0x60, multiply_speed)
    
    elif not LOCAL_PROCESS.read_float(__this + 0x60) == 1.0:
        LOCAL_PROCESS.write_float(__this + 0x60, 1.0)

    return MyFixedUpdateHook.original(__this, method)



@hook(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'GameMgr', 'LoseGame', actualAddress=True))
def LoseGameHook(__this, method):
    if TOGGLE_AUTO_RESTART:
        restart_run()

    return 



@hook(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'SaveMgr', 'SpendResources', actualAddress=True))
def SpendResourcesHook(__this, rt, cost, method):
    if TOGGLE_NO_RESOURCE_COST:
        return

    return SpendResourcesHook.original(__this, rt, cost, method)



@hook(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'WorldTimeMgr', 'Update', actualAddress=True))
def WorldTimeMgrHook(__this, method):
    if TOGGLE_ALWAYS_ALLOW_HARVEST:
        instance = il2cpp.read_static_field_value('Assembly-CSharp.dll', '', 'MetaSaveData', 'I')
        if instance:
            DidHarvestToday = il2cpp.read_field_value('Assembly-CSharp.dll', '', 'MetaSaveData', 'DidHarvestToday', instance)
            if DidHarvestToday:
                il2cpp.write_field_value('Assembly-CSharp.dll', '', 'MetaSaveData', 'DidHarvestToday', instance, False)
                

    return WorldTimeMgrHook.original(__this, method)



@hook(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'BallMgr', 'RunBalls', actualAddress=True))
def RunBallsHook(__this, method):
    if TOGGLE_SHOOT_ALL_BALLS:
        for i in range(500):
            RunBallsHook.original(__this, method)

    return RunBallsHook.original(__this, method)



@hook(ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p), il2cpp.find_method('Assembly-CSharp.dll', '', 'SaveMgr', 'LoadBattle', actualAddress=True))
def LoadBattleHook(__this, method):
    if TOGGLE_ALL_PICKUPS:
        auto_pickup(True)

    return LoadBattleHook.original(__this, method)


@hook(ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.POINTER(MSG)), ctypes.windll.user32.DispatchMessageW)
def HookedDispatchMessageW(lpMsg):
    normal = HookedDispatchMessageW.original(lpMsg)
    if lpMsg[0].message == WM_KEYDOWN:
        key_handler(lpMsg[0].wParam, lpMsg[0].lParam)
    return normal




def restart_run():
    instance = il2cpp.read_static_field_value('Assembly-CSharp.dll', '', 'PauseUI', 'I')
    
    if not instance:
        return
    
    method = il2cpp.find_method('Assembly-CSharp.dll', '', 'PauseUI', 'OnRestartConfirmed')

    il2cpp.invoke_method(method, instance)


def add_resource(resource_type, amount):
    instance = il2cpp.read_static_field_value('Assembly-CSharp.dll', '', 'SaveMgr', 'I')
    if not instance:
        return
    
    method = il2cpp.find_method('Assembly-CSharp.dll', '', 'SaveMgr', 'AddResources')
    
    il2cpp.invoke_method(method, instance, [resource_type, amount, True, True])


def apply_base_cheat(cheat_type):
    instance = il2cpp.read_static_field_value('Assembly-CSharp.dll', '', 'BaseCheatMgr', 'I')
    if not instance:
        return
    
    method = il2cpp.find_method('Assembly-CSharp.dll', '', 'BaseCheatMgr', 'ApplyCheat')
    
    il2cpp.invoke_method(method, instance, [cheat_type])


def unlock_character(char_type):
    instance = il2cpp.read_static_field_value('Assembly-CSharp.dll', '', 'SaveMgr', 'I')
    if not instance:
        return
    
    method = il2cpp.find_method('Assembly-CSharp.dll', '', 'SaveMgr', 'UnlockChar')
    if char_type == 100:
        for i in CharType:
            if not i == 100:
                il2cpp.invoke_method(method, instance, CharType[i])
                return
    
    il2cpp.invoke_method(method, instance, [CharType[char_type]])



def toggle_enemy_spawns(isPaused):
    instance = il2cpp.read_static_field_value('Assembly-CSharp.dll', '', 'GridMgr', 'I')
    if not instance:
        return
    
    method = il2cpp.find_method('Assembly-CSharp.dll', '', 'GridMgr', 'SetSpawningPaused')

    
    il2cpp.invoke_method(method, instance, [isPaused])



def auto_pickup(state):
    instance = il2cpp.read_static_field_value('Assembly-CSharp.dll', '', 'PickupMgr', 'I')
    if not instance:
        return
    
    method = il2cpp.find_method('Assembly-CSharp.dll', '', 'PickupMgr', 'PickUpAllPickupsAboveY')

    if state:
        value = -999999.0
    else:
        value = 999999.0
    il2cpp.invoke_method(method, instance, [value])


def section_header(text):
    dpg.add_text(text)
    dpg.bind_item_theme(dpg.last_item(), "glow_header_theme")
    dpg.add_spacer(height=4)


def switch_tab(sender, app_data, tab_name):
    for t in ["tab_gameplay", "tab_cheats", "tab_multipliers", "tab_settings", "tab_misc"]:
        dpg.configure_item(t, show=False)
        
    dpg.configure_item(tab_name, show=True)


def gui():
    with dpg.theme(tag="global_cosmic_theme"):
        with dpg.theme_component(dpg.mvAll):

            SPACE_DARK = (12, 14, 22, 240)
            SPACE_PANEL = (20, 22, 40, 240)
            PURPLE_GLOW = (120, 95, 220, 200)
            BLUE_GLOW = (140, 170, 255, 200)

            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (12, 14, 22, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SPACE_PANEL)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, SPACE_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (120, 95, 220, 150))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, (120, 95, 220, 150))

            dpg.add_theme_color(dpg.mvThemeCol_Button, (35, 35, 55, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (50, 50, 80, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (65, 65, 100, 255))

            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 30, 50, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (45, 45, 70, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (55, 55, 90, 255))

            dpg.add_theme_color(dpg.mvThemeCol_Border, (60, 60, 120, 160))
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 14)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 12)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 8)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 12)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 12)
            dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 16)


        with dpg.theme_component(dpg.mvSliderInt):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (255, 255, 255, 255))

        with dpg.theme_component(dpg.mvProgressBar):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (25, 25, 45, 255))
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, (PURPLE_GLOW))

        
        with dpg.theme_component(dpg.mvCombo):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 30, 50, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (45, 45, 70, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (55, 55, 90, 255))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (BLUE_GLOW))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (190, 210, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, (35, 35, 55, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (50, 50, 80, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (65, 65, 100, 255))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 12)
            dpg.add_theme_style(dpg.mvComboHeight_Regular, 130)
            dpg.add_theme_style(dpg.mvComboHeight_Small, 130)
            dpg.add_theme_style(dpg.mvComboHeight_Large, 130)
            dpg.add_theme_style(dpg.mvComboHeight_Largest, 130)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 4)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (15, 17, 35, 200))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (10, 12, 30, 200))
        
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 12)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 6)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (30, 30, 50, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (50, 50, 90, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (70, 70, 130, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Text, (200, 180, 255))

        with dpg.theme_component(dpg.mvSliderFloat):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (255, 255, 255, 255))
            
        with dpg.theme_component(dpg.mvWindowAppItem):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)
            
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8)

    with dpg.theme(tag="glow_header_theme"):
        with dpg.theme_component(dpg.mvText):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (180, 160, 255, 255))
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 6, 4)

    with dpg.font_registry():
        default_font = dpg.add_font("C:\\Windows\\Fonts\\arial.ttf", 14)

    with dpg.window(label='Ball-x-pit mod manager',tag='mod_manager_window',width=600,height=340,pos=(ctypes.windll.user32.GetSystemMetrics(0)/2 - 300,ctypes.windll.user32.GetSystemMetrics(1)/2 - 170), no_title_bar=True):
        with dpg.group(horizontal=True):

            with dpg.child_window(width=100, height=-1, no_scrollbar=True):

                btn_gp = dpg.add_button(label="Gameplay", width=-1, height=45, callback=switch_tab, user_data="tab_gameplay")
                btn_ch = dpg.add_button(label="Cheats", width=-1, height=45, callback=switch_tab, user_data="tab_cheats")
                btn_mp = dpg.add_button(label="Multipliers", width=-1, height=45, callback=switch_tab, user_data="tab_multipliers")
                btn_misc = dpg.add_button(label="Misc", width=-1, height=45, callback=switch_tab, user_data="tab_misc")
                btn_settings = dpg.add_button(label="Settings", width=-1, height=45, callback=switch_tab, user_data="tab_settings")

                with dpg.tooltip(btn_gp, delay=0.2):
                    dpg.add_text("Gameplay automation settings")
                with dpg.tooltip(btn_ch, delay=0.2):
                    dpg.add_text("Cheat settings")
                with dpg.tooltip(btn_mp, delay=0.2):
                    dpg.add_text("Multiplier settings")
                with dpg.tooltip(btn_misc, delay=0.2):
                    dpg.add_text("Random stuff")
                with dpg.tooltip(btn_settings, delay=0.2):
                    dpg.add_text("Some useful settings")

            
            with dpg.child_window(width=-1, height=-1, no_scrollbar=True):

                
                with dpg.group(tag="tab_gameplay", show=True):
                    section_header("Gameplay Automation")

                    dpg.add_checkbox(label="Auto play the game", tag="auto_play", callback=lambda: globals().update(TOGGLE_AI=not TOGGLE_AI))

                    dpg.add_checkbox(label="Auto pick upgrades", tag="auto_upgrades", callback=lambda: globals().update(TOGGLE_AUTO_UPGRADE=not TOGGLE_AUTO_UPGRADE))

                    dpg.add_checkbox(label="Enable endless mode", tag="toggle_endless")

                    dpg.add_checkbox(label="Auto pick up drops", tag="all_pickups", callback=lambda item, value: (globals().update(TOGGLE_ALL_PICKUPS=not TOGGLE_ALL_PICKUPS), auto_pickup(value)))

                    dpg.add_checkbox(label="Auto restart game", tag="auto_restart", callback=lambda: globals().update(TOGGLE_AUTO_RESTART=not TOGGLE_AUTO_RESTART))

                
                with dpg.group(tag="tab_cheats", show=False):
                    section_header("Cheats")
                    
                    
                    with dpg.group(horizontal=True):
                        dpg.add_text(default_value='Resource type')
                        dpg.add_combo(items=['Gold', 'Wheat', 'Wood', 'Stone'], default_value='Gold', width=75, tag='resource_type')
                        dpg.add_button(label='Add resource', callback=lambda: add_resource({'Gold': 0, 'Wheat': 1, 'Wood': 2, 'Stone': 3}[dpg.get_value('resource_type')], dpg.get_value('add_resource_value')))
                        dpg.add_input_int(default_value=100, min_value=1, max_value=2147483647, tag='add_resource_value', width=150)

                    dpg.add_checkbox(label="Instant kill", tag="insta_kill", callback=lambda: globals().update(TOGGLE_INSTA_KILL=not TOGGLE_INSTA_KILL))

                    dpg.add_checkbox(label="Godmode", tag="godmode", callback=lambda: globals().update(TOGGLE_GODMODE=not TOGGLE_GODMODE))

                    dpg.add_checkbox(label="Unlimited level up refreshes", tag="unlimited_rerolls", callback=lambda: globals().update(TOGGLE_UNLIMITED_REROLLS=not TOGGLE_UNLIMITED_REROLLS))

                    dpg.add_checkbox(label="Unlimited level up banishes", tag="unlimited_banishes", callback=lambda: globals().update(TOGGLE_UNLIMITED_BANISHES=not TOGGLE_UNLIMITED_BANISHES))

                    dpg.add_checkbox(label="Allow speeds faster than normal before map completion", tag="faster_speeds", callback=lambda: globals().update(TOGGLE_ALLOW_FASTER_SPEEDS=not TOGGLE_ALLOW_FASTER_SPEEDS))

                    dpg.add_checkbox(label="No resources spent", tag="no_spent_resources", callback=lambda: globals().update(TOGGLE_NO_RESOURCE_COST=not TOGGLE_NO_RESOURCE_COST))

                    dpg.add_checkbox(label="Always allow harvest", tag="always_allow_harvest", callback=lambda: globals().update(TOGGLE_ALWAYS_ALLOW_HARVEST=not TOGGLE_ALWAYS_ALLOW_HARVEST))

                    dpg.add_checkbox(label="Disable enemy spawns", tag="toggle_enemy_spawns", callback=lambda item, value: toggle_enemy_spawns(value))

                    dpg.add_checkbox(label="Shoot all balls at once", tag="toggle_shoot_all_balls", callback=lambda item, value: globals().update(TOGGLE_SHOOT_ALL_BALLS=not TOGGLE_SHOOT_ALL_BALLS))
                
                with dpg.group(tag="tab_multipliers", show=False):
                    section_header("Multipliers")


                    
                    dpg.add_checkbox(label="Multiply damage", tag="multiply_damage", callback=lambda: (dpg.hide_item('multiply_damage_group') if dpg.is_item_visible('multiply_damage_group') else dpg.show_item('multiply_damage_group'), globals().update(TOGGLE_MULTIPLY_DAMAGE=not TOGGLE_MULTIPLY_DAMAGE)))
                    with dpg.group(horizontal=True, show=False, tag='multiply_damage_group'):
                        dpg.add_progress_bar(indent=7, width=138, default_value=1 / 100, tag="multiply_damage_progress_bar")
                        dpg.add_slider_int(indent=1, label="", width=150, default_value=1, min_value=1, max_value=100, tag="multiply_damage_slider", callback=lambda s, v, p: (globals().update(multiply_damage = v), dpg.set_value("multiply_damage_progress_bar", v / 100)))
                    

                    dpg.add_checkbox(label="Multiply xp", tag="multiply_xp", callback=lambda: (dpg.hide_item('multiply_xp_group') if dpg.is_item_visible('multiply_xp_group') else dpg.show_item('multiply_xp_group'), globals().update(TOGGLE_MULTIPLY_XP=not TOGGLE_MULTIPLY_XP)))
                    with dpg.group(horizontal=True, show=False, tag='multiply_xp_group'):
                        dpg.add_progress_bar(indent=7, width=138, default_value=1 / 100, tag=f"multiply_xp_progress_bar")
                        dpg.add_slider_int(indent=1, label="", width=150, default_value=1, min_value=1, max_value=100, tag="multiply_xp_slider", callback=lambda s, v, p: (globals().update(multiply_xp = v), dpg.set_value("multiply_xp_progress_bar", v / 100)))


                    dpg.add_checkbox(label="Multiply movement speed", tag="multiply_speed", callback=lambda: (dpg.hide_item('multiply_speed_group') if dpg.is_item_visible('multiply_speed_group') else dpg.show_item('multiply_speed_group'), globals().update(TOGGLE_MULTIPLY_SPEED=not TOGGLE_MULTIPLY_SPEED)))
                    with dpg.group(horizontal=True, show=False, tag='multiply_speed_group'):
                        dpg.add_progress_bar(indent=7, width=138, default_value=1 / 100, tag=f"multiply_speed_progress_bar")
                        dpg.add_slider_float(indent=1, label="", width=150, default_value=1, min_value=0, max_value=100, tag="multiply_speed_slider", callback=lambda s, v, p: (globals().update(multiply_speed = v), dpg.set_value("multiply_speed_progress_bar", v / 100)))
                    

                with dpg.group(tag='tab_misc', show=False):
                    section_header('Misc')


                with dpg.group(tag='tab_settings', show=False):
                    section_header('Settings')
                    with dpg.group(horizontal=True):
                        dpg.add_text("Speedhack hotkey")
                        dpg.add_combo(items=[i for i in VK_KEYS.keys()], default_value='f4', callback=lambda item, hotkey:globals().update({'SPEEDHACK_HOTKEY': VK_KEYS[hotkey]}), width=150)
                    dpg.add_text('Speedhack speed')
                    with dpg.group(horizontal=True):
                        dpg.add_progress_bar(indent=7, width=138, default_value=10 / 100, tag=f"speedhack_speed_progress_bar")
                        dpg.add_slider_int(indent=1, label="", width=150, default_value=10, min_value=1, max_value=100, tag="speedhack_speed_slider", callback=lambda s, v, p: (globals().update(speedhack_speed = v), dpg.set_value("speedhack_speed_progress_bar", v / 100)))
                    
                    # add_slider_with_progress('speedhack_speed', 10)
                    dpg.add_spacer(height=10)


                    with dpg.group(horizontal=True):
                        dpg.add_text("Hide menu hotkey")
                        dpg.add_combo(items=[i for i in VK_KEYS.keys()], default_value='\\', callback=lambda item, hotkey:globals().update({'HIDE_MENU_HOTKEY': VK_KEYS[hotkey]}), width=150)


                    with dpg.group(horizontal=True):
                        dpg.add_text("Close/disable menu hotkey")
                        dpg.add_combo(items=[i for i in VK_KEYS.keys()], default_value='end', callback=lambda item, hotkey:globals().update({'CLOSE_MENU_HOTKEY': VK_KEYS[hotkey]}), width=150)
                    

                    with dpg.group(horizontal=True):
                        dpg.add_text("Restart current run hotkey")
                        dpg.add_combo(items=[i for i in VK_KEYS.keys()], default_value='r', callback=lambda item, hotkey:globals().update({'RESTART_RUN_HOTKEY': VK_KEYS[hotkey]}), width=150)


    
    with dpg.tooltip(parent='auto_play', delay=0.2):
        dpg.add_text('Automatically plays the game for you')

    with dpg.tooltip(parent='auto_upgrades', delay=0.2):
        dpg.add_text('Automatically chooses all upgrades including fusions')

    with dpg.tooltip(parent='toggle_endless', delay=0.2):
        dpg.add_text('Toggles endless mode on/off')

    with dpg.tooltip(parent='auto_restart', delay=0.2):
        dpg.add_text('Automatically restarts the game when you lose (will not give rewards on loss)')

    with dpg.tooltip(parent='insta_kill', delay=0.2):
        dpg.add_text('Allows you to instakill any enemy no matter if its a boss or not')

    with dpg.tooltip(parent='godmode', delay=0.2):
        dpg.add_text('Makes you completely immune to damage')

    with dpg.tooltip(parent='unlimited_rerolls', delay=0.2):
        dpg.add_text('Allows you to infintely reroll')

    with dpg.tooltip(parent='unlimited_banishes', delay=0.2):
        dpg.add_text('Allows you to infinitely banish items')
    
    with dpg.tooltip(parent='multiply_damage', delay=0.2):
        dpg.add_text('Multiplies the damage you do to enemies')
    
    with dpg.tooltip(parent='multiply_xp', delay=0.2):
        dpg.add_text('Multiplies the amount of xp dropped by enemies')

    with dpg.tooltip(parent='multiply_speed', delay=0.2):
        dpg.add_text('Multiplies the speed at which your character moves')

    with dpg.tooltip(parent='faster_speeds', delay=0.2):
        dpg.add_text('Allows you to pick speeds faster than normal before doing your first map completion (goes up to your highest Fast+ tier completed)')

    with dpg.tooltip(parent='all_pickups', delay=0.2):
        dpg.add_text('Automatically picks up any item on the floor when it drops')

    with dpg.tooltip(parent='no_spent_resources', delay=0.2):
        dpg.add_text('Stops the game from deducting resources upon building or upgrading')

    
    dpg.bind_font(default_font)
    dpg.bind_theme("global_cosmic_theme")


def on_startup():
    global GAME_HWND
    GAME_HWND = ctypes.windll.user32.FindWindowW(None, "BALL x PIT")
    ctypes.windll.user32.SetParent(window.overlay_hwnd, GAME_HWND)


window = transparent_window.TransparentViewport(gui, on_startup=on_startup, overlay_name='Ball-x-pit mod manager', on_close=lambda: [i.close() for i in __ACTIVE_HOOKS])
window.start()