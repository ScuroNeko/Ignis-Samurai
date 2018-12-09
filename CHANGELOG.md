**V2.0**

1. Добавлена поддержка Discord
2. Частично переписано ядро. На данный момент не работают LongPoll эвенты
3. Изменены названия методов обработки сообщений

    `before_process` -> `before_msg_process`
    
    `process` -> `msg_process`
    
    `after_process` -> `after_msg_process`
   
4. Другие изменения и исправления