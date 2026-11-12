# FINAL COIL — Последний виток

Проект UE 5.8 (локальный движок 5.8.4). База: Blueprint First Person.
Открытие: FinalCoil.uproject или ./LaunchEditor.ps1.
Если общий кэш Unreal недоступен: ./LaunchEditor.ps1 -MemoryCache.

Стартовая карта: /Game/FirstPerson/Lvl_FirstPerson.
Управление шаблона: WASD, мышь, пробел.
Оригинальный контент шаблона оставлен на своих путях для сохранения ссылок.
Игровой контент добавлять в /Game/FinalCoil: Core, Player, Interaction,
Items, Vehicles, World, UI, Audio, Art, Maps, Developers.

Включены ModelContextProtocol, AllToolsets, PythonScriptPlugin,
EditorScriptingUtilities. MCP запускается автоматически на стандартном порту 8000.
Подключение инструментов в Codex требует активного соединения Unreal MCP;
наличие плагинов само по себе не подтверждает доступность соединения.

Config и Content хранить в Git. Saved, Intermediate, Binaries и кэш исключены.
C++ модуль пока не создан. Игровые системы из GDD ещё не реализованы.
Проверка Blueprint: Scripts/validate_project.py через Unreal Python commandlet.

Текущий стартовый уровень: /Game/FinalCoil/Maps/L_Berezovka_Region_Blockout.
Общий черновой регион 7 км² описан в BEREZOVKA_REGION.md.
Предыдущий локальный план села сохранён в L_Berezovka_Blockout.

Актуальная карта с дорогами: /Game/FinalCoil/Maps/L_Berezovka_Region_Roads.
Она назначена стартовой. Подробности: BEREZOVKA_ROADS.md.

Актуальная карта с усадьбами: /Game/FinalCoil/Maps/L_Berezovka_Homesteads.
Она назначена стартовой. Разметка описана в BEREZOVKA_HOMESTEADS.md.

Актуальный уровень: /Game/FinalCoil/Maps/L_Berezovka_Shop_Bor.
Магазин, часовня и вход в бор описаны в SHOP_BOR.md.

Текущий стартовый уровень: /Game/FinalCoil/Maps/L_Berezovka_Terrain.
Содержит черновой рельеф с коллизией, согласованные дороги и площадки.
Результаты Play и изображения: TERRAIN_REVIEW.md и Review/Terrain.
