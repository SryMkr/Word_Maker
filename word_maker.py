from Engine import *


Word_Maker = MainGame(1000, 800)  # 首先展示一个屏幕,这个是主游戏界面

while Word_Maker.Main_Game_Running:  # 主程序运行
    Word_Maker.game_Loop()  # 循环，并且检测游戏事件
    Word_Maker.current_menu.display_menu()  # 展示游戏菜单
    pygame.display.update()  # 刷新游戏页面
    Word_Maker.reset_Keys()  # 重置事件响应
